import { Trans, tr } from "../i18n";
import { useLoad } from "../hooks/useLoad";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { post, patch, Row } from "../services/api";
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

const deadline = (value: string) =>
  value ? new Date(value).toISOString() : null;
const localDate = (value: string) =>
  value
    ? new Date(
        new Date(value + "Z").getTime() -
          new Date().getTimezoneOffset() * 60000,
      )
        .toISOString()
        .slice(0, 16)
    : "";
const body = (f: FormData) => ({
  title: f.get("title"),
  instructions: f.get("instructions"),
  due_at: deadline(String(f.get("due_at") || "")),
  policy: {
    max_attempts: Number(f.get("max_attempts")),
    allow_resubmission: f.has("allow_resubmission"),
    allow_late: f.has("allow_late"),
    require_feedback: f.has("require_feedback"),
    require_approval: f.has("require_approval"),
    grading_policy: f.get("grading_policy"),
  },
});

function AssignmentFields({ a = {} }: { a?: Row }) {
  const { t } = useI18n();
  return (
    <>
      <Field label="Title">
        <input name="title" defaultValue={a.title} required minLength={2} />
      </Field>
      <Field label="Instructions">
        <textarea
          name="instructions"
          defaultValue={a.instructions}
          required
          minLength={5}
        />
      </Field>
      <div className="form-grid">
        <Field label="Deadline">
          <input
            name="due_at"
            type="datetime-local"
            defaultValue={localDate(a.due_at)}
          />
        </Field>
        <Field label="Maximum attempts">
          <input
            name="max_attempts"
            type="number"
            min={1}
            max={20}
            defaultValue={a.policy?.max_attempts || 1}
            required
          />
        </Field>
      </div>
      <Field label="Official grading policy">
        <select
          name="grading_policy"
          defaultValue={a.policy?.grading_policy || "latest"}
        >
          {["first", "best", "latest", "selected"].map((p) => (
            <option key={p} value={p}>
              {t(p)}
            </option>
          ))}
        </select>
      </Field>
      {[
        "allow_resubmission",
        "allow_late",
        "require_feedback",
        "require_approval",
      ].map((p, i) => (
        <label className="radio-option" key={p}>
          <input
            type="checkbox"
            name={p}
            defaultChecked={a.policy?.[p] || false}
          />
          {t(
            [
              "Allow resubmission",
              "Allow late submissions",
              "Require feedback before resubmission",
              "Require teacher approval",
            ][i],
          )}
        </label>
      ))}
    </>
  );
}

export function AttemptHistory({
  attempts,
  official,
}: {
  attempts: Row[];
  official?: number;
}) {
  const { t } = useI18n();
  return (
    <div className="attempt-history">
      <h3>{t("Attempt history")}</h3>
      {attempts.map((a) => (
        <article key={a.id || a.number} className="attempt-card">
          <div className="panel-heading">
            <strong>
              {t("Attempt")} {a.number}
            </strong>
            <Badge>
              {a.number === official
                ? t("Official score")
                : a.grade
                  ? `${a.grade.score}%`
                  : t("Awaiting feedback")}
            </Badge>
          </div>
          <p className="detail-text">{a.content}</p>
          {a.grade && (
            <>
              <progress
                max="100"
                value={a.grade.score}
                aria-label={`${t("Score")} ${a.grade.score}%`}
              />
              <p>
                {a.grade.score}% · {a.grade.feedback}
              </p>
            </>
          )}
        </article>
      ))}
    </div>
  );
}

function Requests({ id, teacher }: { id: number; teacher: boolean }) {
  const { data, error } = useLoad<Row[]>(
      `/assignments/${id}/resubmission-requests`,
    ),
    { t } = useI18n();
  return (
    <>
      <Notice error>{error}</Notice>
      {data?.map((r) => (
        <div className="attempt-card" key={r.id}>
          <p>
            {r.student_name} · {t("Attempt")} {r.attempt_number} · {t(r.status)}
          </p>
          <p>{r.reason}</p>
          {r.comment && <p>{r.comment}</p>}
          {teacher && r.status === "pending" && (
            <ActionForm
              label="Review request"
              onSubmit={(f) =>
                post(`/resubmission-requests/${r.id}/review`, {
                  decision: f.get("decision"),
                  comment: f.get("comment"),
                  reopen_until: deadline(String(f.get("reopen_until") || "")),
                })
              }
            >
              <Field label="Decision">
                <select name="decision">
                  <option value="approved">{t("Approve")}</option>
                  <option value="rejected">{t("Reject")}</option>
                </select>
              </Field>
              <Field label="Feedback">
                <textarea name="comment" minLength={3} required />
              </Field>
              <Field label="Reopen until">
                <input type="datetime-local" name="reopen_until" />
              </Field>
            </ActionForm>
          )}
        </div>
      ))}
    </>
  );
}

function ReviewAttempts({ a }: { a: Row }) {
  const { data, error } = useLoad<Row[]>(`/assignments/${a.id}/submissions`),
    { data: students } = useLoad<Row[]>(`/courses/${a.course_id}/students`),
    { t } = useI18n();
  return (
    <>
      <Notice error>{error}</Notice>
      {data?.map((s) => (
        <details key={s.id} className="attempt-card">
          <summary>
            {s.student_name} · {t("Official score")}:{" "}
            {s.official ? `${s.official.grade.score}%` : t("Pending")}
          </summary>
          {s.attempts.map((at: Row) => (
            <article className="attempt-card" key={at.number}>
              <h3>
                {t("Attempt")} {at.number}
              </h3>
              <p className="detail-text">{at.content}</p>
              <ActionForm
                label="Record grade"
                onSubmit={(f) =>
                  post(
                    at.id
                      ? `/attempts/${at.id}/grade`
                      : `/submissions/${s.id}/grade`,
                    {
                      score: Number(f.get("score")),
                      feedback: f.get("feedback"),
                    },
                  )
                }
              >
                <Field label="Score">
                  <input
                    name="score"
                    type="number"
                    min={0}
                    max={100}
                    step="0.1"
                    defaultValue={at.grade?.score}
                    required
                  />
                </Field>
                <Field label="Feedback">
                  <textarea
                    name="feedback"
                    defaultValue={at.grade?.feedback}
                    required
                  />
                </Field>
              </ActionForm>
              {a.policy.grading_policy === "selected" && at.grade && at.id && (
                <ActionButton
                  onClick={() => post(`/attempts/${at.id}/select-final`)}
                >
                  {t("Use as official score")}
                </ActionButton>
              )}
            </article>
          ))}
        </details>
      ))}
      <details className="attempt-card">
        <summary>{t("Resubmission requests")}</summary>
        <Requests id={a.id} teacher />
        <ActionForm
          label="Reopen for student"
          onSubmit={(f) =>
            post(`/assignments/${a.id}/reopen`, {
              student_id: Number(f.get("student_id")),
              reason: f.get("reason"),
              reopen_until: deadline(String(f.get("reopen_until"))),
            })
          }
        >
          <Field label="Student">
            <select name="student_id" required>
              {students?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Reason">
            <textarea name="reason" required minLength={3} />
          </Field>
          <Field label="Reopen until">
            <input type="datetime-local" name="reopen_until" required />
          </Field>
        </ActionForm>
      </details>
    </>
  );
}

export function Assignments() {
  const { courses, id, setId, error } = useCourse(),
    { data, error: loadError } = useLoad<Row[]>(
      id ? `/courses/${id}/assignments` : null,
    ),
    { user } = useAuth(),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={tr("Assignments")}
        description={t(
          "Practise, review feedback and improve with each attempt.",
        )}
      />
      <Notice error>{error || loadError}</Notice>
      <CoursePicker courses={courses} value={id} onChange={setId} />
      {data?.map((a) => (
        <Panel
          key={a.id}
          title={a.title}
          action={<Badge>{t(a.submitted ? "Submitted" : "Open")}</Badge>}
        >
          <p className="detail-text">{a.instructions}</p>
          <p>
            {t("Deadline")}:{" "}
            {a.due_at
              ? new Date(a.due_at + "Z").toLocaleString()
              : t("No deadline")}
          </p>
          <p>
            {t("Official grading policy")}: {t(a.policy.grading_policy)} ·{" "}
            {t("Maximum attempts")}: {a.policy.max_attempts}
          </p>
          {user?.role === "student" && (
            <>
              <p>
                {t("Remaining attempts")}: {a.remaining_attempts}
              </p>
              <Notice>
                {a.grade
                  ? `${t("Official score")}: ${a.grade.score}% (${t("Attempt")} ${a.official_attempt})`
                  : t("Official score pending")}
              </Notice>
              {a.attempts.length > 0 && (
                <AttemptHistory
                  attempts={a.attempts}
                  official={a.official_attempt}
                />
              )}
              {a.can_submit ? (
                <ActionForm
                  label={a.submitted ? "Submit another attempt" : "Submit"}
                  onSubmit={(f) =>
                    post(`/assignments/${a.id}/submit`, { body: f.get("body") })
                  }
                >
                  <Field label="Your response">
                    <textarea name="body" required maxLength={10000} />
                  </Field>
                </ActionForm>
              ) : (
                <Notice>{t(a.blocked_reason)}</Notice>
              )}
              {a.submitted && (
                <details className="mt-4">
                  <summary>{t("Resubmission requests")}</summary>
                  <Requests id={a.id} teacher={false} />
                  <ActionForm
                    label="Request resubmission"
                    onSubmit={(f) =>
                      post(`/assignments/${a.id}/resubmission-requests`, {
                        reason: f.get("reason"),
                      })
                    }
                  >
                    <Field label="Reason">
                      <textarea name="reason" required minLength={3} />
                    </Field>
                  </ActionForm>
                </details>
              )}
            </>
          )}
          {user?.role === "teacher" && (
            <>
              <details className="mb-4">
                <summary>{t("Edit assignment")}</summary>
                <ActionForm
                  label="Save changes"
                  onSubmit={(f) => patch(`/assignments/${a.id}`, body(f))}
                >
                  <AssignmentFields a={a} />
                </ActionForm>
              </details>
              <ReviewAttempts a={a} />
            </>
          )}
        </Panel>
      ))}
      {!data?.length && <Empty />}
      {user?.role === "teacher" && id > 0 && (
        <Panel title={t("Create assignment")}>
          <ActionForm
            label="Create assignment"
            onSubmit={(f) => post(`/courses/${id}/assignments`, body(f))}
          >
            <AssignmentFields />
          </ActionForm>
        </Panel>
      )}
    </>
  );
}
