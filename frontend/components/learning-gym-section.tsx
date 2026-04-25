"use client";

import { useEffect, useState } from "react";

import {
  api,
  type Exercise,
  type ExerciseAttempt,
  type ExerciseEvaluation,
  type ExerciseSummary,
  type TopicMastery,
} from "@/lib/api";

type LearningGymSectionProps = {
  className?: string;
  initialExercises?: ExerciseSummary[];
  initialTopicMastery?: TopicMastery[];
  skipInitialLoad?: boolean;
};

const DEFAULT_DRAFT = {
  type: "system_design",
  topic: "scalability",
  subtopic: "rate limiting",
  difficulty: "medium",
  timeLimitMinutes: "30",
  includeHints: true,
};
const MAX_RENDERED_EXERCISES = 30;
const MAX_RENDERED_MASTERY_ITEMS = 20;

function difficultyForMastery(score: number) {
  if (score < 5) {
    return "easy";
  }

  if (score >= 8) {
    return "hard";
  }

  return "medium";
}

export function LearningGymSection({
  className,
  initialExercises = [],
  initialTopicMastery = [],
  skipInitialLoad = false,
}: LearningGymSectionProps) {
  const [draft, setDraft] = useState(DEFAULT_DRAFT);
  const [exercises, setExercises] = useState<ExerciseSummary[]>(initialExercises);
  const [topicMastery, setTopicMastery] = useState<TopicMastery[]>(initialTopicMastery);
  const [activeExercise, setActiveExercise] = useState<Exercise | null>(null);
  const [attempt, setAttempt] = useState<ExerciseAttempt | null>(null);
  const [evaluation, setEvaluation] = useState<ExerciseEvaluation | null>(null);
  const [answerMarkdown, setAnswerMarkdown] = useState("");
  const [answerCode, setAnswerCode] = useState("");
  const [revealedHintCount, setRevealedHintCount] = useState(0);
  const [isLoading, setIsLoading] = useState(!skipInitialLoad);
  const [isWorking, setIsWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (skipInitialLoad) {
      return;
    }

    let active = true;

    void Promise.all([api.listExercises(), api.getTopicMastery()])
      .then(([exerciseResponse, masteryResponse]) => {
        if (!active) {
          return;
        }
        setExercises(exerciseResponse.data);
        setTopicMastery(masteryResponse.data);
        setError(null);
        setNotice(null);
      })
      .catch(() => {
        if (active) {
          setError("Learning gym could not be loaded.");
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
  }, [skipInitialLoad]);

  const weakestTopics = topicMastery.slice(0, 3).map((item) => item.topic);
  const visibleExercises = exercises.slice(0, MAX_RENDERED_EXERCISES);
  const visibleTopicMastery = topicMastery.slice(0, MAX_RENDERED_MASTERY_ITEMS);

  const refreshMastery = async () => {
    const masteryResponse = await api.getTopicMastery();
    setTopicMastery(masteryResponse.data);
  };

  const handleGenerate = async () => {
    setIsWorking(true);
    setError(null);
    setNotice(null);

    try {
      const response = await api.generateExercise({
        type: draft.type,
        topic: draft.topic,
        subtopic: draft.subtopic || undefined,
        difficulty: draft.difficulty,
        timeLimitMinutes: Number(draft.timeLimitMinutes),
        includeHints: draft.includeHints,
        context: {
          targetRole: null,
          weakTopics: weakestTopics,
        },
      });
      const generated = response.data.exercise;
      setActiveExercise(generated);
      setAttempt(null);
      setEvaluation(null);
      setAnswerMarkdown("");
      setAnswerCode("");
      setRevealedHintCount(0);
      const exerciseListResponse = await api.listExercises();
      setExercises(exerciseListResponse.data);
      setNotice("Exercise generated.");
    } catch {
      setError("Exercise could not be generated.");
    } finally {
      setIsWorking(false);
    }
  };

  const loadExercise = async (exerciseId: string) => {
    setIsWorking(true);
    setError(null);
    setNotice(null);

    try {
      const response = await api.getExercise(exerciseId);
      setActiveExercise(response.data);
      setAttempt(null);
      setEvaluation(null);
      setAnswerMarkdown("");
      setAnswerCode("");
      setRevealedHintCount(0);
    } catch {
      setError("Exercise could not be loaded.");
    } finally {
      setIsWorking(false);
    }
  };

  const handleSubmit = async () => {
    if (!activeExercise) {
      return;
    }

    setIsWorking(true);
    setError(null);
    setNotice(null);

    try {
      const attemptResponse = await api.createAttempt(activeExercise.id, {
        answerMarkdown,
        answerCode,
        submit: true,
      });
      setAttempt(attemptResponse.data.attempt);
      const evaluationResponse = await api.evaluateAttempt(attemptResponse.data.attempt.id);
      setEvaluation(evaluationResponse.data);
      await refreshMastery();
      setNotice("Submission evaluated.");
    } catch {
      setError("Submission could not be evaluated.");
    } finally {
      setIsWorking(false);
    }
  };

  const applyRecommendedTopic = (topic: string) => {
    setDraft((current) => ({ ...current, topic, subtopic: topic }));
    setNotice(`Topic preset updated to ${topic}.`);
  };

  const applyAdaptivePreset = () => {
    const weakestTopic = topicMastery[0];

    if (!weakestTopic) {
      setNotice("Adaptive setup will be available after your first evaluated submission.");
      return;
    }

    setDraft((current) => ({
      ...current,
      topic: weakestTopic.topic,
      subtopic: weakestTopic.topic,
      difficulty: difficultyForMastery(weakestTopic.averageScore),
      includeHints: true,
    }));
    setNotice(`Adaptive setup targets ${weakestTopic.topic} at ${difficultyForMastery(weakestTopic.averageScore)} difficulty.`);
  };

  const revealNextHint = () => {
    if (!activeExercise) {
      return;
    }

    setRevealedHintCount((current) => Math.min(current + 1, activeExercise.hints.length));
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Learning Gym</p>
        <h2>Generate practice, submit an answer, and let the system track your weak topics.</h2>
      </div>

      <p className="section-status">
        {isLoading
          ? "Loading learning gym..."
          : error ??
            notice ??
            `${exercises.length} exercise${exercises.length === 1 ? "" : "s"} generated, ${topicMastery.length} topic signal${topicMastery.length === 1 ? "" : "s"}`}
      </p>

      <div className="learning-grid">
        <div className="learning-column">
          <div className="learning-panel">
            <h3>Generate</h3>
            <div className="field-grid">
              <label className="field">
                <span>Exercise type</span>
                <select
                  value={draft.type}
                  onChange={(event) => setDraft((current) => ({ ...current, type: event.target.value }))}
                >
                  <option value="dsa">DSA</option>
                  <option value="system_design">System design</option>
                  <option value="architecture_decision">Architecture decision</option>
                  <option value="database_optimization">Database optimization</option>
                  <option value="debugging">Debugging</option>
                  <option value="agile_scenario">Agile scenario</option>
                  <option value="code_review">Code review</option>
                </select>
              </label>
              <label className="field">
                <span>Difficulty</span>
                <select
                  value={draft.difficulty}
                  onChange={(event) =>
                    setDraft((current) => ({ ...current, difficulty: event.target.value }))
                  }
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </label>
              <label className="field">
                <span>Topic</span>
                <input
                  value={draft.topic}
                  onChange={(event) => setDraft((current) => ({ ...current, topic: event.target.value }))}
                  placeholder="scalability"
                />
              </label>
              <label className="field">
                <span>Subtopic</span>
                <input
                  value={draft.subtopic}
                  onChange={(event) =>
                    setDraft((current) => ({ ...current, subtopic: event.target.value }))
                  }
                  placeholder="rate limiting"
                />
              </label>
              <label className="field">
                <span>Time limit</span>
                <input
                  type="number"
                  min="5"
                  max="120"
                  value={draft.timeLimitMinutes}
                  onChange={(event) =>
                    setDraft((current) => ({ ...current, timeLimitMinutes: event.target.value }))
                  }
                />
              </label>
              <label className="field field-inline">
                <span>Include hints</span>
                <input
                  type="checkbox"
                  checked={draft.includeHints}
                  onChange={(event) =>
                    setDraft((current) => ({ ...current, includeHints: event.target.checked }))
                  }
                />
              </label>
            </div>

            <div className="section-actions">
              <button className="ghost-button" type="button" onClick={applyAdaptivePreset} disabled={isWorking}>
                Use adaptive setup
              </button>
              <button className="primary-button" type="button" onClick={handleGenerate} disabled={isWorking}>
                {isWorking ? "Working..." : "Generate exercise"}
              </button>
            </div>
          </div>

          <div className="learning-panel">
            <h3>History</h3>
            <div className="exercise-history">
              {visibleExercises.map((exercise) => (
                <button
                  className="exercise-history-item"
                  key={exercise.id}
                  type="button"
                  onClick={() => loadExercise(exercise.id)}
                >
                  <strong>{exercise.title}</strong>
                  <span>
                    {exercise.type} · {exercise.topic} · {exercise.difficulty}
                  </span>
                </button>
              ))}
              {exercises.length > visibleExercises.length ? (
                <p className="empty-state">
                  Showing latest {visibleExercises.length} exercises. Use topic generation to continue from recent work.
                </p>
              ) : null}
              {exercises.length === 0 ? (
                <p className="empty-state">No exercises yet. Generate your first one.</p>
              ) : null}
            </div>
          </div>
        </div>

        <div className="learning-column learning-column-wide">
          <div className="learning-panel">
            <h3>Current exercise</h3>
            {activeExercise ? (
              <div className="exercise-detail">
                <div className="exercise-detail-header">
                  <strong>{activeExercise.title}</strong>
                  <span>
                    {activeExercise.type} · {activeExercise.topic} · {activeExercise.difficulty}
                  </span>
                </div>
                <p>{activeExercise.promptMarkdown}</p>
                <div className="exercise-badges">
                  {activeExercise.constraints.reviewMode === true ? (
                    <span className="exercise-badge">review mode</span>
                  ) : null}
                  {activeExercise.tags.map((tag) => (
                    <span className="exercise-badge" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
                {activeExercise.constraints.reviewMode === true ? (
                  <p className="empty-state">
                    This practice intentionally resurfaces a weaker topic from your recent evaluations.
                  </p>
                ) : null}
                <div className="learning-subgrid">
                  <div>
                    <h4>Expected outcomes</h4>
                    <ul className="plain-list">
                      {activeExercise.expectedOutcomes.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4>Hints</h4>
                    <ul className="plain-list">
                      {activeExercise.hints.slice(0, revealedHintCount).map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                    {activeExercise.hints.length === 0 ? <p className="empty-state">Hints disabled.</p> : null}
                    {activeExercise.hints.length > 0 && revealedHintCount === 0 ? (
                      <p className="empty-state">Reveal hints one at a time when you are blocked.</p>
                    ) : null}
                    {activeExercise.hints.length > revealedHintCount ? (
                      <button className="ghost-button" type="button" onClick={revealNextHint}>
                        Reveal next hint
                      </button>
                    ) : null}
                  </div>
                </div>

                <div className="field-grid">
                  <label className="field field-wide">
                    <span>Reasoning</span>
                    <textarea
                      rows={6}
                      value={answerMarkdown}
                      onChange={(event) => setAnswerMarkdown(event.target.value)}
                      placeholder="Explain the approach, edge cases, and trade-offs."
                    />
                  </label>
                  <label className="field field-wide">
                    <span>Code or pseudo-code</span>
                    <textarea
                      rows={6}
                      value={answerCode}
                      onChange={(event) => setAnswerCode(event.target.value)}
                      placeholder="def solve(...):"
                    />
                  </label>
                </div>

                <div className="section-actions">
                  <button
                    className="primary-button"
                    type="button"
                    onClick={handleSubmit}
                    disabled={isWorking || (answerMarkdown.trim().length === 0 && answerCode.trim().length === 0)}
                  >
                    {isWorking ? "Evaluating..." : "Submit and evaluate"}
                  </button>
                </div>
              </div>
            ) : (
              <p className="empty-state">Generate or load an exercise to start practicing.</p>
            )}
          </div>

          <div className="learning-subgrid">
            <div className="learning-panel">
              <h3>Feedback</h3>
              {evaluation ? (
                <>
                  <p className="score-chip">Overall score: {evaluation.overallScore}/10</p>
                  <p>{evaluation.feedbackMarkdown}</p>
                  <h4>Rubric breakdown</h4>
                  <div className="exercise-badges">
                    {Object.entries(evaluation.rubricScores).map(([dimension, score]) => (
                      <span className="exercise-badge" key={dimension}>
                        {dimension.replaceAll("_", " ")}: {score}/10
                      </span>
                    ))}
                  </div>
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
                  <h4>Improvement plan</h4>
                  <ul className="plain-list">
                    {evaluation.improvementActions.map((item) => (
                      <li key={`${item.action}-${item.why}`}>
                        <strong>{item.action}:</strong> {item.why}
                      </li>
                    ))}
                  </ul>
                  <h4>Recommended next topics</h4>
                  <div className="exercise-badges">
                    {evaluation.recommendedNextTopics.map((topic) => (
                      <button className="exercise-badge exercise-badge-button" key={topic} type="button" onClick={() => applyRecommendedTopic(topic)}>
                        {topic}
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <p className="empty-state">Evaluation feedback will appear here after you submit.</p>
              )}
            </div>

            <div className="learning-panel">
              <h3>Weak topics</h3>
              <div className="mastery-list">
                {visibleTopicMastery.map((item) => (
                  <article className="mastery-card" key={item.topic}>
                    <div className="goal-card-topline">
                      <strong>{item.topic}</strong>
                      <span>{item.averageScore.toFixed(1)}/10</span>
                    </div>
                    <p>
                      {item.attemptsCount} attempt{item.attemptsCount === 1 ? "" : "s"} · weakest dimension:{" "}
                      {item.weakestDimension ?? "n/a"}
                    </p>
                  </article>
                ))}
                {topicMastery.length > visibleTopicMastery.length ? (
                  <p className="empty-state">
                    Showing weakest {visibleTopicMastery.length} topics to keep scrolling responsive.
                  </p>
                ) : null}
                {topicMastery.length === 0 ? (
                  <p className="empty-state">Weak-topic tracking will populate after evaluations.</p>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
