# Detailed Database Schema

## 1.1 Domain Overview

You currently need these bounded contexts:

- Identity
- Profile & Skills
- Learning
- Exercises & Evaluations
- Jobs
- CV / Resume
- Knowledge Vault
- AI Workflows
- Analytics

## 1.2 PostgreSQL Conventions

Recommended conventions:

- primary keys: `uuid`
- timestamps: `timestamptz`
- enums for stable states
- `JSONB` only where flexibility is useful
- soft delete only where recovery matters
- audit fields on important tables

## 1.3 PostgreSQL Enum Types

```sql
create type proficiency_level as enum (
  'none',
  'beginner',
  'elementary',
  'intermediate',
  'advanced',
  'expert'
);

create type exercise_type as enum (
  'dsa',
  'system_design',
  'architecture_decision',
  'database_optimization',
  'debugging',
  'agile_scenario',
  'code_review'
);

create type difficulty_level as enum (
  'easy',
  'medium',
  'hard'
);

create type submission_status as enum (
  'draft',
  'submitted',
  'evaluated',
  'failed_evaluation'
);

create type artifact_type as enum (
  'exercise_prompt',
  'exercise_feedback',
  'job_parse',
  'gap_analysis',
  'cv_tailored',
  'coach_response',
  'knowledge_summary'
);

create type job_status as enum (
  'saved',
  'considering',
  'applied',
  'interviewing',
  'offer',
  'rejected',
  'archived'
);

create type source_type as enum (
  'manual',
  'rss',
  'job_board',
  'import',
  'ai_generated'
);

create type cv_version_status as enum (
  'base',
  'tailored',
  'archived'
);

create type workflow_status as enum (
  'queued',
  'running',
  'completed',
  'failed',
  'cancelled'
);

create type note_type as enum (
  'note',
  'snippet',
  'article_summary',
  'playbook_entry'
);
```

## 1.4 Core Tables

### A. `users`

For MVP, you can support one user, but design as multi-user.

```sql
create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text not null,
  full_name text,
  timezone text not null default 'Europe/Lisbon',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### B. `user_profiles`

Keep mutable profile data outside `users`.

```sql
create table user_profiles (
  user_id uuid primary key references users(id) on delete cascade,
  headline text,
  bio text,
  years_experience numeric(4,1),
  current_role text,
  stack text[],
  target_role text,
  target_roles text[],
  target_seniority text,
  preferred_industries text[],
  preferred_locations text[],
  preferred_work_modes text[],
  salary_expectation_min integer,
  salary_expectation_max integer,
  learning_goals text[],
  summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### C. `skills`

Master catalog.

```sql
create table skills (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  category text not null,
  description text,
  created_at timestamptz not null default now()
);
```

Examples:

- `java`
- `python`
- `postgresql`
- `system-design`
- `distributed-systems`
- `agile-retrospectives`

### D. `user_skills`

Tracks your perceived and measured skill.

```sql
create table user_skills (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  skill_id uuid not null references skills(id) on delete cascade,
  self_assessed_level proficiency_level not null default 'none',
  measured_level proficiency_level,
  confidence_score numeric(5,2),
  evidence_count integer not null default 0,
  last_evaluated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, skill_id)
);
```

### E. `goals`

```sql
create table goals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  title text not null,
  description text,
  target_date date,
  horizon text not null default 'medium',
  priority integer not null default 3,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### F. `user_preferences`

```sql
create table user_preferences (
  user_id uuid primary key references users(id) on delete cascade,
  content_sources text[],
  notification_cadence text not null default 'weekly',
  ai_assistance_level text not null default 'balanced',
  privacy_settings jsonb not null default '{}'::jsonb,
  target_opportunity_filters jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

## 1.5 Learning Domain

### G. `exercises`

Stores generated or manually created exercises.

```sql
create table exercises (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete set null,
  type exercise_type not null,
  topic text not null,
  subtopic text,
  difficulty difficulty_level not null,
  title text not null,
  prompt_markdown text not null,
  constraints_json jsonb not null default '{}'::jsonb,
  expected_outcomes_json jsonb not null default '[]'::jsonb,
  hints_json jsonb not null default '[]'::jsonb,
  canonical_solution_json jsonb,
  tags text[] not null default '{}',
  source source_type not null default 'ai_generated',
  created_by_ai boolean not null default false,
  created_at timestamptz not null default now()
);
```

#### Suggested JSON Shapes

**`constraints_json`**

```json
{
  "timeLimitMinutes": 25,
  "mustConsider": ["time complexity", "edge cases"],
  "forbidden": ["external libraries"]
}
```

**`expected_outcomes_json`**

```json
[
  "Identifies trade-offs clearly",
  "Provides O(n log n) or better",
  "Explains why chosen approach is appropriate"
]
```

**`canonical_solution_json`**

```json
{
  "summary": "Use binary search over answer space.",
  "steps": ["Sort input", "Apply two-pointer check"],
  "code": "optional solution",
  "complexity": {
    "time": "O(n log n)",
    "space": "O(1)"
  }
}
```

### H. `exercise_attempts`

One exercise can have multiple attempts.

```sql
create table exercise_attempts (
  id uuid primary key default gen_random_uuid(),
  exercise_id uuid not null references exercises(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  status submission_status not null default 'draft',
  answer_markdown text,
  answer_code text,
  answer_sql text,
  answer_json jsonb not null default '{}'::jsonb,
  submitted_at timestamptz,
  evaluated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### I. `exercise_evaluations`

Separate table for evaluation traceability and versioning.

```sql
create table exercise_evaluations (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid not null references exercise_attempts(id) on delete cascade,
  overall_score numeric(5,2) not null,
  rubric_scores_json jsonb not null,
  strengths_json jsonb not null default '[]'::jsonb,
  weaknesses_json jsonb not null default '[]'::jsonb,
  feedback_markdown text not null,
  recommended_next_topics text[] not null default '{}',
  improvement_actions_json jsonb not null default '[]'::jsonb,
  evaluator_type text not null default 'ai',
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

#### `rubric_scores_json` Example

```json
{
  "correctness": 7,
  "efficiency": 6,
  "clarity": 8,
  "tradeOffReasoning": 5,
  "maintainability": 7
}
```

### J. `user_topic_mastery`

Aggregated read model for dashboard and recommendations.

```sql
create table user_topic_mastery (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  topic text not null,
  subtopic text,
  mastery_score numeric(5,2) not null default 0,
  confidence_score numeric(5,2) not null default 0,
  attempts_count integer not null default 0,
  last_practiced_at timestamptz,
  updated_at timestamptz not null default now(),
  unique (user_id, topic, subtopic)
);
```

## 1.6 Jobs Domain

### K. `companies`

```sql
create table companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  website_url text,
  linkedin_url text,
  location text,
  notes text,
  created_at timestamptz not null default now(),
  unique(name)
);
```

### L. `jobs`

```sql
create table jobs (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id) on delete set null,
  external_id text,
  source source_type not null default 'manual',
  source_url text,
  title text not null,
  raw_description text not null,
  location text,
  work_mode text,
  salary_min integer,
  salary_max integer,
  currency text,
  seniority text,
  employment_type text,
  posted_at timestamptz,
  imported_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (external_id, source_url)
);
```

### M. `job_parses`

AI-extracted structure from the raw JD.

```sql
create table job_parses (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references jobs(id) on delete cascade,
  parsed_title text,
  parsed_company_name text,
  responsibilities_json jsonb not null default '[]'::jsonb,
  required_skills_json jsonb not null default '[]'::jsonb,
  preferred_skills_json jsonb not null default '[]'::jsonb,
  keywords_json jsonb not null default '[]'::jsonb,
  seniority_assessment text,
  summary_markdown text,
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

### N. `user_jobs`

User-specific tracking.

```sql
create table user_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  job_id uuid not null references jobs(id) on delete cascade,
  status job_status not null default 'saved',
  match_score numeric(5,2),
  interest_score numeric(5,2),
  notes text,
  applied_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, job_id)
);
```

### O. `job_gap_analyses`

```sql
create table job_gap_analyses (
  id uuid primary key default gen_random_uuid(),
  user_job_id uuid not null references user_jobs(id) on delete cascade,
  fit_summary_markdown text not null,
  matched_skills_json jsonb not null default '[]'::jsonb,
  missing_skills_json jsonb not null default '[]'::jsonb,
  weak_evidence_json jsonb not null default '[]'::jsonb,
  recommendation_json jsonb not null default '{}'::jsonb,
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

## 1.7 CV / Resume Domain

### P. `cv_documents`

Logical CV container.

```sql
create table cv_documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  name text not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### Q. `cv_versions`

Versioned CV outputs.

```sql
create table cv_versions (
  id uuid primary key default gen_random_uuid(),
  cv_document_id uuid not null references cv_documents(id) on delete cascade,
  based_on_version_id uuid references cv_versions(id) on delete set null,
  job_id uuid references jobs(id) on delete set null,
  status cv_version_status not null,
  title text not null,
  summary text,
  structured_content_json jsonb not null,
  rendered_markdown text,
  ats_plain_text text,
  created_by_ai boolean not null default false,
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

#### `structured_content_json` Example

```json
{
  "header": {
    "fullName": "Andre Butuc",
    "email": "andre@example.com",
    "location": "Portugal"
  },
  "summary": "Software Engineer with ...",
  "experience": [
    {
      "company": "X",
      "role": "Software Engineer",
      "startDate": "2024-01",
      "endDate": "2025-01",
      "bullets": ["Built ...", "Improved ..."]
    }
  ],
  "projects": [],
  "skills": {
    "languages": ["Java", "Python"],
    "databases": ["PostgreSQL"]
  },
  "education": []
}
```

### R. `cv_feedback`

Optional quality pass.

```sql
create table cv_feedback (
  id uuid primary key default gen_random_uuid(),
  cv_version_id uuid not null references cv_versions(id) on delete cascade,
  score numeric(5,2),
  strengths_json jsonb not null default '[]'::jsonb,
  weaknesses_json jsonb not null default '[]'::jsonb,
  suggestions_json jsonb not null default '[]'::jsonb,
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

## 1.8 Knowledge Vault

### S. `knowledge_items`

```sql
create table knowledge_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  type note_type not null,
  title text not null,
  content_markdown text not null,
  source source_type not null default 'manual',
  source_url text,
  tags text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### T. `knowledge_summaries`

```sql
create table knowledge_summaries (
  id uuid primary key default gen_random_uuid(),
  knowledge_item_id uuid not null references knowledge_items(id) on delete cascade,
  summary_markdown text not null,
  key_takeaways_json jsonb not null default '[]'::jsonb,
  flashcards_json jsonb not null default '[]'::jsonb,
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

## 1.9 AI Traceability

### U. `ai_workflows`

Top-level execution log.

```sql
create table ai_workflows (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  workflow_name text not null,
  status workflow_status not null default 'queued',
  input_json jsonb not null,
  output_json jsonb,
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now()
);
```

### V. `ai_artifacts`

Stores AI-generated outputs by type.

```sql
create table ai_artifacts (
  id uuid primary key default gen_random_uuid(),
  workflow_id uuid references ai_workflows(id) on delete set null,
  user_id uuid not null references users(id) on delete cascade,
  artifact_type artifact_type not null,
  related_entity_type text,
  related_entity_id uuid,
  content_json jsonb not null,
  prompt_version text,
  model_name text,
  created_at timestamptz not null default now()
);
```

### W. `ai_prompt_versions`

Critical for reproducibility.

```sql
create table ai_prompt_versions (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  version text not null,
  system_prompt text not null,
  developer_prompt text,
  expected_output_schema_json jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique(name, version)
);
```

## 1.10 Optional Embeddings

If you add vector search later:

### X. `document_embeddings`

```sql
create table document_embeddings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  entity_type text not null,
  entity_id uuid not null,
  chunk_index integer not null,
  content_text text not null,
  embedding vector(1536),
  created_at timestamptz not null default now()
);
```

## 1.11 Indexes

Important indexes:

```sql
create index idx_exercises_type_topic_difficulty
  on exercises(type, topic, difficulty);

create index idx_attempts_user_exercise
  on exercise_attempts(user_id, exercise_id);

create index idx_topic_mastery_user_topic
  on user_topic_mastery(user_id, topic, subtopic);

create index idx_jobs_title on jobs(title);
create index idx_jobs_posted_at on jobs(posted_at desc);
create index idx_user_jobs_user_status on user_jobs(user_id, status);

create index idx_knowledge_items_user_tags
  on knowledge_items using gin(tags);

create index idx_exercises_tags
  on exercises using gin(tags);

create index idx_jobs_raw_description_fts
  on jobs using gin(to_tsvector('english', raw_description));

create index idx_knowledge_items_content_fts
  on knowledge_items using gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content_markdown, '')));
```

## 1.12 Relationship Summary

- `users` 1—1 `user_profiles`
- `users` 1—1 `user_preferences`
- `users` 1—N `user_skills`
- `users` 1—N `goals`
- `users` 1—N `exercise_attempts`
- `exercises` 1—N `exercise_attempts`
- `exercise_attempts` 1—N `exercise_evaluations`
- `users` 1—N `user_topic_mastery`
- `companies` 1—N `jobs`
- `jobs` 1—N `job_parses`
- `users` N—N `jobs` via `user_jobs`
- `user_jobs` 1—N `job_gap_analyses`
- `cv_documents` 1—N `cv_versions`
- `cv_versions` 1—N `cv_feedback`
- `knowledge_items` 1—N `knowledge_summaries`
- `users` 1—N `ai_workflows`
- `ai_workflows` 1—N `ai_artifacts`
