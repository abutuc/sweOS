# Product Epics & User Stories

---

## 🧩 EPIC 1 — User Profile & Skill Model

### Goal

Have a structured understanding of “who you are as an engineer”.

### User Stories

**US1.1**  
As a user, I want to define my experience, stack, and goals so the system can personalize recommendations.

**US1.2**  
As a user, I want to track my skills by category so I can see strengths and weaknesses.

**US1.3**  
As a user, I want to update my target role (e.g. Backend Engineer, AI Engineer) so the system adapts exercises and CV.

### Acceptance Criteria

- Profile includes:
  - years of experience
  - stack (tags)
  - target role(s)
- Skill model is structured (not free text)
- Skills have levels (e.g. 1–5 or Beginner → Advanced)

---

## 🧠 EPIC 2 — Learning Gym (Core Feature)

### Goal

Daily practice + feedback loop.

### User Stories

**US2.1**  
As a user, I want to generate an exercise by topic and difficulty.

**US2.2**  
As a user, I want to submit a solution (text/code).

**US2.3**  
As a user, I want feedback on my solution so I can improve.

**US2.4**  
As a user, I want hints before seeing the solution.

**US2.5**  
As a user, I want the system to track my weak topics.

**US2.6**  
As a user, I want recommended next exercises based on performance.

### Acceptance Criteria

- Exercise includes:
  - description
  - constraints
  - expected reasoning
- Feedback includes:
  - strengths
  - weaknesses
  - improved solution
- Weak topics are persisted

---

## 🧱 EPIC 3 — Progress & Analytics

### Goal

Make improvement visible.

### User Stories

**US3.1**  
As a user, I want to see my progress by topic.

**US3.2**  
As a user, I want to see my recent activity (timeline).

**US3.3**  
As a user, I want to know my weakest areas.

### Acceptance Criteria

- Dashboard shows:
  - exercises completed
  - accuracy/quality score
  - weak topics
- Data updates after each submission

---

## 💼 EPIC 4 — CV & Job Matching (High Value)

### Goal

Bridge learning → real opportunities.

### User Stories

**US4.1**  
As a user, I want to store my CV in structured form.

**US4.2**  
As a user, I want to paste a job description and extract requirements.

**US4.3**  
As a user, I want to generate a tailored CV for a job.

**US4.4**  
As a user, I want to see what is missing in my profile for that job.

**US4.5**  
As a user, I want to save job opportunities.

### Acceptance Criteria

- Job parsing extracts:
  - skills
  - responsibilities
- CV tailoring:
  - rewrites bullets
  - aligns keywords
- Gap analysis:
  - shows missing skills clearly

---

## 🤖 EPIC 5 — AI Coach (Workflow Interface)

### Goal

One interface to orchestrate everything.

### User Stories

**US5.1**  
As a user, I want to ask “prepare me for this job”.

**US5.2**  
As a user, I want guidance on what to study next.

**US5.3**  
As a user, I want explanations of mistakes.

### Acceptance Criteria

- Chat is context-aware (profile + history)
- Can trigger workflows:
  - generate exercise
  - analyze job
  - tailor CV
- Outputs are editable (not locked)

---

## 🧰 EPIC 6 — Knowledge Vault (Light Version)

### Goal

Store useful things.

### User Stories

**US6.1**  
As a user, I want to save notes/snippets.

**US6.2**  
As a user, I want to search my knowledge.

**US6.3**  
As a user, I want AI to summarize my notes.

### Acceptance Criteria

- Supports markdown
- Supports tagging
- Search works (keyword minimum)
