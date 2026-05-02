from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Protocol
from urllib.parse import urlparse


@dataclass(slots=True)
class ParsedArtifact:
    parsed_type: str
    parsed_json: dict[str, Any]
    summary_markdown: str | None
    confidence_score: float | None
    prompt_version: str | None
    model_name: str | None


class Parser(Protocol):
    def parse(self, item: dict[str, Any]) -> ParsedArtifact:
        raise NotImplementedError


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_keywords(text: str) -> list[str]:
    candidates = re.findall(r"\b(?:go|python|rust|docker|postgresql|kubernetes|react|typescript|github|llm|api)\b", text.lower())
    ordered: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


class RuleBasedParser:
    prompt_version = "ingestion-rule-based-v1"

    def parse(self, item: dict[str, Any]) -> ParsedArtifact:
        item_type = str(item.get("type") or "unknown")
        raw_content = str(item.get("raw_content") or "")
        title = str(item.get("title") or "").strip()
        raw_json = item.get("raw_json") or {}

        if item_type == "job_post":
            body = _clean_text(raw_content)
            keywords = _extract_keywords(body)
            parsed_json = {
                "title": title or raw_json.get("title") or "Untitled role",
                "company": raw_json.get("company") or raw_json.get("company_name") or None,
                "location": raw_json.get("location") or None,
                "responsibilities": re.findall(r"(?:responsibilit(?:y|ies)|what you will do):?(.+)", body, flags=re.IGNORECASE),
                "requiredSkills": [keyword.title() for keyword in keywords[:4]],
                "preferredSkills": [keyword.title() for keyword in keywords[4:6]],
                "keywords": keywords,
                "seniorityAssessment": raw_json.get("seniority") or "mid",
                "summaryMarkdown": f"Role {title or 'item'} looks centered on {', '.join(keywords[:3]) or 'general delivery'}.",
            }
            return ParsedArtifact("job_post", parsed_json, parsed_json["summaryMarkdown"], 0.84, self.prompt_version, "rule-based-parser")

        if item_type == "article":
            parsed_json = {
                "title": title or "Article",
                "sourceUrl": item.get("canonical_url"),
                "summary": _clean_text(raw_content)[:240],
                "keywords": _extract_keywords(raw_content),
            }
            return ParsedArtifact("article", parsed_json, f"Summarized article: {parsed_json['summary']}", 0.76, self.prompt_version, "rule-based-parser")

        if item_type == "github_repository":
            repo = raw_json if isinstance(raw_json, dict) else {}
            parsed_json = {
                "name": repo.get("name") or title or "repository",
                "owner": repo.get("owner") or repo.get("full_name", "").split("/")[0] or None,
                "description": repo.get("description") or _clean_text(raw_content)[:180],
                "languages": repo.get("languages") or [],
                "topics": repo.get("topics") or [],
                "stars": repo.get("stars") or 0,
                "forks": repo.get("forks") or 0,
                "readmeSummary": _clean_text(raw_content)[:200],
                "learningValue": "high" if any(topic in {"backend", "workers", "platform"} for topic in repo.get("topics") or []) else "medium",
            }
            return ParsedArtifact("github_repository", parsed_json, f"Repository {parsed_json['name']} has {len(parsed_json['languages'])} languages detected.", 0.71, self.prompt_version, "rule-based-parser")

        if item_type == "mock_transaction":
            parsed_json = {
                "provider": raw_json.get("provider") or "mock",
                "externalTxId": raw_json.get("external_tx_id") or item.get("external_id"),
                "assetSymbol": raw_json.get("asset_symbol") or "USDC",
                "amount": raw_json.get("amount") or 0,
                "status": raw_json.get("status") or "completed",
            }
            return ParsedArtifact("mock_transaction", parsed_json, "Mock transaction normalized for reconciliation.", 0.99, self.prompt_version, "mock-exchange-parser")

        if item_type == "mock_balance_snapshot":
            parsed_json = {
                "provider": raw_json.get("provider") or "mock",
                "accountRef": raw_json.get("account_ref"),
                "assetSymbol": raw_json.get("asset_symbol") or "USDC",
                "balance": raw_json.get("balance") or 0,
            }
            return ParsedArtifact("mock_balance_snapshot", parsed_json, "Balance snapshot captured for reconciliation.", 0.99, self.prompt_version, "mock-exchange-parser")

        parsed_json = {
            "text": _clean_text(raw_content),
            "sourceUrl": item.get("canonical_url"),
            "keywords": _extract_keywords(raw_content),
        }
        return ParsedArtifact(
            item_type if item_type else "unknown",
            parsed_json,
            f"Captured raw text from {item.get('canonical_url') or 'manual input'}.",
            0.5,
            self.prompt_version,
            "rule-based-parser",
        )


class MockAIParser:
    prompt_version = "ingestion-mock-ai-v1"

    def __init__(self, fallback: Parser | None = None):
        self._fallback = fallback or RuleBasedParser()

    def parse(self, item: dict[str, Any]) -> ParsedArtifact:
        parsed = self._fallback.parse(item)
        parsed.summary_markdown = f"AI-assisted parse: {parsed.summary_markdown or 'structured output produced.'}"
        parsed.confidence_score = min(0.97, (parsed.confidence_score or 0.75) + 0.08)
        parsed.prompt_version = self.prompt_version
        parsed.model_name = "mock-llm"
        return parsed


class OptionalLLMParser:
    prompt_version = "ingestion-optional-llm-v1"

    def __init__(self, api_key: str | None = None, fallback: Parser | None = None):
        self.api_key = api_key
        self._fallback = fallback or RuleBasedParser()

    def parse(self, item: dict[str, Any]) -> ParsedArtifact:
        if not self.api_key:
            parsed = self._fallback.parse(item)
            parsed.prompt_version = self.prompt_version
            parsed.model_name = "disabled-llm-fallback"
            return parsed

        parsed = self._fallback.parse(item)
        payload = json.dumps(parsed.parsed_json)
        parsed.summary_markdown = f"LLM-ready structured payload length: {len(payload)} characters."
        parsed.confidence_score = 0.9
        parsed.prompt_version = self.prompt_version
        parsed.model_name = "external-llm"
        return parsed


def parse_source_url(url: str | None) -> str | None:
    if not url:
        return None

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
