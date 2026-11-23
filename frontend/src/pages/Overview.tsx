import { Link } from "react-router-dom";
import {
  BookOpen,
  ChartNoAxesCombined,
  ClipboardCheck,
  Activity,
  Sparkles,
  CalendarDays,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { useLoad } from "../hooks/useLoad";
import { Panel, Badge, Notice, Empty } from "../components/UI";
import { Row } from "../services/api";

export function PerformanceChart({ courses }: { courses: Row[] }) {
  return (
    <div
      className="chart-container"
      aria-label="Average recorded score by subject"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={courses.filter((c) => c.average !== null)}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 5"
            vertical={false}
            stroke="#e7eee8"
          />
          <XAxis
            dataKey="subject"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#667c72" }}
          />
          <YAxis
            domain={[0, 100]}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#667c72" }}
          />
          <Tooltip
            formatter={(v) => [`${v}%`, "Average score"]}
            cursor={{ fill: "#f4f8f5" }}
          />
          <Bar dataKey="average" radius={[5, 5, 0, 0]} maxBarSize={40}>
            {courses
              .filter((c) => c.average !== null)
              .map((_, i) => (
                <Cell key={i} fill={i % 2 ? "#d6b46b" : "#398d70"} />
              ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
function Stat({
  label,
  value,
  note,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  note: string;
  icon: typeof BookOpen;
}) {
  return (
    <article className="stat-card">
      <div className="stat-label">
        {label}
        <Icon size={18} />
      </div>
      <strong className="stat-value">{value}</strong>
      <div className="stat-note">{note}</div>
    </article>
  );
}
export function Overview() {
  const { user } = useAuth(),
    { t } = useI18n(),
    { data: courses, error } = useLoad<Row[]>("/courses"),
    { data: links } = useLoad<Row[]>(
      user?.role === "parent" ? "/parent/links" : null,
    );
  const studentId =
    user?.role === "student"
      ? user.id
      : links?.find((x) => x.status === "approved")?.student_id;
  const { data: perf } = useLoad(
      studentId ? `/students/${studentId}/performance` : null,
    ),
    { data: school } = useLoad(
      user?.role === "admin" ? "/admin/reports" : null,
    ),
    { data: recs } = useLoad<Row[]>(
      user?.role === "teacher" || user?.role === "student"
        ? "/recommendations"
        : null,
    ),
    { data: notifications } = useLoad<Row[]>("/notifications");
  const student = user?.role === "student",
    teacher = user?.role === "teacher",
    admin = user?.role === "admin";
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">YOUR EDUCATION WORKSPACE</span>
          <h1>
            {t("Welcome back")}, {user?.name.split(" ")[0]}.
          </h1>
          <p>
            {t("Your learning at a glance")} ·{" "}
            {new Intl.DateTimeFormat(undefined, {
              day: "numeric",
              month: "long",
              year: "numeric",
            }).format(new Date())}
          </p>
        </div>
        <Badge>{t("Academic demonstration")}</Badge>
      </div>
      <Notice error>{error}</Notice>
      <section className="welcome-banner">
        <div>
          <span className="eyebrow">
            <Sparkles size={14} />{" "}
            {teacher
              ? "TEACH WITH PURPOSE"
              : admin
                ? "A CONNECTED SCHOOL"
                : "ROOM TO GROW"}
          </span>
          <h2>{t("A little progress, every day.")}</h2>
          <p>
            {teacher
              ? "Turn learning evidence into useful next steps. Review pathways and prepare your next lesson."
              : admin
                ? "Manage your school community with clear records, verified access and useful academic evidence."
                : "Your notes, practice and teacher-reviewed guidance are together in one place. Take the next step at your own pace."}
          </p>
          <Link
            className="button small"
            to={
              teacher
                ? "/app/recommendations"
                : admin
                  ? "/app/reports"
                  : student
                    ? "/app/courses"
                    : "/app/performance"
            }
          >
            {t(
              teacher
                ? "Review queue"
                : admin
                  ? "View report"
                  : "Continue learning",
            )}
          </Link>
        </div>
        <svg className="banner-art" viewBox="0 0 180 140" aria-hidden="true">
          <circle cx="93" cy="70" r="61" fill="#d5e6d8" />
          <path d="M25 80L125 55L154 74L54 101Z" fill="#d3a54c" />
          <path d="M25 80V95L54 116L154 89V74L54 101Z" fill="#f3d48a" />
          <path d="M40 55L122 36L146 52L64 74Z" fill="#0d6851" />
          <path d="M40 55V67L64 86L146 64V52L64 74Z" fill="#3e987b" />
          <path
            d="M99 35V14M99 26C77 27 76 10 78 7C94 7 103 15 99 26M100 21C116 21 124 9 121 3C108 3 99 11 100 21"
            fill="#368867"
            stroke="#368867"
            strokeWidth="3"
          />
        </svg>
      </section>
      <div className="stats-grid">
        <Stat
          label={t(admin ? "Users" : "My courses")}
          value={admin ? (school?.users ?? "—") : (courses?.length ?? "—")}
          note={admin ? "In your school" : "Available in your workspace"}
          icon={BookOpen}
        />
        <Stat
          label={t(admin ? "School average" : "Average score")}
          value={
            (admin ? school?.school_average : perf?.average) != null
              ? `${admin ? school?.school_average : perf?.average}%`
              : "—"
          }
          note="From persisted graded results"
          icon={ChartNoAxesCombined}
        />
        <Stat
          label={t(teacher ? "Pending review" : "Approved pathways")}
          value={
            teacher
              ? (recs?.filter((r) => r.status === "pending_review").length ?? 0)
              : student
                ? (recs?.length ?? 0)
                : admin
                  ? (school?.students?.length ?? 0)
                  : (links?.filter((x) => x.status === "approved").length ?? 0)
          }
          note={
            teacher
              ? "Awaiting your decision"
              : admin
                ? "Enrolled students"
                : student
                  ? "Ready for your next step"
                  : "Approved student links"
          }
          icon={ClipboardCheck}
        />
        <Stat
          label={t("Learning activity")}
          value={
            admin
              ? (school?.learning_activities ?? 0)
              : (perf?.courses?.reduce(
                  (n: number, c: Row) => n + c.activities_30d,
                  0,
                ) ?? "—")
          }
          note="Recorded activity in 30 days"
          icon={Activity}
        />
      </div>
      <div className="dashboard-grid">
        <div>
          <Panel
            title={t(
              student || (!teacher && !admin)
                ? "Performance"
                : "Assigned courses",
            )}
            action={
              <Link
                to={
                  teacher
                    ? "/app/courses"
                    : admin
                      ? "/app/reports"
                      : "/app/performance"
                }
                className="text-link"
              >
                {t("View report")}
              </Link>
            }
          >
            {perf?.courses?.length ? (
              <PerformanceChart courses={perf.courses} />
            ) : admin ? (
              <p>{school?.method}</p>
            ) : courses?.length ? (
              courses.slice(0, 3).map((c) => (
                <div className="course-row" key={c.id}>
                  <span className="subject-icon">
                    <BookOpen size={20} />
                  </span>
                  <div className="course-row-content">
                    <h3>{c.title}</h3>
                    <small>
                      {c.subject} · {c.form}
                    </small>
                  </div>
                  <Link to={`/app/materials?course=${c.id}`}>{t("Read")}</Link>
                </div>
              ))
            ) : (
              <Empty />
            )}
          </Panel>
          <Panel
            title={t("My courses")}
            action={<Link to="/app/courses">{t("View courses")}</Link>}
          >
            {courses?.length ? (
              courses.slice(0, 3).map((c) => (
                <div className="course-row" key={c.id}>
                  <span className="subject-icon">
                    <BookOpen size={20} />
                  </span>
                  <div className="course-row-content">
                    <h3>{c.title}</h3>
                    <small>
                      {c.subject} · {c.form}
                    </small>
                  </div>
                  <Badge>{c.form}</Badge>
                </div>
              ))
            ) : (
              <Empty />
            )}
          </Panel>
        </div>
        <div>
          <Panel title={t("Your next steps")}>
            <div className="course-row">
              <span className="subject-icon">
                <CalendarDays size={19} />
              </span>
              <div className="course-row-content">
                <h3>
                  {teacher
                    ? "Review learning pathways"
                    : admin
                      ? "Review school reports"
                      : "Make time for practice"}
                </h3>
                <small>
                  {teacher
                    ? "Check the evidence before publishing."
                    : admin
                      ? "Follow up on students needing support."
                      : "A short daily session builds confidence."}
                </small>
              </div>
            </div>
            {perf?.risk && (
              <>
                <p className="mt-4">
                  Recorded learning risk <Badge>{perf.risk.level}</Badge>
                </p>
                <p className="text-sm">{perf.risk.reasons[0]}</p>
                <small>
                  Explainable baseline. Offline study is not captured.
                </small>
              </>
            )}
          </Panel>
          <Panel title={t("Notifications")}>
            {notifications?.length ? (
              notifications.slice(0, 3).map((n) => (
                <article className="course-row" key={n.id}>
                  <div>
                    <h3>{n.title}</h3>
                    <p className="text-sm mb-0">{n.body}</p>
                  </div>
                </article>
              ))
            ) : (
              <Empty />
            )}
            <Link to="/app/notifications" className="inline-block mt-4 text-sm">
              {t("Notifications")}
            </Link>
          </Panel>
        </div>
      </div>
    </>
  );
}
