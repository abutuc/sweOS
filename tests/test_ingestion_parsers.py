from app.services.ingestion_parsers import MockAIParser, OptionalLLMParser, RuleBasedParser


def test_rule_based_parser_extracts_job_post_keywords():
    parser = RuleBasedParser()
    parsed = parser.parse(
        {
            "type": "job_post",
            "title": "Senior Go Backend Engineer",
            "raw_content": "We build Go services, PostgreSQL workflows, Docker workers, and APIs.",
            "raw_json": {"company": "Example", "seniority": "senior"},
            "canonical_url": "https://example.com/jobs/1",
        }
    )

    assert parsed.parsed_type == "job_post"
    assert "Go" in parsed.parsed_json["requiredSkills"]
    assert parsed.confidence_score is not None


def test_mock_ai_parser_wraps_rule_based_output():
    parser = MockAIParser()
    parsed = parser.parse(
        {
            "type": "article",
            "title": "Async workflows",
            "raw_content": "Workers, retries, reconciliation, and audit trails.",
            "raw_json": {},
            "canonical_url": "https://example.com/a",
        }
    )

    assert parsed.model_name == "mock-llm"
    assert parsed.prompt_version == "ingestion-mock-ai-v1"
    assert parsed.summary_markdown.startswith("AI-assisted parse:")


def test_optional_llm_parser_falls_back_without_key():
    parser = OptionalLLMParser(api_key=None)
    parsed = parser.parse(
        {
            "type": "github_repository",
            "title": "ingestion-engine",
            "raw_content": "Go worker platform",
            "raw_json": {"name": "ingestion-engine"},
            "canonical_url": "https://github.com/sweos/ingestion-engine",
        }
    )

    assert parsed.model_name == "disabled-llm-fallback"
    assert parsed.prompt_version == "ingestion-optional-llm-v1"
