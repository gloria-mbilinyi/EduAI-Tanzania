import { Trans, tr } from "../i18n";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { useLoad } from "../hooks/useLoad";
import { download, patch, Row } from "../services/api";
import {
  ActionForm,
  ActionButton,
  Field,
  Panel,
  Badge,
  Notice,
  Empty,
} from "../components/UI";
import { Heading, useCourse, CoursePicker } from "./Academics";
import { PerformanceChart } from "./Overview";

export function Performance() {
  const { user } = useAuth(),
    { t } = useI18n(),
    [params, setParams] = useSearchParams(),
    { courses, id, setId } = useCourse(),
    { data: links } = useLoad<Row[]>(
      user?.role === "parent" ? "/parent/links" : null,
    ),
    { data: roster } = useLoad<Row[]>(
      user?.role === "teacher" && id ? `/courses/${id}/students` : null,
    );
  const choices =
    user?.role === "parent"
      ? links
          ?.filter((x) => x.status === "approved")
          .map((x) => ({ id: x.student_id, name: x.student_name }))
      : roster;
  const sid =
    user?.role === "student"
      ? user.id
      : Number(params.get("student")) || choices?.[0]?.id;
  const { data, error } = useLoad(sid ? `/students/${sid}/performance` : null);
  return (
    <>
      <Heading
        title={tr("Performance")}
        description="Recorded assessments and explainable next steps."
      />
      {user?.role === "teacher" && (
        <CoursePicker courses={courses} value={id} onChange={setId} />
      )}
      <div className="toolbar">
        {user?.role !== "student" && (
          <Field label="Student">
            <select
              value={sid || ""}
              onChange={(e) =>
                setParams({
                  student: e.target.value,
                  ...(id ? { course: String(id) } : {}),
                })
              }
            >
              {choices?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </Field>
        )}
        {sid && (
          <>
            <ActionButton
              onClick={() =>
                download(`/students/${sid}/report.csv`, "progress-report.csv")
              }
            >
              {t("Download report")}
            </ActionButton>
            <button className="button secondary" onClick={() => window.print()}>
              {t("Print report")}
            </button>
          </>
        )}
      </div>
      <Notice error>{error}</Notice>
      {data ? (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">{data.name}</div>
              <strong className="stat-value">
                {data.average !== null ? `${data.average}%` : "—"}
              </strong>
              <div className="stat-note">{t("Average score")}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">
                <Trans value={"Graded assessments"} />
              </div>
              <strong className="stat-value">{data.graded_assessments}</strong>
              <div className="stat-note">
                <Trans value={"Persisted results"} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">
                <Trans value={"Recorded learning risk"} />
              </div>
              <Badge>{data.risk.level}</Badge>
              <div className="stat-note">
                <Trans value={"Explainable rule baseline"} />
              </div>
            </div>
          </div>
          <div className="two-columns">
            <Panel title={t("Performance")}>
              <PerformanceChart courses={data.courses} />
            </Panel>
            <Panel title={tr("Learning evidence")}>
              <p>{data.summary}</p>
              <ul className="review-reasons">
                {data.risk.reasons.map((r: string, i: number) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
              <small>{data.risk.mode}</small>
            </Panel>
          </div>
          {data.courses.map((c: Row) => (
            <Panel key={c.course_id} title={c.title}>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>
                        <Trans value={"Assessment"} />
                      </th>
                      <th>{t("Score")}</th>
                      <th>{t("Feedback")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {c.results.map((r: Row, i: number) => (
                      <tr key={i}>
                        <td>{r.title}</td>
                        <td>{r.score}%</td>
                        <td>{r.feedback}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {!c.results.length && <Empty />}
            </Panel>
          ))}
        </>
      ) : (
        !error && <Empty />
      )}
    </>
  );
}
export function Students() {
  const { t } = useI18n(),
    { courses, id, setId } = useCourse(),
    { data, error } = useLoad<Row[]>(id ? `/courses/${id}/students` : null);
  return (
    <>
      <Heading
        title={tr("Students")}
        description="Students enrolled in your assigned courses."
      />
      <CoursePicker value={id} onChange={setId} courses={courses} />
      <Notice error>{error}</Notice>
      <Panel>
        {data?.map((s) => (
          <div key={s.id} className="course-row">
            <div className="course-row-content">
              <h3>{s.name}</h3>
              <small>
                {t("Student ID")}: {s.id}
              </small>
            </div>
            <Link
              className="button secondary"
              to={`/app/performance?course=${id}&student=${s.id}`}
            >
              {t("View report")}
            </Link>
            <Link to={`/app/messages?student=${s.id}`}>{t("Messages")}</Link>
          </div>
        ))}
        {!data?.length && <Empty />}
      </Panel>
    </>
  );
}
export function Profile() {
  const { user, update } = useAuth(),
    { t } = useI18n(),
    { data, error } = useLoad("/me");
  return (
    <>
      <Heading
        title={tr("My profile")}
        description="Keep your learning preferences and personal details up to date."
      />
      <Notice error>{error}</Notice>
      {data && (
        <Panel title={user?.name}>
          <ActionForm
            label="Save changes"
            onSubmit={async (f) => {
              const r = await patch("/me", {
                name: f.get("name"),
                language: f.get("language"),
                interests: f.get("interests") || "Science",
                preference: f.get("preference") || "reading",
              });
              update(r);
            }}
          >
            <Field label="Full name">
              <input
                name="name"
                required
                minLength={2}
                defaultValue={data.name}
              />
            </Field>
            <Field label="Language">
              <select name="language" defaultValue={data.language}>
                <option value="en">
                  <Trans value={"English"} />
                </option>
                <option value="sw">
                  <Trans value={"Kiswahili"} />
                </option>
              </select>
            </Field>
            {user?.role === "student" && (
              <>
                <Field label="Interests">
                  <input
                    name="interests"
                    maxLength={200}
                    defaultValue={data.profile.interests}
                  />
                </Field>
                <Field label="Learning preference">
                  <select
                    name="preference"
                    defaultValue={data.profile.preference}
                  >
                    <option value="reading">{t("Reading")}</option>
                    <option value="video">{t("Video")}</option>
                    <option value="practice">{t("Practice")}</option>
                  </select>
                </Field>
              </>
            )}
            <p className="text-sm">
              {data.email}
              <Trans value={" · School ID "} />
              {data.school_id}
              <Trans
                value={
                  ". Contact your school administrator for account changes. "
                }
              />
            </p>
          </ActionForm>
        </Panel>
      )}
    </>
  );
}
