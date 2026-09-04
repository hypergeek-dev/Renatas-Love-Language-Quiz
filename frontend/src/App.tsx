import { ArrowLeft, Clipboard, RotateCcw, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { answerQuestion, createSession, getResult, goBack, resetSession } from "./api";
import type { AnswerKey, ResultResponse, SessionResponse } from "./types";
import heroArtwork from "../assets/renata-hero.webp";

type View = "intro" | "quiz" | "results";
const STORAGE_KEY = "renata_session_id";

const iconLabels: Record<string, string> = {
  WORDS: "A handwritten message",
  TIME: "A quiet moonlit cup",
  SERVICE: "Helping hands",
  TOUCH: "Two hands touching",
  GIFTS: "A small keepsake"
};

function DimensionIcon({ kind }: { kind: string }) {
  return (
    <svg className="dimension-icon" viewBox="0 0 64 64" role="img" aria-label={iconLabels[kind]}>
      {kind === "WORDS" && <path d="M14 17h36v24H29l-10 8v-8h-5zM22 26h20M22 33h14" />}
      {kind === "TIME" && <path d="M22 38c-6 0-10-4-10-9s4-9 10-9c4 0 7 2 10 6 3-4 6-6 10-6 6 0 10 4 10 9s-4 9-10 9H22zM32 13v6M45 15l-4 5" />}
      {kind === "SERVICE" && <path d="M16 34l9 9 10-10M29 43l8 5 13-19c2-3-1-8-5-6L33 31M14 23c7-7 15-7 22 0" />}
      {kind === "TOUCH" && <path d="M16 38c8-10 14-12 18-7l3 4M48 26c-6-3-12-1-16 7l-6 12M20 45h28" />}
      {kind === "GIFTS" && <path d="M16 28h32v24H16zM13 22h38v6H13zM32 22v30M25 17c-5-6-13 1-4 5h11M39 17c5-6 13 1 4 5H32" />}
    </svg>
  );
}

function Intro({ onBegin, loading }: { onBegin: () => void; loading: boolean }) {
  return (
    <main className="intro-shell">
      <section className="intro-panel" aria-labelledby="title">
        <div className="intro-art">
          <img
            src={heroArtwork}
            alt="A candlelit rainy window scene with soft bedding, books, and handwritten romantic details."
            loading="eager"
            decoding="async"
          />
        </div>
        <h1 id="title" className="sr-only">Ren&aacute;ta's Love Language Quiz</h1>
        <div className="intro-copy">
          <p className="eyebrow">A softer kind of quiz</p>
          <h2>How do you notice love?</h2>
          <p>
            There isn&apos;t always just one way we want to be loved. It can change with the person, the
            moment, and even the day. So don&apos;t think too hard. Step into each little scene and choose
            the moment that feels closest to your heart.
          </p>
          <button className="primary-action" onClick={onBegin} disabled={loading}>
            <Sparkles aria-hidden="true" size={18} />
            {loading ? "Preparing..." : "Begin"}
          </button>
          <p className="privacy-note">Your answers are only used for this quiz session and are not saved as a personal profile.</p>
        </div>
      </section>
    </main>
  );
}

function Quiz({
  session,
  pending,
  onAnswer,
  onBack
}: {
  session: SessionResponse;
  pending: boolean;
  onAnswer: (answer: AnswerKey) => void;
  onBack: () => void;
}) {
  const question = session.question;
  const progress = ((session.current_question - 1) / session.total_questions) * 100;
  if (!question) return null;
  const selected = session.answers[String(question.id)];
  return (
    <main className="quiz-shell">
      <section className="quiz-frame" aria-labelledby="question-count">
        <div className="progress-row">
          <button className="ghost-button" onClick={onBack} disabled={pending}>
            <ArrowLeft aria-hidden="true" size={18} />
            Back
          </button>
          <p id="question-count">Question {session.current_question} of {session.total_questions}</p>
        </div>
        <div className="progress-track" aria-hidden="true"><span style={{ width: `${progress}%` }} /></div>
        <article className="scene-card" key={question.id}>
          <div className="scene-copy">
            <p className="scene-text">{question.scene}</p>
            {question.prompt && <h2>{question.prompt}</h2>}
          </div>
          <div className="choice-grid" role="group" aria-label="Answer choices">
            {(["A", "B"] as AnswerKey[]).map((answer) => (
              <button
                key={answer}
                className={`choice ${selected === answer ? "selected" : ""}`}
                disabled={pending}
                onClick={() => onAnswer(answer)}
              >
                <span>{answer}</span>
                {question.choices[answer]}
              </button>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}

function Results({ result, onRestart }: { result: ResultResponse; onRestart: () => void }) {
  const copyText = useMemo(
    () => [
      "Renáta's Love Language Quiz",
      `Primary tendency: ${result.primary.name} (${result.primary.percentage}%)`,
      `Secondary tendency: ${result.secondary.name} (${result.secondary.percentage}%)`,
      ...result.dimensions.map((dimension) => `${dimension.name}: ${dimension.percentage}%`),
      result.summary
    ].join("\n"),
    [result]
  );

  return (
    <main className="results-shell">
      <section className="results-layout">
        <div className="result-card" aria-label="Shareable result card">
          <img className="result-atmosphere" src={heroArtwork} alt="" aria-hidden="true" loading="lazy" decoding="async" />
          <p className="eyebrow">Renáta's Love Language Quiz</p>
          <h1>{result.profile_shape} profile</h1>
          <p>{result.summary}</p>
          <div className="tendency-row">
            <strong>Primary: {result.primary.name}</strong>
            <strong>Secondary: {result.secondary.name}</strong>
          </div>
          <div className="bars" aria-label="Result percentages">
            {result.dimensions.map((dimension) => (
              <div className="bar-row" key={dimension.key}>
                <DimensionIcon kind={dimension.key} />
                <div>
                  <div className="bar-label"><span>{dimension.name}</span><span>{dimension.percentage}%</span></div>
                  <div className="bar-track"><span style={{ width: `${dimension.percentage}%` }} /></div>
                </div>
              </div>
            ))}
          </div>
          <div className="result-actions">
            <button className="primary-action" onClick={() => navigator.clipboard.writeText(copyText)}>
              <Clipboard aria-hidden="true" size={18} />
              Copy result
            </button>
            <button className="ghost-button" onClick={onRestart}>
              <RotateCcw aria-hidden="true" size={18} />
              Start again
            </button>
          </div>
        </div>
        <div className="interpretations">
          {result.dimensions.map((dimension) => (
            <article key={dimension.key}>
              <DimensionIcon kind={dimension.key} />
              <div>
                <h2>{dimension.name}</h2>
                <p>{dimension.interpretation}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState<View>("intro");
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [result, setResult] = useState<ResultResponse | null>(null);
  const [pending, setPending] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const previousSessionId = sessionStorage.getItem(STORAGE_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
    createSession(previousSessionId)
      .then((created) => {
        sessionStorage.setItem(STORAGE_KEY, created.id);
        setSession(created);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setPending(false));
  }, []);

  async function handleAnswer(answer: AnswerKey) {
    if (!session?.question) return;
    setPending(true);
    try {
      const next = await answerQuestion(session.id, session.question.id, answer);
      setSession(next);
      if (next.completed) {
        const quizResult = await getResult(next.id);
        setResult(quizResult);
        setView("results");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setPending(false);
    }
  }

  async function handleBack() {
    if (!session) return;
    if (session.current_question === 1) {
      setView("intro");
      return;
    }
    setPending(true);
    try {
      setSession(await goBack(session.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setPending(false);
    }
  }

  async function handleRestart() {
    if (!session) return;
    setPending(true);
    try {
      const reset = await resetSession(session.id);
      setSession(reset);
      setResult(null);
      setView("intro");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="app">
      {error && <div className="error" role="alert">{error}</div>}
      {view === "intro" && <Intro loading={pending} onBegin={() => setView("quiz")} />}
      {view === "quiz" && session && <Quiz session={session} pending={pending} onAnswer={handleAnswer} onBack={handleBack} />}
      {view === "results" && result && <Results result={result} onRestart={handleRestart} />}
    </div>
  );
}
