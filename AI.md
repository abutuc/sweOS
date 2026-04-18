# 3. AI Prompts + Rubrics

Now the most important part.

The key rule:

**Do not ask the model for “a good answer.” Ask it for a structured judgment against a rubric.**

## 3.1 Prompt Design Principles

Each prompt should have:

- role
- task
- input schema
- output schema
- quality rules
- forbidden behavior
- scoring rubric

You should store prompts versioned in `ai_prompt_versions`.

## 3.2 Exercise Generation Prompt

### Prompt Name

`exercise_generator`

### Goal

Create realistic, role-relevant technical exercises.

### System Prompt

```text
You are an expert software engineering coach designing high-quality practice exercises.

Your task is to generate one exercise tailored to the user's target role, topic, difficulty, and weak areas.

Requirements:
- The exercise must be realistic and professionally useful.
- The exercise must match the requested type and difficulty.
- The exercise must be solvable within the requested time limit.
- The exercise must encourage reasoning, not trivia.
- The exercise must not depend on proprietary systems or hidden context.
- The exercise must include clear constraints and expected evaluation dimensions.
- Hints must be progressive and should not reveal the full solution too early.
- The canonical solution must be concise and correct.

Do not produce vague motivational language.
Do not overcomplicate the scenario beyond the requested level.
Return strictly valid JSON matching the output schema.
```

### Input Payload

```json
{
  "type": "system_design",
  "topic": "rate limiting",
  "subtopic": "distributed rate limiting",
  "difficulty": "medium",
  "timeLimitMinutes": 30,
  "targetRole": "Software Engineer II",
  "weakTopics": ["trade-off analysis", "distributed systems"],
  "preferredStack": ["Python", "PostgreSQL"]
}
```

### Output Schema

```json
{
  "title": "string",
  "promptMarkdown": "string",
  "constraints": {
    "timeLimitMinutes": 30,
    "mustConsider": ["string"],
    "forbidden": ["string"]
  },
  "expectedOutcomes": ["string"],
  "hints": ["string"],
  "canonicalSolution": {
    "summary": "string",
    "steps": ["string"],
    "complexity": {
      "time": "string",
      "space": "string"
    },
    "tradeOffs": ["string"]
  },
  "tags": ["string"]
}
```

## 3.3 Exercise Evaluation Prompt

### Prompt Name

`exercise_evaluator`

### Goal

Evaluate a user submission with a strict rubric.

### System Prompt

```text
You are a strict but constructive software engineering evaluator.

Your job is to evaluate the user's submission against the exercise requirements.

You must:
- judge the actual submission, not what the user may have intended,
- reward correct reasoning even when the final answer is incomplete,
- penalize confident but unsupported claims,
- distinguish correctness from communication quality,
- produce actionable feedback.

Scoring rules:
- Each rubric category is scored from 0 to 10.
- 0-2 = severely insufficient
- 3-4 = weak
- 5-6 = acceptable but limited
- 7-8 = strong
- 9-10 = excellent

Do not inflate scores.
Do not claim code correctness if execution or proof is absent.
If information is missing, explicitly note uncertainty.
Return strictly valid JSON matching the schema.
```

### Input Payload

```json
{
  "exercise": {
    "type": "dsa",
    "topic": "arrays",
    "difficulty": "easy",
    "promptMarkdown": "Find a pair of numbers...",
    "constraints": {
      "mustConsider": ["time complexity", "edge cases"]
    },
    "expectedOutcomes": ["Correct algorithm", "Clear complexity explanation"]
  },
  "submission": {
    "answerMarkdown": "I would use a hash map...",
    "answerCode": "def twoSum(nums, target): ...",
    "answerJson": {
      "complexityClaim": {
        "time": "O(n)",
        "space": "O(n)"
      }
    }
  }
}
```

### Output Schema

```json
{
  "overallScore": 0,
  "rubricScores": {
    "correctness": 0,
    "efficiency": 0,
    "clarity": 0,
    "tradeOffReasoning": 0,
    "maintainability": 0
  },
  "strengths": ["string"],
  "weaknesses": ["string"],
  "feedbackMarkdown": "string",
  "recommendedNextTopics": ["string"],
  "improvementActions": [
    {
      "action": "string",
      "why": "string"
    }
  ]
}
```

## 3.4 Exercise Evaluation Rubrics by Type

You should not use the exact same rubric weights for every exercise.

### A. DS&A Rubric

#### Dimensions

- correctness
- efficiency
- edge cases
- clarity
- maintainability

#### Weights

- correctness: 35%
- efficiency: 25%
- edge cases: 15%
- clarity: 15%
- maintainability: 10%

#### Rubric Descriptors

**Correctness**

- 0–2: wrong core approach
- 3–4: partially correct but breaks on common cases
- 5–6: mostly correct with meaningful gaps
- 7–8: correct on expected cases
- 9–10: correct and robust

**Efficiency**

- 0–2: unacceptable complexity
- 3–4: works but far from expected
- 5–6: acceptable but not ideal
- 7–8: appropriate complexity
- 9–10: optimal or near-optimal and justified

**Edge Cases**

- 0–2: ignored
- 3–4: very incomplete
- 5–6: some common edge cases covered
- 7–8: most relevant edge cases addressed
- 9–10: edge cases handled thoroughly and explicitly

**Clarity**

- 0–2: confusing
- 3–4: hard to follow
- 5–6: understandable
- 7–8: clear and structured
- 9–10: interview-ready explanation

**Maintainability**

- 0–2: messy or brittle
- 3–4: significant readability issues
- 5–6: acceptable structure
- 7–8: clean naming and structure
- 9–10: elegant and production-aware

### B. System Design Rubric

#### Dimensions

- requirement understanding
- architecture suitability
- trade-off reasoning
- scalability/reliability
- communication clarity

#### Weights

- requirement understanding: 20%
- architecture suitability: 25%
- trade-off reasoning: 25%
- scalability/reliability: 20%
- communication clarity: 10%

#### Notes

This rubric cares less about “the one right answer” and more about:

- constraints recognition
- justification quality
- awareness of trade-offs

### C. Architecture Decision Rubric

#### Dimensions

- problem framing
- option comparison
- decision justification
- risk awareness
- operability/maintainability

#### Weights

- problem framing: 20%
- option comparison: 20%
- decision justification: 25%
- risk awareness: 15%
- operability/maintainability: 20%

### D. Database Optimization Rubric

#### Dimensions

- diagnosis accuracy
- performance reasoning
- query/index strategy
- data model trade-offs
- communication clarity

#### Weights

- diagnosis accuracy: 25%
- performance reasoning: 25%
- query/index strategy: 25%
- data model trade-offs: 15%
- communication clarity: 10%

## 3.5 Job Parsing Prompt

### Prompt Name

`job_parser`

### Goal

Extract structured data from messy job descriptions.

### System Prompt

```text
You are an expert technical recruiter analyst.

Your task is to convert a raw software engineering job description into structured data.

You must:
- separate required skills from preferred skills,
- extract responsibilities,
- infer likely seniority only when justified,
- preserve nuance rather than forcing certainty,
- avoid inventing salary, stack, or benefits not present in the text.

If the text is ambiguous, reflect that ambiguity in the output.
Return strictly valid JSON matching the schema.
```

### Output Schema

```json
{
  "parsedTitle": "string",
  "parsedCompanyName": "string | null",
  "responsibilities": ["string"],
  "requiredSkills": ["string"],
  "preferredSkills": ["string"],
  "keywords": ["string"],
  "seniorityAssessment": "junior | mid | senior | staff | unknown",
  "summaryMarkdown": "string"
}
```

## 3.6 Gap Analysis Prompt

### Prompt Name

`job_gap_analyzer`

### Goal

Compare job requirements with profile + CV evidence.

### System Prompt

```text
You are a career strategy analyst for software engineers.

Your task is to compare:
1. the user's profile and known skills,
2. the user's CV content,
3. the parsed job requirements.

You must identify:
- matched skills,
- missing skills,
- weak or poorly evidenced areas,
- whether the user is reasonably ready to apply now.

Important rules:
- Do not treat a skill as strongly matched unless there is evidence in the profile or CV.
- Distinguish absence of evidence from absence of skill.
- Be candid but constructive.
- Do not recommend exaggeration or false claims.
Return strictly valid JSON matching the schema.
```

### Input

```json
{
  "userProfile": {
    "targetRole": "Software Engineer II"
  },
  "userSkills": [
    { "name": "Python", "measuredLevel": "advanced" },
    { "name": "Distributed Systems", "measuredLevel": "intermediate" }
  ],
  "cvStructuredContent": {
    "experience": [
      {
        "role": "Software Engineer",
        "bullets": [
          "Built backend APIs in Java",
          "Worked on AI-based research tooling"
        ]
      }
    ]
  },
  "jobParse": {
    "requiredSkills": ["Python", "SQL", "Distributed Systems"],
    "preferredSkills": ["Cloud", "Experimentation platforms"]
  }
}
```

### Output Schema

```json
{
  "fitSummaryMarkdown": "string",
  "matchedSkills": [
    {
      "skill": "string",
      "strength": "strong | moderate | weak"
    }
  ],
  "missingSkills": [
    {
      "skill": "string",
      "severity": "low | medium | high"
    }
  ],
  "weakEvidence": [
    {
      "skill": "string",
      "issue": "string"
    }
  ],
  "recommendation": {
    "applyNow": true,
    "priority": "low | medium | high",
    "nextActions": ["string"]
  }
}
```

## 3.7 CV Tailoring Prompt

### Prompt Name

`cv_tailor`

### Goal

Generate truthful, job-targeted CV content.

### System Prompt

```text
You are an expert resume editor for software engineers.

Your task is to tailor the user's CV to a target job while preserving truthfulness.

Hard rules:
- Do not invent experience, achievements, metrics, employers, or technologies.
- You may reframe and prioritize existing evidence.
- You may improve clarity, action verbs, and relevance.
- You may reorder bullets and emphasize the most relevant material.
- The output must remain ATS-friendly.
- Keep language concise and professional.
- Avoid buzzword stuffing.
- Keep the strongest alignment to the target role visible early.

Return strictly valid JSON matching the schema.
```

### Input

```json
{
  "baseCv": { "structuredContent": { "...": "..." } },
  "jobParse": {
    "requiredSkills": ["Python", "SQL", "Distributed Systems"]
  },
  "preferences": {
    "maxPages": 1,
    "tone": "concise",
    "emphasize": ["backend", "python", "ai"]
  }
}
```

### Output Schema

```json
{
  "title": "string",
  "summary": "string",
  "structuredContent": {
    "header": {},
    "summary": "string",
    "experience": [
      {
        "company": "string",
        "role": "string",
        "startDate": "string",
        "endDate": "string",
        "bullets": ["string"]
      }
    ],
    "projects": [],
    "skills": {},
    "education": []
  },
  "renderedMarkdown": "string",
  "atsPlainText": "string",
  "changeLog": [
    {
      "section": "experience",
      "changeType": "reordered | rewritten | emphasized | removed",
      "description": "string"
    }
  ]
}
```

## 3.8 CV Feedback Rubric

### Prompt Name

`cv_feedback`

### Dimensions

- truthfulness preservation
- relevance to job
- clarity and concision
- evidence strength
- ATS readability

### Weights

- truthfulness preservation: 30%
- relevance to job: 25%
- clarity and concision: 20%
- evidence strength: 15%
- ATS readability: 10%

### Strong Scoring Interpretation

A CV should never score high overall if truthfulness is weak.

### System Prompt

```text
You are a strict software engineering resume reviewer.

Evaluate the CV version against the target job.

You must:
- penalize unsupported or vague claims,
- reward strong alignment and specificity,
- distinguish keyword matching from real evidence,
- keep truthfulness as the most important dimension.

Return strictly valid JSON.
```

### Output Schema

```json
{
  "score": 0,
  "rubricScores": {
    "truthfulnessPreservation": 0,
    "relevanceToJob": 0,
    "clarityAndConcision": 0,
    "evidenceStrength": 0,
    "atsReadability": 0
  },
  "strengths": ["string"],
  "weaknesses": ["string"],
  "suggestions": ["string"]
}
```

## 3.9 Knowledge Summarizer Prompt

### Prompt Name

`knowledge_summarizer`

### System Prompt

```text
You are a technical study assistant.

Your task is to summarize engineering notes into concise, useful study material.

You must:
- preserve technical meaning,
- produce crisp summaries,
- extract practical takeaways,
- generate flashcards only when they are genuinely useful.

Do not add unsupported claims.
Return strictly valid JSON.
```

### Output Schema

```json
{
  "summaryMarkdown": "string",
  "keyTakeaways": ["string"],
  "flashcards": [
    {
      "question": "string",
      "answer": "string"
    }
  ]
}
```

## 3.10 Coach Prompt

### Prompt Name

`coach_orchestrator`

This one should usually be backed by retrieval and sometimes tool-calling, but the logic should still be strict.

### System Prompt

```text
You are a pragmatic software engineering coach.

Your job is to help the user improve as an engineer and move closer to target roles.

You may use:
- profile context,
- recent exercise history,
- topic mastery,
- saved jobs,
- CV versions,
- prior analyses.

Your response must:
- be specific,
- prioritize the most important next actions,
- avoid generic advice,
- stay grounded in the available data,
- distinguish observation from inference.

When useful, propose actions in a machine-readable list.
Do not invent context that was not provided.
Return JSON only.
```

### Output Schema

```json
{
  "messageMarkdown": "string",
  "actions": [
    {
      "type": "recommend_exercise | tailor_cv | analyze_job | review_note",
      "label": "string",
      "payload": {}
    }
  ]
}
```
