import { Trans, tr } from "../i18n";
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { BookOpen, FileText, Video, Download } from "lucide-react";
import { useLoad } from "../hooks/useLoad";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { api, post, patch, download, Row } from "../services/api";
import {
  ActionForm,
  ActionButton,
  Field,
  Panel,
  Badge,
  Notice,
  Empty,
} from "../components/UI";

export function Heading({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  const { t } = useI18n();
  return (
    <div className="page-heading">
      <div>
        <h1>{t(title)}</h1>
        {description && <p>{t(description)}</p>}
      </div>
    </div>
  );
}
export function CoursePicker({
  value,
  onChange,
  courses,
}: {
  value: number;
  onChange: (v: number) => void;
  courses: Row[];
}) {
  const { t } = useI18n();
  return (
    <div className="toolbar">
      <Field label="Course">
        <select
          value={value || ""}
          onChange={(e) => onChange(Number(e.target.value))}
        >
          <option value="" disabled>
            {t("Course")}
          </option>
          {courses.map((c) => (
            <option value={c.id} key={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </Field>
    </div>
  );
}
export function useCourse() {
  const [params, setParams] = useSearchParams(),
    { data: courses, error } = useLoad<Row[]>("/courses");
  const id = Number(params.get("course")) || courses?.[0]?.id || 0;
  return {
    courses: courses || [],
    id,
    setId: (n: number) => setParams({ course: String(n) }),
    error,
  };
}
function CourseFields({ course = {} }: { course?: Row }) {
  return (
    <>
      <div className="form-grid">
        <Field label="Title">
          <input
            name="title"
            required
            minLength={3}
            defaultValue={course.title}
          />
        </Field>
        <Field label="Subject">
          <input
            name="subject"
            required
            minLength={2}
            defaultValue={course.subject}
            list="subjects"
          />
          <datalist id="subjects">
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
              <option key={s}>{s}</option>
            ))}
          </datalist>
        </Field>
      </div>
      <Field label="Form">
        <select name="form" defaultValue={course.form || "Form 2"}>
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <option key={n}>
              <Trans value={"Form "} />
              {n}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Description">
        <textarea name="description" defaultValue={course.description} />
      </Field>
    </>
  );
}
const courseBody = (f: FormData) => ({
  title: f.get("title"),
  subject: f.get("subject"),
  form: f.get("form"),
  description: f.get("description"),
});
export function Courses() {
  const { user } = useAuth(),
    { t } = useI18n(),
    { data, error } = useLoad<Row[]>("/courses"),
    [query, setQuery] = useState("");
  return (
    <>
      <Heading
        title={user?.role === "teacher" ? "Assigned courses" : "My courses"}
        description="Your subjects, resources and practice, together."
      />
      <Notice error>{error}</Notice>
      <div className="toolbar">
        <Field label="Search courses">
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("Search courses")}
          />
        </Field>
      </div>
      <div className="card-grid">
        {data
          ?.filter((c) =>
            (c.title + " " + c.subject)
              .toLowerCase()
              .includes(query.toLowerCase()),
          )
          .map((c) => (
            <article className="panel course-card" key={c.id}>
              <div className="course-cover">
                <BookOpen size={35} />
                <Badge>{c.form}</Badge>
              </div>
              <small>{c.subject.toUpperCase()}</small>
              <h3>{c.title}</h3>
              <p>{c.description}</p>
              <div className="course-links">
                <Link to={`/app/materials?course=${c.id}`}>
                  {t("Study notes")}
                </Link>
                <Link to={`/app/assignments?course=${c.id}`}>
                  {t("Assignments")}
                </Link>
                <Link to={`/app/quizzes?course=${c.id}`}>{t("Quizzes")}</Link>
              </div>
              {user?.role === "teacher" && (
                <details className="mt-4">
                  <summary className="text-sm cursor-pointer">
                    <Trans value={" Manage course "} />
                  </summary>
                  <ActionForm
                    label="Save changes"
                    className="mt-4"
                    onSubmit={(f) => patch(`/courses/${c.id}`, courseBody(f))}
                  >
                    <CourseFields course={c} />
                  </ActionForm>
                </details>
              )}
            </article>
          ))}
      </div>
      {data?.length === 0 && <Empty />}
      {user?.role === "teacher" && (
        <Panel title={t("Create course")}>
          <ActionForm
            label="Create course"
            onSubmit={(f) => post("/courses", courseBody(f))}
          >
            <CourseFields />
          </ActionForm>
        </Panel>
      )}
    </>
  );
}
export function Materials() {
  const { courses, id, setId, error } = useCourse(),
    { data, error: loadError } = useLoad<Row[]>(
      id ? `/courses/${id}/materials` : null,
    ),
    { user } = useAuth(),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={tr("Learning materials")}
        description="Lightweight teaching notes and resources for your subjects."
      />
      <Notice error>{error || loadError}</Notice>
      <CoursePicker courses={courses} value={id} onChange={setId} />
      {data?.map((m) => (
        <Panel
          key={m.id}
          title={m.title}
          action={
            <Badge>
              {m.kind === "video" ? (
                <Video size={16} />
              ) : (
                <FileText size={16} />
              )}
            </Badge>
          }
        >
          <p className="detail-text">{m.content}</p>
          {user?.role === "student" && (
            <div className="mb-4">
              <ActionButton onClick={() => post(`/materials/${m.id}/study`)}>
                <Trans value={" Mark as studied "} />
              </ActionButton>
            </div>
          )}
          {m.url && (
            <a
              className="button secondary"
              target="_blank"
              rel="noopener noreferrer"
              href={m.url}
            >
              {t("Video")}
              <Trans value={" / resource "} />
            </a>
          )}
          {m.downloadable && (
            <ActionButton
              onClick={() =>
                download(`/materials/${m.id}/download`, "learning-material")
              }
            >
              <Download size={16} />
              {t("Download")}
            </ActionButton>
          )}
        </Panel>
      ))}
      {!data?.length && <Empty />}
      {user?.role === "teacher" && id > 0 && (
        <div className="two-columns">
          <Panel title={t("Add material")}>
            <ActionForm
              label="Add material"
              onSubmit={(f) =>
                post(`/courses/${id}/materials`, {
                  title: f.get("title"),
                  kind: f.get("kind"),
                  content: f.get("content"),
                  url: f.get("url") || null,
                })
              }
            >
              <Field label="Title">
                <input name="title" required minLength={2} />
              </Field>
              <Field label="Content">
                <textarea name="content" />
              </Field>
              <Field label="Video">
                <select name="kind">
                  <option value="notes">
                    <Trans value={"Notes"} />
                  </option>
                  <option value="video">
                    <Trans value={"Video link"} />
                  </option>
                </select>
              </Field>
              <Field label="HTTPS resource URL">
                <input name="url" type="url" placeholder={tr("https://…")} />
              </Field>
            </ActionForm>
          </Panel>
          <Panel title={tr("Upload educational file")}>
            <p className="text-sm">
              <Trans
                value={
                  " PDF, TXT, PNG, JPG or MP4. Maximum 5 MB; downloads require course access. "
                }
              />
            </p>
            <ActionForm
              label="Add material"
              onSubmit={(f) =>
                api(`/courses/${id}/upload`, { method: "POST", body: f })
              }
            >
              <Field label="Title">
                <input name="title" required minLength={2} />
              </Field>
              <Field label="File">
                <input
                  name="file"
                  type="file"
                  accept=".pdf,.txt,.png,.jpg,.mp4"
                  required
                />
              </Field>
            </ActionForm>
          </Panel>
        </div>
      )}
    </>
  );
}
export { Assignments } from "./AssignmentWorkflows";
export { Quizzes } from "./QuizWorkflows";
