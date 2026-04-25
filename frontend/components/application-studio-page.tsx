"use client";

import { useEffect, useState } from "react";

import { useOnboardingStatus } from "@/components/use-onboarding-status";
import { api, type CvFeedback, type CvTailoredVersion, type JobGapAnalysis, type JobListItem, type JobParse } from "@/lib/api";

const DEFAULT_JOB = {
  title: "AI Backend Engineer",
  companyName: "",
  location: "Remote",
  workMode: "remote",
  rawDescription: "Responsibilities\n- Build backend and AI platform services.\nRequirements\n- Python, FastAPI, PostgreSQL, Docker, LLM.",
};

const DEFAULT_CV_CONTENT = JSON.stringify(
  {
    header: {
      fullName: "Your Name",
      email: "you@example.com",
      location: "Portugal",
    },
    summary: "Software engineer focused on backend systems.",
    experience: [
      {
        company: "Company X",
        role: "Software Engineer",
        bullets: ["Built backend APIs serving 1000 users."],
      },
    ],
    skills: {
      languages: ["Python", "TypeScript"],
      databases: ["PostgreSQL"],
    },
    education: [],
  },
  null,
  2,
);

export function ApplicationStudioPage() {
  useOnboardingStatus();

  const [jobDraft, setJobDraft] = useState(DEFAULT_JOB);
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [activeUserJobId, setActiveUserJobId] = useState<string | null>(null);
  const [jobParse, setJobParse] = useState<JobParse | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<JobGapAnalysis | null>(null);
  const [cvDocumentId, setCvDocumentId] = useState<string | null>(null);
  const [baseVersionId, setBaseVersionId] = useState<string | null>(null);
  const [cvContent, setCvContent] = useState(DEFAULT_CV_CONTENT);
  const [tailoredCv, setTailoredCv] = useState<CvTailoredVersion | null>(null);
  const [feedback, setFeedback] = useState<CvFeedback | null>(null);
  const [status, setStatus] = useState("Application Studio ready.");
  const [isWorking, setIsWorking] = useState(false);

  const refreshJobs = async () => {
    const response = await api.listJobs();
    setJobs(response.data);
  };

  useEffect(() => {
    void refreshJobs().catch(() => setStatus("Saved jobs could not be loaded."));
  }, []);

  const createParseAndSaveJob = async () => {
    setIsWorking(true);
    setStatus("Creating and parsing job...");
    setGapAnalysis(null);
    try {
      const created = await api.createJob(jobDraft);
      const jobId = created.data.job.id;
      const parsed = await api.parseJob(jobId);
      const saved = await api.saveJob(jobId, { status: "saved", notes: "Saved from Application Studio" });
      setActiveJobId(jobId);
      setActiveUserJobId(saved.data.userJobId);
      setJobParse(parsed.data.parse);
      await refreshJobs();
      setStatus("Job saved and requirements extracted.");
    } catch {
      setStatus("Job could not be created or parsed.");
    } finally {
      setIsWorking(false);
    }
  };

  const analyzeActiveJob = async () => {
    if (!activeUserJobId) {
      setStatus("Save a job before running gap analysis.");
      return;
    }

    setIsWorking(true);
    try {
      const response = await api.analyzeJobGap(activeUserJobId);
      setGapAnalysis(response.data.analysis);
      await refreshJobs();
      setStatus("Gap analysis generated.");
    } catch {
      setStatus("Gap analysis could not be generated.");
    } finally {
      setIsWorking(false);
    }
  };

  const createBaseCv = async () => {
    setIsWorking(true);
    try {
      const content = JSON.parse(cvContent) as Record<string, unknown>;
      const document = await api.createCvDocument({ name: "Base CV", description: "Application Studio CV" });
      const version = await api.createCvVersion(document.data.cvDocumentId, {
        status: "base",
        title: "Base CV",
        structuredContent: content,
      });
      setCvDocumentId(document.data.cvDocumentId);
      setBaseVersionId(version.data.cvVersionId);
      setStatus("Structured base CV stored.");
    } catch {
      setStatus("CV JSON is invalid or could not be stored.");
    } finally {
      setIsWorking(false);
    }
  };

  const tailorActiveCv = async () => {
    if (!cvDocumentId || !baseVersionId || !activeJobId) {
      setStatus("Create a base CV and save a job before tailoring.");
      return;
    }

    setIsWorking(true);
    try {
      const response = await api.tailorCv(cvDocumentId, {
        baseVersionId,
        jobId: activeJobId,
        preferences: { tone: "concise", preserveTruthfulness: true, emphasize: ["backend", "ai"] },
      });
      setTailoredCv(response.data.cvVersion);
      setFeedback(null);
      setStatus("Tailored CV generated.");
    } catch {
      setStatus("Tailored CV could not be generated.");
    } finally {
      setIsWorking(false);
    }
  };

  const reviewTailoredCv = async () => {
    if (!tailoredCv) {
      return;
    }

    setIsWorking(true);
    try {
      const response = await api.createCvFeedback(tailoredCv.id);
      setFeedback(response.data.feedback);
      setStatus("CV feedback generated.");
    } catch {
      setStatus("CV feedback could not be generated.");
    } finally {
      setIsWorking(false);
    }
  };

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <p className="eyebrow">Application Studio</p>
        <h1>Convert learning progress into job-ready evidence.</h1>
        <p className="hero-copy">
          Save opportunities, extract requirements, inspect gaps, and tailor structured CV versions without mixing this workflow into daily practice.
        </p>
      </section>

      <p className="section-status">{isWorking ? "Working..." : status}</p>

      <section className="workspace-grid">
        <div className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Job Matching</p>
            <h2>Paste a role and extract matching signals.</h2>
          </div>
          <div className="field-grid">
            <label className="field">
              <span>Title</span>
              <input value={jobDraft.title} onChange={(event) => setJobDraft((current) => ({ ...current, title: event.target.value }))} />
            </label>
            <label className="field">
              <span>Company</span>
              <input value={jobDraft.companyName} onChange={(event) => setJobDraft((current) => ({ ...current, companyName: event.target.value }))} />
            </label>
            <label className="field">
              <span>Location</span>
              <input value={jobDraft.location} onChange={(event) => setJobDraft((current) => ({ ...current, location: event.target.value }))} />
            </label>
            <label className="field">
              <span>Work mode</span>
              <input value={jobDraft.workMode} onChange={(event) => setJobDraft((current) => ({ ...current, workMode: event.target.value }))} />
            </label>
            <label className="field field-wide">
              <span>Job description</span>
              <textarea rows={9} value={jobDraft.rawDescription} onChange={(event) => setJobDraft((current) => ({ ...current, rawDescription: event.target.value }))} />
            </label>
          </div>
          <div className="section-actions">
            <button className="primary-button" type="button" onClick={createParseAndSaveJob} disabled={isWorking}>
              Save and parse job
            </button>
            <button className="ghost-button" type="button" onClick={analyzeActiveJob} disabled={isWorking || !activeUserJobId}>
              Analyze gaps
            </button>
          </div>
          {jobParse ? (
            <div className="learning-subgrid">
              <article className="mastery-card">
                <strong>Required skills</strong>
                <p>{jobParse.requiredSkills.join(", ") || "No skills extracted yet."}</p>
              </article>
              <article className="mastery-card">
                <strong>Responsibilities</strong>
                <p>{jobParse.responsibilities.join(" ") || "No responsibilities extracted yet."}</p>
              </article>
            </div>
          ) : null}
        </div>

        <div className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">CV Studio</p>
            <h2>Store structured CV content and generate targeted versions.</h2>
          </div>
          <label className="field">
            <span>Structured CV JSON</span>
            <textarea rows={16} value={cvContent} onChange={(event) => setCvContent(event.target.value)} />
          </label>
          <div className="section-actions">
            <button className="primary-button" type="button" onClick={createBaseCv} disabled={isWorking}>
              Store base CV
            </button>
            <button className="ghost-button" type="button" onClick={tailorActiveCv} disabled={isWorking || !baseVersionId || !activeJobId}>
              Tailor to active job
            </button>
          </div>
        </div>

        <div className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Saved Opportunities</p>
            <h2>Track roles and match score updates.</h2>
          </div>
          <div className="mastery-list">
            {jobs.map((job) => (
              <button
                className="exercise-history-item"
                key={job.userJobId ?? job.id}
                type="button"
                onClick={() => {
                  setActiveJobId(job.id);
                  setActiveUserJobId(job.userJobId);
                  setStatus(`${job.title} selected.`);
                }}
              >
                <strong>{job.title}</strong>
                <span>
                  {job.companyName ?? "Unknown company"} · {job.status ?? "unsaved"} · {job.matchScore === null ? "not scored" : `${job.matchScore}/10`}
                </span>
              </button>
            ))}
            {jobs.length === 0 ? <p className="empty-state">Saved jobs will appear here.</p> : null}
          </div>
        </div>

        <div className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Readiness</p>
            <h2>Missing proof and tailored output.</h2>
          </div>
          {gapAnalysis ? (
            <>
              <p>{gapAnalysis.fitSummaryMarkdown}</p>
              <h3>Missing skills</h3>
              <div className="exercise-badges">
                {gapAnalysis.missingSkills.map((item) => (
                  <span className="exercise-badge" key={item.skill}>
                    {item.skill} · {item.severity}
                  </span>
                ))}
              </div>
              <h3>Next actions</h3>
              <ul className="plain-list">
                {(gapAnalysis.recommendation.nextActions ?? []).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          ) : (
            <p className="empty-state">Run gap analysis to see missing skills and evidence.</p>
          )}

          {tailoredCv ? (
            <>
              <h3>{tailoredCv.title}</h3>
              <pre className="markdown-preview">{tailoredCv.renderedMarkdown}</pre>
              <button className="ghost-button" type="button" onClick={reviewTailoredCv} disabled={isWorking}>
                Review tailored CV
              </button>
            </>
          ) : null}

          {feedback ? (
            <article className="mastery-card">
              <div className="goal-card-topline">
                <strong>CV feedback</strong>
                <span>{feedback.score}/10</span>
              </div>
              <p>{feedback.suggestions.join(" ")}</p>
            </article>
          ) : null}
        </div>
      </section>
    </>
  );
}
