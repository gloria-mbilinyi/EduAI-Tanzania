import { useState } from "react";
import { useLoad } from "../hooks/useLoad";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { post, Row } from "../services/api";
import {
  ActionForm,
  Field,
  Panel,
  Badge,
  Notice,
  Empty,
} from "../components/UI";
import { Heading, CoursePicker, useCourse } from "./Academics";

function QuizAttempt({ id }: { id: number }) {
  const { data, error } = useLoad(`/quizzes/${id}`),
    [answers, setAnswers] = useState<Record<number, number | string>>({}),
    [result, setResult] = useState<Row | null>(null),
    { t } = useI18n();
  return (
    <>
      <Notice error>{error}</Notice>
      {result ? (
        <Notice>
          {result.score === null
            ? t("Awaiting teacher grading")
            : `${result.score}%`}{" "}
          · {result.feedback.map((p: Row) => p.explanation).join("\n")}
        </Notice>
      ) : (
        <ActionForm
          label="Submit answers"
          onSubmit={async () =>
            setResult(await post(`/quizzes/${id}/attempt`, { answers }))
          }
        >
          {data?.questions.map((q: Row, i: number) => (
            <fieldset key={q.id}>
              <legend>
                {i + 1}. {q.prompt}
              </legend>
              {["numerical", "short_answer"].includes(q.kind) ? (
                <Field
                  label={
                    q.kind === "numerical"
                      ? "Numerical answer"
                      : "Your response"
                  }
                >
                  <textarea
                    required
                    maxLength={2000}
                    onChange={(e) =>
                      setAnswers((a) => ({ ...a, [q.id]: e.target.value }))
                    }
                  />
                </Field>
              ) : (
                q.options.map((o: string, n: number) => (
                  <label className="radio-option" key={n}>
                    <input
                      type="radio"
                      name={`question-${q.id}`}
                      required
                      onChange={() => setAnswers((a) => ({ ...a, [q.id]: n }))}
                    />
                    {o}
                  </label>
                ))
              )}
            </fieldset>
          ))}
        </ActionForm>
      )}
    </>
  );
}

function QuizReview({ id, status }: { id: number; status: string }) {
  const { data, error } = useLoad(`/quizzes/${id}`),
    { data: subs } = useLoad<Row[]>(`/quizzes/${id}/submissions`),
    { t } = useI18n();
  return (
    <details>
      <summary>{t("Review questions and submissions")}</summary>
      <Notice error>{error}</Notice>
      {data?.questions.map((q: Row) => (
        <div className="attempt-card" key={q.id}>
          <h3>{q.prompt}</h3>
          <p>
            {t(q.kind)} · {q.answer || q.options[q.correct_index]}
          </p>
          <p>{q.explanation}</p>
        </div>
      ))}
      {status === "draft" && (
        <ActionForm
          label="Publish reviewed quiz"
          onSubmit={() => post(`/quizzes/${id}/publish`, { reviewed: true })}
        >
          <label className="radio-option">
            <input type="checkbox" required />
            {t("I reviewed the questions and answer keys.")}
          </label>
        </ActionForm>
      )}
      {subs?.map((s) => (
        <div key={s.id} className="attempt-card">
          <h3>
            {s.student_name} ·{" "}
            {s.grade ? `${s.grade.score}%` : t("Awaiting teacher grading")}
          </h3>
          {s.parts.map((p: Row) => (
            <p key={p.question_id}>
              {p.prompt}: {String(s.answers[p.question_id])}
            </p>
          ))}
          {!s.grade && s.parts.some((p: Row) => p.kind === "short_answer") && (
            <ActionForm
              label="Record grade"
              onSubmit={(f) =>
                post(`/quiz-submissions/${s.id}/grade`, {
                  feedback: f.get("feedback"),
                  marks: Object.fromEntries(
                    s.parts
                      .filter((p: Row) => p.kind === "short_answer")
                      .map((p: Row) => [
                        p.question_id,
                        Number(f.get(`mark-${p.question_id}`)),
                      ]),
                  ),
                })
              }
            >
              {s.parts
                .filter((p: Row) => p.kind === "short_answer")
                .map((p: Row) => (
                  <Field label={p.prompt} key={p.question_id}>
                    <input
                      type="number"
                      name={`mark-${p.question_id}`}
                      min={0}
                      max={100}
                      step="0.1"
                      required
                    />
                  </Field>
                ))}
              <Field label="Feedback">
                <textarea name="feedback" required minLength={3} />
              </Field>
            </ActionForm>
          )}
        </div>
      ))}
    </details>
  );
}

function QuizEditor({ courseId }: { courseId: number }) {
  const { t, lang } = useI18n(),
    [questions, setQuestions] = useState<Row[]>([]),
    [mode, setMode] = useState(""),
    [warning, setWarning] = useState("");
  const change = (i: number, k: string, value: unknown) =>
    setQuestions((q) =>
      q.map((row, n) => (n === i ? { ...row, [k]: value } : row)),
    );
  return (
    <Panel title={t("Draft assistance")}>
      <p>
        {t(
          "Review every generated question and answer key. Only an assigned teacher can publish or grade short answers.",
        )}
      </p>
      <ActionForm
        label="Generate draft"
        onSubmit={async (f) => {
          const r = await post("/teacher-tools/quiz-draft", {
            course_id: courseId,
            topic: f.get("topic"),
            objective: f.get("objective"),
            difficulty: f.get("difficulty"),
            count: Number(f.get("count")),
            kind: f.get("kind"),
            language: f.get("language"),
            use_local_ai: f.has("use_local_ai"),
          });
          setQuestions(r.questions);
          setMode(r.mode);
          setWarning(r.warning);
        }}
      >
        <Field label="Topic">
          <input name="topic" required minLength={3} />
        </Field>
        <Field label="Learning objective">
          <input name="objective" required minLength={5} />
        </Field>
        <div className="form-grid">
          <Field label="Difficulty">
            <select name="difficulty">
              {["easy", "medium", "hard"].map((s) => (
                <option key={s} value={s}>
                  {t(s)}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Number of questions">
            <input
              name="count"
              type="number"
              min={1}
              max={20}
              defaultValue={3}
              required
            />
          </Field>
        </div>
        <Field label="Question type">
          <select name="kind">
            {["mcq", "true_false", "numerical", "short_answer"].map((s) => (
              <option key={s} value={s}>
                {t(s)}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Language">
          <select name="language" defaultValue={lang}>
            <option value="en">English</option>
            <option value="sw">Kiswahili</option>
          </select>
        </Field>
        <label className="radio-option">
          <input type="checkbox" name="use_local_ai" />
          {t("Use optional local AI")}
        </label>
      </ActionForm>
      <Notice>{t(mode)}</Notice>
      <Notice>{t(warning)}</Notice>
      <ActionForm
        label="Save reviewed quiz"
        onSubmit={(f) =>
          post(`/courses/${courseId}/quizzes`, {
            title: f.get("title"),
            status: f.get("status"),
            questions,
            reviewed: true,
          })
        }
      >
        <Field label="Title">
          <input name="title" required minLength={2} />
        </Field>
        {questions.map((q, i) => (
          <div key={i} className="attempt-card">
            <h3>
              {t("Question")} {i + 1} · {t(q.kind)}
            </h3>
            <Field label="Question">
              <textarea
                value={q.prompt}
                onChange={(e) => change(i, "prompt", e.target.value)}
                required
                minLength={5}
              />
            </Field>
            {["mcq", "true_false"].includes(q.kind) ? (
              <>
                <Field label="Options one per line">
                  <textarea
                    value={q.options.join("\n")}
                    onChange={(e) =>
                      change(i, "options", e.target.value.split("\n"))
                    }
                    required
                  />
                </Field>
                <Field label="Correct option">
                  <select
                    value={q.correct_index}
                    onChange={(e) =>
                      change(i, "correct_index", Number(e.target.value))
                    }
                  >
                    {q.options.map((o: string, n: number) => (
                      <option key={n} value={n}>
                        {n + 1}. {o}
                      </option>
                    ))}
                  </select>
                </Field>
              </>
            ) : (
              <Field
                label={
                  q.kind === "numerical"
                    ? "Numerical answer"
                    : "Reviewed answer rubric"
                }
              >
                <textarea
                  value={q.answer}
                  onChange={(e) => change(i, "answer", e.target.value)}
                  required
                />
              </Field>
            )}
            <Field label="Explanation">
              <textarea
                value={q.explanation}
                onChange={(e) => change(i, "explanation", e.target.value)}
                required
                minLength={2}
              />
            </Field>
            <button
              type="button"
              className="button secondary"
              onClick={() =>
                setQuestions((rows) => rows.filter((_, n) => n !== i))
              }
            >
              {t("Remove question")}
            </button>
          </div>
        ))}
        <Field label="Add question type">
          <select
            id="new-question-kind"
            onChange={() => {}}
            defaultValue="mcq"
            name="new_kind"
          >
            {["mcq", "true_false", "numerical", "short_answer"].map((k) => (
              <option value={k} key={k}>
                {t(k)}
              </option>
            ))}
          </select>
        </Field>
        <button
          type="button"
          className="button secondary"
          onClick={(e) => {
            const select = e.currentTarget.form?.elements.namedItem(
              "new_kind",
            ) as HTMLSelectElement;
            const kind = select.value;
            setQuestions((rows) => [
              ...rows,
              {
                prompt: "",
                kind,
                options:
                  kind === "true_false"
                    ? ["True", "False"]
                    : kind === "mcq"
                      ? ["", ""]
                      : [],
                correct_index: 0,
                answer: "",
                explanation: "",
                language: lang,
              },
            ]);
          }}
        >
          {t("Add question")}
        </button>
        <Field label="Publication">
          <select name="status">
            <option value="draft">{t("Draft")}</option>
            <option value="published">
              {t("Published after teacher review")}
            </option>
          </select>
        </Field>
        <label className="radio-option">
          <input type="checkbox" required />
          {t("I reviewed the questions and answer keys.")}
        </label>
      </ActionForm>
    </Panel>
  );
}

export function Quizzes() {
  const { courses, id, setId, error } = useCourse(),
    { data, error: loadError } = useLoad<Row[]>(
      id ? `/courses/${id}/quizzes` : null,
    ),
    { user } = useAuth(),
    { t } = useI18n(),
    [selected, setSelected] = useState<number | null>(null);
  return (
    <>
      <Heading
        title="Quizzes"
        description={t(
          "Objective answers are checked securely. Written reasoning is graded by your teacher.",
        )}
      />
      <Notice error>{error || loadError}</Notice>
      <CoursePicker
        courses={courses}
        value={id}
        onChange={(n) => {
          setId(n);
          setSelected(null);
        }}
      />
      {data?.map((q) => (
        <Panel
          key={q.id}
          title={q.title}
          action={<Badge>{t(q.attempted ? "Completed" : q.status)}</Badge>}
        >
          {user?.role === "student" && !q.attempted && selected !== q.id && (
            <button
              className="button secondary"
              onClick={() => setSelected(q.id)}
            >
              {t("Start quiz")}
            </button>
          )}
          {selected === q.id && <QuizAttempt id={q.id} />}
          {user?.role === "teacher" && (
            <QuizReview id={q.id} status={q.status} />
          )}
        </Panel>
      ))}
      {!data?.length && <Empty />}
      {user?.role === "teacher" && id > 0 && (
        <QuizEditor key={id} courseId={id} />
      )}
    </>
  );
}
