# 2. API Endpoints + Request/Response Contracts

I will assume:

- REST JSON API
- `/api/v1/...`
- JWT auth
- all timestamps ISO 8601 UTC
- validation errors return `422`
- auth errors return `401`
- not found returns `404`

## 2.1 Common Envelope Style

I recommend:

### Success

```json
{
  "data": { "...": "..." },
  "meta": { "...": "..." }
}
```

### Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body",
    "details": [
      {
        "field": "difficulty",
        "message": "Must be one of easy, medium, hard"
      }
    ]
  }
}
```

## 2.2 Auth

### `POST /api/v1/auth/register`

#### Request

```json
{
  "email": "andre@example.com",
  "password": "StrongPassword123!",
  "fullName": "Andre Butuc"
}
```

#### Response

```json
{
  "data": {
    "user": {
      "id": "uuid",
      "email": "andre@example.com",
      "fullName": "Andre Butuc"
    },
    "token": "jwt-token"
  }
}
```

### `POST /api/v1/auth/login`

#### Request

```json
{
  "email": "andre@example.com",
  "password": "StrongPassword123!"
}
```

#### Response

```json
{
  "data": {
    "user": {
      "id": "uuid",
      "email": "andre@example.com",
      "fullName": "Andre Butuc"
    },
    "token": "jwt-token"
  }
}
```

## 2.3 Profile & Skills

### `GET /api/v1/profile`

#### Response

```json
{
  "data": {
    "userId": "uuid",
    "headline": "Software Engineer",
    "bio": "Backend and AI-focused engineer",
    "yearsExperience": 2,
    "currentRole": "Software Engineer",
    "targetRole": "Software Engineer II",
    "targetSeniority": "mid",
    "preferredLocations": ["Portugal", "Remote EU"],
    "preferredWorkModes": ["remote", "hybrid"],
    "salaryExpectationMin": 30000,
    "salaryExpectationMax": 45000,
    "summary": "..."
  }
}
```

### `PUT /api/v1/profile`

#### Request

```json
{
  "headline": "Software Engineer",
  "bio": "Backend and AI-focused engineer",
  "yearsExperience": 2,
  "currentRole": "Software Engineer",
  "targetRole": "Software Engineer II",
  "targetSeniority": "mid",
  "preferredLocations": ["Portugal", "Remote EU"],
  "preferredWorkModes": ["remote", "hybrid"],
  "salaryExpectationMin": 30000,
  "salaryExpectationMax": 45000,
  "summary": "..."
}
```

#### Response

```json
{
  "data": {
    "updated": true
  }
}
```

### `GET /api/v1/skills/catalog`

#### Query Params

- `category`
- `search`

#### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "slug": "postgresql",
      "name": "PostgreSQL",
      "category": "database",
      "description": "Relational database and ecosystem"
    }
  ]
}
```

### `GET /api/v1/skills/me`

#### Response

```json
{
  "data": [
    {
      "skillId": "uuid",
      "skillSlug": "python",
      "skillName": "Python",
      "category": "language",
      "selfAssessedLevel": "advanced",
      "measuredLevel": "intermediate",
      "confidenceScore": 0.74,
      "evidenceCount": 8,
      "lastEvaluatedAt": "2026-04-18T11:00:00Z"
    }
  ]
}
```

### `PUT /api/v1/skills/me`

Bulk upsert.

#### Request

```json
{
  "skills": [
    {
      "skillId": "uuid",
      "selfAssessedLevel": "advanced"
    },
    {
      "skillId": "uuid2",
      "selfAssessedLevel": "intermediate"
    }
  ]
}
```

#### Response

```json
{
  "data": {
    "updatedCount": 2
  }
}
```

## 2.4 Exercises

### `POST /api/v1/exercises/generate`

Generates a new exercise and persists it.

#### Request

```json
{
  "type": "system_design",
  "topic": "scalability",
  "subtopic": "rate limiting",
  "difficulty": "medium",
  "timeLimitMinutes": 30,
  "includeHints": true,
  "context": {
    "targetRole": "Software Engineer II",
    "weakTopics": ["distributed systems", "trade-off analysis"]
  }
}
```

#### Response

```json
{
  "data": {
    "exercise": {
      "id": "uuid",
      "type": "system_design",
      "topic": "scalability",
      "subtopic": "rate limiting",
      "difficulty": "medium",
      "title": "Design a Rate Limiter for a Public API",
      "promptMarkdown": "Design a rate limiter ...",
      "constraints": {
        "timeLimitMinutes": 30,
        "mustConsider": ["throughput", "fairness", "burst traffic"]
      },
      "expectedOutcomes": [
        "Explains trade-offs between token bucket and sliding window",
        "Addresses distributed deployment concerns"
      ],
      "hints": [
        "Think about per-user vs global limits",
        "Consider storage consistency requirements"
      ],
      "tags": ["scalability", "system-design", "rate-limiting"]
    }
  }
}
```

### `GET /api/v1/exercises`

#### Query Params

- `type`
- `topic`
- `difficulty`
- `limit`
- `offset`

#### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "type": "dsa",
      "topic": "arrays",
      "difficulty": "easy",
      "title": "Two Sum Variant",
      "createdAt": "2026-04-18T10:00:00Z"
    }
  ],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 42
  }
}
```

### `GET /api/v1/exercises/{exerciseId}`

#### Response

```json
{
  "data": {
    "id": "uuid",
    "type": "dsa",
    "topic": "arrays",
    "subtopic": "two-pointers",
    "difficulty": "easy",
    "title": "Two Sum Variant",
    "promptMarkdown": "...",
    "constraints": {
      "timeLimitMinutes": 20
    },
    "expectedOutcomes": ["Handles edge cases"],
    "hints": ["Sort before searching"],
    "tags": ["arrays", "hashmap"]
  }
}
```

### `POST /api/v1/exercises/{exerciseId}/attempts`

Create draft or direct submission.

#### Request

```json
{
  "answerMarkdown": "My reasoning is ...",
  "answerCode": "def solve(nums): ...",
  "answerSql": null,
  "answerJson": {
    "complexityClaim": {
      "time": "O(n)",
      "space": "O(n)"
    }
  },
  "submit": true
}
```

#### Response

```json
{
  "data": {
    "attempt": {
      "id": "uuid",
      "exerciseId": "uuid",
      "status": "submitted",
      "submittedAt": "2026-04-18T11:30:00Z"
    }
  }
}
```

### `POST /api/v1/exercise-attempts/{attemptId}/evaluate`

#### Request

```json
{
  "evaluationMode": "standard"
}
```

#### Response

```json
{
  "data": {
    "evaluation": {
      "id": "uuid",
      "attemptId": "uuid",
      "overallScore": 7.2,
      "rubricScores": {
        "correctness": 8,
        "efficiency": 7,
        "clarity": 8,
        "tradeOffReasoning": 6,
        "maintainability": 7
      },
      "strengths": ["Correct main approach", "Clear explanation"],
      "weaknesses": [
        "Did not discuss edge cases thoroughly",
        "Complexity explanation was incomplete"
      ],
      "feedbackMarkdown": "You chose a sound approach ...",
      "recommendedNextTopics": [
        "edge case analysis",
        "complexity communication"
      ],
      "improvementActions": [
        {
          "action": "Rewrite explanation section",
          "why": "Improve interview clarity"
        }
      ]
    }
  }
}
```

### `GET /api/v1/exercise-attempts/{attemptId}`

#### Response

```json
{
  "data": {
    "id": "uuid",
    "exerciseId": "uuid",
    "status": "evaluated",
    "answerMarkdown": "...",
    "answerCode": "...",
    "submittedAt": "...",
    "evaluation": {
      "overallScore": 7.2,
      "rubricScores": {
        "correctness": 8,
        "efficiency": 7,
        "clarity": 8,
        "tradeOffReasoning": 6,
        "maintainability": 7
      }
    }
  }
}
```

## 2.5 Analytics

### `GET /api/v1/analytics/dashboard`

#### Response

```json
{
  "data": {
    "summary": {
      "totalExercisesCompleted": 37,
      "averageScore": 7.1,
      "streakDays": 5
    },
    "weakTopics": [
      {
        "topic": "distributed systems",
        "subtopic": "consistency",
        "masteryScore": 4.1
      }
    ],
    "strongTopics": [
      {
        "topic": "python",
        "subtopic": "data structures",
        "masteryScore": 8.6
      }
    ],
    "recentActivity": [
      {
        "type": "exercise_evaluated",
        "entityId": "uuid",
        "title": "Design a Rate Limiter",
        "createdAt": "2026-04-18T11:30:00Z"
      }
    ]
  }
}
```

### `GET /api/v1/analytics/topic-mastery`

#### Query Params

- `topic`
- `limit`

#### Response

```json
{
  "data": [
    {
      "topic": "system design",
      "subtopic": "rate limiting",
      "masteryScore": 6.8,
      "confidenceScore": 0.64,
      "attemptsCount": 3,
      "lastPracticedAt": "2026-04-18T11:30:00Z"
    }
  ]
}
```

## 2.6 Jobs

### `POST /api/v1/jobs`

Manual job save.

#### Request

```json
{
  "title": "Software Engineer II - Data Platform",
  "companyName": "Tripadvisor",
  "sourceUrl": "https://...",
  "rawDescription": "About the team ...",
  "location": "Portugal",
  "workMode": "remote"
}
```

#### Response

```json
{
  "data": {
    "job": {
      "id": "uuid",
      "title": "Software Engineer II - Data Platform",
      "companyName": "Tripadvisor"
    }
  }
}
```

### `POST /api/v1/jobs/{jobId}/parse`

#### Request

```json
{}
```

#### Response

```json
{
  "data": {
    "parse": {
      "id": "uuid",
      "parsedTitle": "Software Engineer II - Data Platform",
      "responsibilities": ["Build and maintain data platform services"],
      "requiredSkills": ["Python", "SQL", "Distributed systems"],
      "preferredSkills": ["Cloud platforms"],
      "keywords": ["experimentation", "data platform", "scalability"],
      "seniorityAssessment": "mid",
      "summaryMarkdown": "This role emphasizes ..."
    }
  }
}
```

### `GET /api/v1/jobs`

#### Query Params

- `status`
- `search`
- `limit`
- `offset`

#### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Software Engineer II - Data Platform",
      "companyName": "Tripadvisor",
      "location": "Portugal",
      "status": "saved",
      "matchScore": 7.8
    }
  ],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 8
  }
}
```

### `POST /api/v1/jobs/{jobId}/save`

Creates `user_jobs`.

#### Request

```json
{
  "status": "saved",
  "notes": "Interesting role, strong data angle"
}
```

#### Response

```json
{
  "data": {
    "userJobId": "uuid",
    "status": "saved"
  }
}
```

### `POST /api/v1/user-jobs/{userJobId}/gap-analysis`

#### Request

```json
{}
```

#### Response

```json
{
  "data": {
    "analysis": {
      "id": "uuid",
      "fitSummaryMarkdown": "You are a moderate match ...",
      "matchedSkills": [
        {
          "skill": "Python",
          "strength": "strong"
        }
      ],
      "missingSkills": [
        {
          "skill": "Large-scale data platform design",
          "severity": "medium"
        }
      ],
      "weakEvidence": [
        {
          "skill": "Distributed systems",
          "issue": "Present in profile, but weak evidence in CV"
        }
      ],
      "recommendation": {
        "applyNow": true,
        "priority": "high",
        "nextActions": [
          "Tailor CV toward data workflows",
          "Prepare examples around platform thinking"
        ]
      }
    }
  }
}
```

## 2.7 CV / Resume

### `POST /api/v1/cvs`

Create CV document.

#### Request

```json
{
  "name": "Base CV",
  "description": "Main professional CV"
}
```

#### Response

```json
{
  "data": {
    "cvDocumentId": "uuid"
  }
}
```

### `POST /api/v1/cvs/{cvDocumentId}/versions`

Upload or create a structured base version.

#### Request

```json
{
  "status": "base",
  "title": "Base CV - April 2026",
  "structuredContent": {
    "header": {
      "fullName": "Andre Butuc",
      "email": "andre@example.com",
      "location": "Portugal"
    },
    "summary": "Software Engineer with experience in Java, Python ...",
    "experience": [
      {
        "company": "Company X",
        "role": "Software Engineer",
        "startDate": "2024-01",
        "endDate": "2025-12",
        "bullets": ["Built backend services...", "Improved performance..."]
      }
    ],
    "projects": [],
    "skills": {
      "languages": ["Java", "Python"],
      "databases": ["PostgreSQL"]
    },
    "education": []
  }
}
```

#### Response

```json
{
  "data": {
    "cvVersionId": "uuid"
  }
}
```

### `GET /api/v1/cvs/{cvDocumentId}/versions`

#### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "status": "base",
      "title": "Base CV - April 2026",
      "jobId": null,
      "createdByAi": false,
      "createdAt": "2026-04-18T12:00:00Z"
    }
  ]
}
```

### `POST /api/v1/cvs/{cvDocumentId}/tailor`

#### Request

```json
{
  "baseVersionId": "uuid",
  "jobId": "uuid",
  "preferences": {
    "maxPages": 1,
    "tone": "concise",
    "preserveTruthfulness": true,
    "emphasize": ["backend", "python", "ai"]
  }
}
```

#### Response

```json
{
  "data": {
    "cvVersion": {
      "id": "uuid",
      "status": "tailored",
      "title": "Tailored CV - Tripadvisor Data Platform",
      "structuredContent": {
        "summary": "Software Engineer with backend and data-oriented experience ..."
      },
      "renderedMarkdown": "Andre Butuc\n\nSummary\n..."
    }
  }
}
```

### `POST /api/v1/cv-versions/{cvVersionId}/feedback`

#### Request

```json
{}
```

#### Response

```json
{
  "data": {
    "feedback": {
      "score": 8.1,
      "strengths": ["Good keyword alignment", "Clear technical direction"],
      "weaknesses": [
        "Some bullets still generic",
        "Could include more metrics"
      ],
      "suggestions": [
        "Quantify backend performance improvements",
        "Tighten summary opening line"
      ]
    }
  }
}
```

## 2.8 Knowledge Vault

### `POST /api/v1/knowledge-items`

#### Request

```json
{
  "type": "note",
  "title": "Rate limiting notes",
  "contentMarkdown": "Token bucket vs leaky bucket...",
  "sourceUrl": null,
  "tags": ["system-design", "rate-limiting"]
}
```

#### Response

```json
{
  "data": {
    "knowledgeItemId": "uuid"
  }
}
```

### `GET /api/v1/knowledge-items`

#### Query Params

- `search`
- `tag`
- `limit`
- `offset`

#### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "type": "note",
      "title": "Rate limiting notes",
      "tags": ["system-design", "rate-limiting"],
      "updatedAt": "2026-04-18T12:30:00Z"
    }
  ],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 12
  }
}
```

### `POST /api/v1/knowledge-items/{knowledgeItemId}/summarize`

#### Request

```json
{}
```

#### Response

```json
{
  "data": {
    "summary": {
      "summaryMarkdown": "This note compares token bucket ...",
      "keyTakeaways": [
        "Token bucket allows bursts",
        "Sliding window is more precise"
      ],
      "flashcards": [
        {
          "question": "What is the main advantage of token bucket?",
          "answer": "Allows controlled bursts while limiting long-term rate"
        }
      ]
    }
  }
}
```

## 2.9 Coach / Orchestration

### `POST /api/v1/coach/message`

#### Request

```json
{
  "message": "Prepare me for this job and tell me what to study this week",
  "jobId": "uuid",
  "context": {
    "includeProfile": true,
    "includeRecentExercises": true,
    "includeCvBaseVersionId": "uuid"
  }
}
```

#### Response

```json
{
  "data": {
    "response": {
      "messageMarkdown": "You are a good but not complete fit for this role ...",
      "actions": [
        {
          "type": "recommend_exercise",
          "label": "Practice distributed systems trade-offs",
          "payload": {
            "topic": "distributed systems",
            "difficulty": "medium"
          }
        },
        {
          "type": "tailor_cv",
          "label": "Generate a tailored CV",
          "payload": {
            "jobId": "uuid",
            "baseVersionId": "uuid"
          }
        }
      ],
      "artifacts": [
        {
          "type": "coach_response",
          "id": "uuid"
        }
      ]
    }
  }
}
```

## 2.10 Workflow Endpoints

If you want explicit backend orchestration:

### `POST /api/v1/workflows/job-prep`

#### Request

```json
{
  "jobId": "uuid",
  "baseCvVersionId": "uuid"
}
```

#### Response

```json
{
  "data": {
    "workflowId": "uuid",
    "status": "completed",
    "result": {
      "gapAnalysisId": "uuid",
      "tailoredCvVersionId": "uuid",
      "studyPlan": [
        {
          "day": 1,
          "focus": "distributed systems basics"
        }
      ]
    }
  }
}
```
