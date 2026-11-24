import { Trans, tr } from "../i18n";
import { useState } from "react";
import { useLoad } from "../hooks/useLoad";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { post, Row } from "../services/api";
import {
  ActionForm,
  ActionButton,
  Field,
  Panel,
  Badge,
  Notice,
  Empty,
} from "../components/UI";
import { Heading, CoursePicker, useCourse } from "./Academics";

export function MathAnswer({ text }: { text: string }) {
  return (
    <div className="math-answer">
      {text.split("\n").map((line, i) => (
        <div key={i}>
          {line
            .split(/(\^[0-9]+)/)
            .map((part, j) =>
              part.startsWith("^") ? (
                <sup key={j}>{part.slice(1)}</sup>
              ) : (
                <span key={j}>{part.replaceAll("*", " × ")}</span>
              ),
            )}
        </div>
      ))}
    </div>
  );
}
export function Tutor() {
  const { lang, t } = useI18n(),
    { data, error } = useLoad<Row[]>("/tutor/history"),
    { data: provider } = useLoad<Row>("/tutor/provider-health"),
    [question, setQuestion] = useState(""),
    [status, setStatus] = useState("");
  return (
    <>
      <Heading
        title={tr("AI tutor")}
        description={t(
          "Ask a specific question, solve an expression or continue a conversation.",
        )}
      />
      <Notice>
        {t(
          "Verified symbolic mathematics and topic-aware teaching notes. Local AI is optional. Ask your teacher to check learning advice.",
        )}
      </Notice>
      <Notice error>{error}</Notice>
      <Notice>{status}</Notice>
      <div className="two-columns">
        <Panel title={t("Ask a question")}>
          <ActionForm
            label="Ask tutor"
            onSubmit={async (f) => {
              const submitted=question;
              const r = await post("/tutor/ask", {
                subject: f.get("subject"),
                question,
                language: lang,
                use_local_ai: f.has("use_local_ai"),
              });
              setStatus(t(r.provider_status || r.mode));
              setQuestion(current=>current===submitted?'':current);
            }}
          >
            <Field label="Subject">
              <select name="subject">
                {[
                  "Mathematics",
                  "Biology",
                  "Physics",
                  "Chemistry",
                  "Geography",
                  "History",
                  "English",
                  "Kiswahili",
                ].map((s) => (
                  <option key={s} value={s}>
                    {t(s)}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Ask a question">
              <textarea
                name="question"
                required
                minLength={3}
                maxLength={1500}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder={tr("3x + 9 = 18")}
              />
            </Field>
            <label className="radio-option">
              <input type="checkbox" name="use_local_ai" />
              {t("Use optional local AI")}
            </label>
            <small>
              {t(provider?.reason || "Checking local AI availability")}
            </small>
          </ActionForm>
          <p className="text-sm mt-4">{t("Try a worked example")}</p>
          <div className="actions">
            {[
              "3x + 9 = 18",
              "Differentiate x^3 + 2x",
              "Integrate 2x",
              "Explain calculus",
            ].map((q) => (
              <button
                key={q}
                className="button secondary"
                onClick={() => setQuestion(q)}
              >
                {t(q)}
              </button>
            ))}
          </div>
        </Panel>
        <Panel title={t("Your conversations")}>
          {data?.length ? (
            data.map((m) => (
              <article key={m.id}>
                <div className="chat-message question">
                  <span className="message-meta">
                    {t(m.subject)} · {m.language.toUpperCase()}
                  </span>
                  <p>{m.question}</p>
                </div>
                <div className="chat-message">
                  <Badge>
                    {t(
                      m.source.startsWith("SymPy")
                        ? "Verified mathematics"
                        : m.source.startsWith("Ollama")
                          ? "Local AI generated"
                          : m.source.startsWith("No ")
                            ? "Clarification"
                            : "Teaching passage",
                    )}
                  </Badge>
                  <MathAnswer text={m.answer} />
                  <span className="message-meta">{m.source}</span>
                </div>
              </article>
            ))
          ) : (
            <Empty />
          )}
        </Panel>
      </div>
    </>
  );
}
export function Recommendations() {
  const { user } = useAuth(),
    { t } = useI18n(),
    { data, error } = useLoad<Row[]>("/recommendations"),
    { courses, id, setId } = useCourse(),
    { data: students } = useLoad<Row[]>(
      user?.role === "teacher" && id ? `/courses/${id}/students` : null,
    ),
    teacher = user?.role === "teacher";
  return (
    <>
      <Heading
        title={teacher ? "Review queue" : "Learning pathways"}
        description="Evidence-based next steps, reviewed by an assigned teacher."
      />
      <Notice>
        <Trans
          value={
            " Explainable rules use grades, activity, interests and learning preferences. No validated prediction model is used. Drafts stay hidden from students until teacher approval. "
          }
        />
      </Notice>
      <Notice error>{error}</Notice>
      <Panel title={t("Generate pathway")}>
        <CoursePicker value={id} onChange={setId} courses={courses} />
        {id > 0 && (
          <ActionForm
            label="Generate pathway"
            onSubmit={(f) =>
              post("/recommendations/generate", {
                course_id: id,
                student_id: teacher ? Number(f.get("student_id")) : user?.id,
              })
            }
          >
            {teacher && (
              <Field label="Student">
                <select name="student_id" required defaultValue="">
                  <option value="" disabled>
                    {t("Choose a student")}
                  </option>
                  {students?.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </Field>
            )}
          </ActionForm>
        )}
      </Panel>
      {data?.length ? (
        data.map((r) => (
          <Panel
            key={r.id}
            title={
              teacher ? `${r.student_name} · ${r.course_title}` : r.course_title
            }
            action={<Badge>{r.status}</Badge>}
          >
            <p className="detail-text">{r.content}</p>
            <details>
              <summary className="text-sm cursor-pointer">
                <Trans value={" Why this pathway? · Version "} />
                {r.version}
              </summary>
              <ul className="review-reasons">
                {r.reasons.map((x: string, i: number) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </details>
            {teacher && r.status === "pending_review" && (
              <ActionForm
                label="Save changes"
                className="mt-5"
                onSubmit={(f) =>
                  post(`/recommendations/${r.id}/review`, {
                    decision: f.get("decision"),
                    comment: f.get("comment"),
                  })
                }
              >
                <Field label="Review comment">
                  <textarea name="comment" required minLength={3} />
                </Field>
                <Field label="Decision">
                  <select name="decision">
                    <option value="approved">{t("Approve")}</option>
                    <option value="rejected">{t("Reject")}</option>
                  </select>
                </Field>
              </ActionForm>
            )}
            {teacher && (
              <div className="actions">
                {r.status === "rejected" && (
                  <ActionButton
                    onClick={() => post(`/recommendations/${r.id}/regenerate`)}
                  >
                    {t("Regenerate")}
                  </ActionButton>
                )}
                {["published", "viewed", "rejected"].includes(r.status) && (
                  <ActionButton
                    onClick={() => post(`/recommendations/${r.id}/archive`)}
                  >
                    {t("Archive")}
                  </ActionButton>
                )}
                <ReviewHistory id={r.id} />
              </div>
            )}
            {!teacher && r.status === "published" && (
              <div className="mt-4">
                <ActionButton
                  onClick={() => post(`/recommendations/${r.id}/view`)}
                >
                  {t("Mark as viewed")}
                </ActionButton>
              </div>
            )}
          </Panel>
        ))
      ) : (
        <Empty />
      )}
    </>
  );
}
function ReviewHistory({ id }: { id: number }) {
  const [open, setOpen] = useState(false),
    { data, error } = useLoad<Row[]>(
      open ? `/recommendations/${id}/history` : null,
    );
  return (
    <div>
      <button className="button secondary" onClick={() => setOpen((x) => !x)}>
        <Trans value={" Review history "} />
      </button>
      {open && (
        <>
          <Notice error>{error}</Notice>
          {data?.map((h) => (
            <p key={h.id} className="text-sm mt-3">
              <Trans value={" v"} />
              {h.version} · {h.decision}: {h.comment}
            </p>
          ))}
        </>
      )}
    </div>
  );
}
export function LessonPlans() {
  const { t } = useI18n(),
    { courses, id, setId } = useCourse(),
    [outline, setOutline] = useState(""),
    [topic, setTopic] = useState(""),
    { data, error } = useLoad<Row[]>(
      id ? `/teacher-tools/lessons/${id}` : null,
    );
  return (
    <>
      <Heading
        title={tr("Lesson planning")}
        description="Prepare a structured outline, then adapt it for your learners."
      />
      <Notice>
        <Trans
          value={
            " Premium assistance combines retrieved teaching passages with a lesson template. Teacher review is required. No generative model is connected. "
          }
        />
      </Notice>
      <CoursePicker
        value={id}
        onChange={(n) => {
          setId(n);
          setOutline("");
        }}
        courses={courses}
      />
      <Notice error>{error}</Notice>
      {id > 0 && (
        <Panel title={t("Draft assistance")}>
          <ActionForm
            label="Generate draft"
            onSubmit={async (f) => {
              const v = String(f.get("topic"));
              const r = await post("/teacher-tools/lesson-draft", {
                course_id: id,
                topic: v,
              });
              setTopic(v);
              setOutline(r.outline);
            }}
          >
            <Field label="Topic">
              <input
                name="topic"
                required
                minLength={3}
                placeholder={tr("Linear equations")}
              />
            </Field>
          </ActionForm>
          {outline && (
            <ActionForm
              label="Save reviewed lesson"
              className="mt-6"
              onSubmit={() =>
                post("/teacher-tools/lessons", {
                  course_id: id,
                  topic,
                  outline,
                })
              }
            >
              <Field label="Title">
                <input
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  required
                  minLength={3}
                />
              </Field>
              <Field label="Content">
                <textarea
                  value={outline}
                  onChange={(e) => setOutline(e.target.value)}
                  rows={14}
                  required
                  minLength={20}
                />
              </Field>
              <label className="text-sm">
                <input type="checkbox" required />
                <Trans value={" I reviewed and adapted this lesson. "} />
              </label>
            </ActionForm>
          )}
        </Panel>
      )}
      {data?.map((l) => (
        <Panel key={l.id} title={l.title}>
          <p className="detail-text">{l.outline}</p>
          <Badge>{t("Teacher reviewed")}</Badge>
        </Panel>
      ))}
    </>
  );
}
