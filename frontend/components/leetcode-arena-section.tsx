"use client";

import { useEffect, useState } from "react";

import {
  api,
  type Exercise,
  type ExerciseEvaluation,
  type ExerciseRunResult,
  type ExerciseSummary,
} from "@/lib/api";

type LeetCodeArenaSectionProps = {
  className?: string;
};

type LeetCodeRuntimeConfig = {
  language?: string;
  functionName?: string;
  signature?: string;
  starterCode?: string;
  tests?: Array<{ args: unknown[]; expected: unknown }>;
};

export function LeetCodeArenaSection({ className }: LeetCodeArenaSectionProps) {
  const [problems, setProblems] = useState<ExerciseSummary[]>([]);
  const [selectedProblemId, setSelectedProblemId] = useState<string | null>(null);
  const [activeProblem, setActiveProblem] = useState<Exercise | null>(null);
  const [code, setCode] = useState("");
  const [runResult, setRunResult] = useState<ExerciseRunResult | null>(null);
  const [evaluation, setEvaluation] = useState<ExerciseEvaluation | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingProblem, setIsLoadingProblem] = useState(false);
  const [isWorking, setIsWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void api
      .listExercises({ tag: "leetcode", limit: 50 })
      .then((response) => {
        if (!active) {
          return;
        }

        const sortedProblems = [...response.data].sort((left, right) =>
          left.title.localeCompare(right.title),
        );
        setProblems(sortedProblems);
        setSelectedProblemId((current) => current ?? sortedProblems[0]?.id ?? null);
        setError(null);
      })
      .catch(() => {
        if (active) {
          setError("LeetCode catalog could not be loaded.");
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedProblemId) {
      return;
    }

    let active = true;
    setIsLoadingProblem(true);

    void api
      .getExercise(selectedProblemId)
      .then((response) => {
        if (!active) {
          return;
        }

        setActiveProblem(response.data);
        const runtime = response.data.constraints.runtime as LeetCodeRuntimeConfig | undefined;
        setCode(runtime?.starterCode ?? "def solve(*args):\n    pass\n");
        setRunResult(null);
        setEvaluation(null);
        setAttemptId(null);
        setNotice(null);
        setError(null);
      })
      .catch(() => {
        if (active) {
          setError("Problem details could not be loaded.");
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingProblem(false);
        }
      });

    return () => {
      active = false;
    };
  }, [selectedProblemId]);

  const runtimeConfig = (activeProblem?.constraints as { runtime?: LeetCodeRuntimeConfig } | undefined)?.runtime;
  const runtimeTests = runtimeConfig?.tests ?? [];
  const visibleProblems = problems.filter((problem) => {
    const matchesDifficulty = difficulty === "all" || problem.difficulty === difficulty;
    const normalizedSearch = search.trim().toLowerCase();
    const matchesSearch =
      normalizedSearch.length === 0 ||
      problem.title.toLowerCase().includes(normalizedSearch) ||
      problem.topic.toLowerCase().includes(normalizedSearch) ||
      problem.type.toLowerCase().includes(normalizedSearch);

    return matchesDifficulty && matchesSearch;
  });

  const handleRun = async () => {
    if (!activeProblem) {
      return;
    }

    setIsWorking(true);
    setError(null);
    setNotice(null);

    try {
      const response = await api.runExerciseCode(activeProblem.id, {
        answerCode: code,
      });
      setRunResult(response.data);
      setNotice("Code run completed.");
    } catch {
      setError("Code could not be run.");
    } finally {
      setIsWorking(false);
    }
  };

  const handleCheck = async () => {
    if (!activeProblem) {
      return;
    }

    setIsWorking(true);
    setError(null);
    setNotice(null);

    try {
      const attemptResponse = await api.createAttempt(activeProblem.id, {
        answerCode: code,
        submit: true,
      });
      setAttemptId(attemptResponse.data.attempt.id);
      const evaluationResponse = await api.evaluateAttempt(attemptResponse.data.attempt.id);
      setEvaluation(evaluationResponse.data);
      setNotice("Solution checked.");
    } catch {
      setError("Solution could not be checked.");
    } finally {
      setIsWorking(false);
    }
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">LeetCode Arena</p>
        <h2>Practice 50 runnable algorithm problems with exact solution checks.</h2>
      </div>

      <p className="section-status">
        {isLoading
          ? "Loading problem catalog..."
          : error ??
            notice ??
            `${problems.length} problem${problems.length === 1 ? "" : "s"} available`}
      </p>

      <div className="leetcode-toolbar">
        <label className="field">
          <span>Search</span>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search title or topic"
          />
        </label>
        <label className="field">
          <span>Difficulty</span>
          <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
            <option value="all">All</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>
      </div>

      <div className="leetcode-layout">
        <aside className="leetcode-sidebar">
          <div className="exercise-history">
            {visibleProblems.map((problem) => {
              const isActive = problem.id === selectedProblemId;

              return (
                <button
                  className={`exercise-history-item leetcode-problem-item ${isActive ? "leetcode-problem-item-active" : ""}`}
                  key={problem.id}
                  type="button"
                  onClick={() => setSelectedProblemId(problem.id)}
                >
                  <strong>{problem.title}</strong>
                  <span>
                    {problem.difficulty} · {problem.topic}
                  </span>
                </button>
              );
            })}
          </div>
          {visibleProblems.length === 0 ? (
            <p className="empty-state">No problems match the current filters.</p>
          ) : null}
        </aside>

        <div className="leetcode-main">
          {activeProblem ? (
            <div className="leetcode-board">
              <div className="exercise-detail">
                <div className="exercise-detail-header">
                  <strong>{activeProblem.title}</strong>
                  <span>
                    {activeProblem.type} · {activeProblem.topic} · {activeProblem.difficulty}
                  </span>
                </div>
                <p>{activeProblem.promptMarkdown}</p>
                <div className="exercise-badges">
                  {activeProblem.tags.map((tag) => (
                    <span className="exercise-badge" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="leetcode-meta-grid">
                  <div>
                    <h4>Signature</h4>
                    <code className="leetcode-signature">{runtimeConfig?.signature ?? "def solve(*args):"}</code>
                  </div>
                  <div>
                    <h4>Test cases</h4>
                    <p className="empty-state">{runtimeTests.length} hidden checks from the catalog.</p>
                  </div>
                </div>
              </div>

              <div className="leetcode-editor-pane">
                <div className="section-heading">
                  <p className="section-kicker">Editor</p>
                  <h3>Python</h3>
                </div>
                <textarea
                  className="code-editor"
                  rows={18}
                  value={code}
                  onChange={(event) => setCode(event.target.value)}
                  spellCheck={false}
                />
                <div className="section-actions section-actions-left">
                  <button className="ghost-button" type="button" onClick={() => setCode(runtimeConfig?.starterCode ?? "def solve(*args):\n    pass\n")}>
                    Reset
                  </button>
                  <button className="ghost-button" type="button" onClick={() => void handleRun()} disabled={isWorking}>
                    {isWorking ? "Running..." : "Run code"}
                  </button>
                  <button className="primary-button" type="button" onClick={() => void handleCheck()} disabled={isWorking || code.trim().length === 0}>
                    {isWorking ? "Checking..." : "Check solution"}
                  </button>
                </div>
              </div>

              <div className="leetcode-results-grid">
                <div className="learning-panel">
                  <h3>Run result</h3>
                  {runResult ? (
                    <>
                      <p className="score-chip">
                        {runResult.passedCases}/{runResult.totalCases} tests passed
                      </p>
                      <p>{runResult.message}</p>
                      {runResult.stderr ? <pre className="leetcode-log">{runResult.stderr}</pre> : null}
                      <div className="leetcode-case-list">
                        {runResult.caseResults.map((caseResult) => (
                          <article className="leetcode-case" key={caseResult.index}>
                            <strong>Case {caseResult.index}</strong>
                            <p>{caseResult.passed ? "Passed" : "Failed"}</p>
                            {caseResult.error ? <pre className="leetcode-log">{caseResult.error}</pre> : null}
                          </article>
                        ))}
                      </div>
                    </>
                  ) : (
                    <p className="empty-state">Run the code to see the sample-case result.</p>
                  )}
                </div>

                <div className="learning-panel">
                  <h3>Check result</h3>
                  {evaluation ? (
                    <>
                      <p className="score-chip">Overall score: {evaluation.overallScore}/10</p>
                      <p>{evaluation.feedbackMarkdown}</p>
                      <h4>Strengths</h4>
                      <ul className="plain-list">
                        {evaluation.strengths.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                      <h4>Weaknesses</h4>
                      <ul className="plain-list">
                        {evaluation.weaknesses.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </>
                  ) : (
                    <p className="empty-state">Check your solution to save a scored attempt.</p>
                  )}
                  {attemptId ? <p className="empty-state">Attempt id: {attemptId}</p> : null}
                </div>
              </div>
            </div>
          ) : isLoadingProblem ? (
            <p className="empty-state">Loading problem details...</p>
          ) : (
            <p className="empty-state">Select a LeetCode problem to begin.</p>
          )}
        </div>
      </div>
    </section>
  );
}
