import { Trans, tr } from "../i18n";
import { ReactNode } from "react";
import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { useLoad } from "../hooks/useLoad";
import { api, post, patch, Row } from "../services/api";
import {
  ActionForm,
  ActionButton,
  Field,
  Panel,
  Badge,
  Notice,
  Empty,
} from "../components/UI";
import { Heading } from "./Academics";

function Table({
  rows,
  columns,
}: {
  rows: Row[] | null;
  columns: [string, (row: Row) => ReactNode][];
}) {
  return rows?.length ? (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map(([label]) => (
              <th key={label}>
                <Trans value={label} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.id ?? i}>
              {columns.map(([label, cell]) => (
                <td key={label}>{cell(r)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ) : (
    <Empty />
  );
}
export function School() {
  const { data, error } = useLoad("/admin/school"),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={tr("School")}
        description="Manage the registered school within your administrative scope."
      />
      <Notice error>{error}</Notice>
      {data && (
        <Panel title={data.name}>
          <ActionForm
            label="Update school"
            onSubmit={(f) =>
              patch("/admin/school", {
                name: f.get("name"),
                region: f.get("region"),
              })
            }
          >
            <Field label="School">
              <input
                name="name"
                required
                minLength={3}
                defaultValue={data.name}
              />
            </Field>
            <Field label="Region">
              <input
                name="region"
                required
                minLength={2}
                defaultValue={data.region}
              />
            </Field>
            <Badge>{t(data.active ? "Active" : "Pending")}</Badge>
          </ActionForm>
        </Panel>
      )}
    </>
  );
}
export function Users() {
  const { user } = useAuth(),
    { t } = useI18n(),
    { data, error } = useLoad<Row[]>("/admin/users");
  return (
    <>
      <Heading
        title={tr("Users")}
        description="Manage school accounts and activate verified teachers."
      />
      <Notice error>{error}</Notice>
      <Panel>
        <Table
          rows={data}
          columns={[
            [
              t("Full name"),
              (r) => (
                <>
                  {r.name}
                  <small>{r.email}</small>
                </>
              ),
            ],
            [t("Role"), (r) => <Badge>{r.role}</Badge>],
            ["Status", (r) => <Badge>{r.active ? "Active" : "Pending"}</Badge>],
            [
              "Action",
              (r) =>
                r.role !== "admin" && (
                  <ActionButton
                    onClick={() =>
                      patch(`/admin/users/${r.id}`, { active: !r.active })
                    }
                  >
                    {t(r.active ? "Deactivate" : "Activate")}
                  </ActionButton>
                ),
            ],
          ]}
        />
      </Panel>
      <Panel title={t("Create user")}>
        <ActionForm
          label="Create user"
          onSubmit={(f) =>
            post("/admin/users", {
              name: f.get("name"),
              email: f.get("email"),
              password: f.get("password"),
              role: f.get("role"),
              school_id: user?.school_id,
              language: "en",
            })
          }
        >
          <div className="form-grid">
            <Field label="Full name">
              <input name="name" required minLength={2} />
            </Field>
            <Field label="Email address">
              <input name="email" type="email" required />
            </Field>
          </div>
          <Field label="Password">
            <input
              name="password"
              type="password"
              minLength={10}
              maxLength={128}
              required
              autoComplete="new-password"
            />
          </Field>
          <Field label="Role">
            <select name="role">
              <option value="student">{t("Student")}</option>
              <option value="teacher">{t("Teacher")}</option>
              <option value="parent">{t("Parent")}</option>
            </select>
          </Field>
          <small>
            <Trans
              value={
                " New teacher accounts remain pending until separately activated. Administrator provisioning is out of band. "
              }
            />
          </small>
        </ActionForm>
      </Panel>
    </>
  );
}
export function TeacherAssignments() {
  const { t } = useI18n(),
    { data: users, error } = useLoad<Row[]>("/admin/users"),
    { data: courses } = useLoad<Row[]>("/courses"),
    { data: assignments } = useLoad<Row[]>("/admin/teacher-assignments");
  const name = (id: number) => users?.find((x) => x.id === id)?.name || id;
  return (
    <>
      <Heading
        title={tr("Teacher assignments")}
        description="Assign active teachers and enroll students in school courses."
      />
      <Notice error>{error}</Notice>
      <div className="two-columns">
        <Panel title={t("Assign teacher")}>
          <ActionForm
            label="Assign teacher"
            onSubmit={(f) =>
              post("/admin/teacher-assignments", {
                teacher_id: Number(f.get("teacher_id")),
                course_id: Number(f.get("course_id")),
              })
            }
          >
            <Field label="Teacher">
              <select name="teacher_id" required>
                {users
                  ?.filter((u) => u.role === "teacher" && u.active)
                  .map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
              </select>
            </Field>
            <CourseSelect courses={courses} />
          </ActionForm>
        </Panel>
        <Panel title={t("Enroll student")}>
          <ActionForm
            label="Enroll student"
            onSubmit={(f) =>
              post("/admin/enrollments", {
                student_id: Number(f.get("student_id")),
                course_id: Number(f.get("course_id")),
              })
            }
          >
            <Field label="Student">
              <select name="student_id" required>
                {users
                  ?.filter((u) => u.role === "student")
                  .map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
              </select>
            </Field>
            <CourseSelect courses={courses} />
          </ActionForm>
        </Panel>
      </div>
      <Panel title={tr("Current assignments")}>
        <Table
          rows={assignments}
          columns={[
            [t("Teacher"), (r) => name(r.teacher_id)],
            [
              t("Course"),
              (r) => courses?.find((c) => c.id === r.course_id)?.title,
            ],
            [
              "Action",
              (r) => (
                <ActionButton
                  onClick={() =>
                    api(`/admin/teacher-assignments/${r.id}`, {
                      method: "DELETE",
                    })
                  }
                >
                  <Trans value={" Remove assignment "} />
                </ActionButton>
              ),
            ],
          ]}
        />
      </Panel>
    </>
  );
}
function CourseSelect({ courses }: { courses: Row[] | null }) {
  return (
    <Field label="Course">
      <select name="course_id" required>
        {courses?.map((c) => (
          <option key={c.id} value={c.id}>
            {c.title}
          </option>
        ))}
      </select>
    </Field>
  );
}
export function ParentLinks() {
  const { data, error } = useLoad<Row[]>("/admin/parent-links"),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={tr("Parent links")}
        description="Verify family identity through school records before granting access."
      />
      <Notice>
        <Trans
          value={
            " Approval grants access to a student's academic records. Verify the family relationship through your school's trusted process. "
          }
        />
      </Notice>
      <Notice error>{error}</Notice>
      <Panel>
        <Table
          rows={data}
          columns={[
            [t("Parent"), (r) => r.parent_name],
            [t("Student"), (r) => r.student_name],
            ["Status", (r) => <Badge>{r.status}</Badge>],
            [
              "Decision",
              (r) => (
                <div className="actions">
                  <ActionButton
                    onClick={() =>
                      patch(`/admin/parent-links/${r.id}`, {
                        status: "approved",
                      })
                    }
                  >
                    {t("Approve")}
                  </ActionButton>
                  <ActionButton
                    onClick={() =>
                      patch(`/admin/parent-links/${r.id}`, {
                        status: "rejected",
                      })
                    }
                  >
                    {t("Reject")}
                  </ActionButton>
                </div>
              ),
            ],
          ]}
        />
      </Panel>
    </>
  );
}
export function Reports() {
  const { data, error } = useLoad("/admin/reports"),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={tr("Reports")}
        description="School-scoped academic evidence and platform usage."
      />
      <Notice error>{error}</Notice>
      {data && (
        <>
          <div className="toolbar">
            <button className="button secondary" onClick={() => window.print()}>
              {t("Print report")}
            </button>
          </div>
          <div className="stats-grid">
            {[
              ["Users", data.users],
              [
                "School average",
                data.school_average !== null ? data.school_average + "%" : "—",
              ],
              ["Learning activity", data.learning_activities],
              ["Login events", data.login_events],
            ].map(([label, value]) => (
              <div className="stat-card" key={String(label)}>
                <div className="stat-label">{t(String(label))}</div>
                <strong className="stat-value">{value}</strong>
              </div>
            ))}
          </div>
          <Panel title={data.school.name}>
            <p>{data.method}</p>
            <Table
              rows={data.students}
              columns={[
                [t("Student"), (r) => r.name],
                [
                  t("Average score"),
                  (r) => (r.average !== null ? r.average + "%" : "No evidence"),
                ],
                ["Assessments", (r) => r.graded_assessments],
                ["Risk baseline", (r) => <Badge>{r.risk.level}</Badge>],
                ["Evidence", (r) => r.summary],
              ]}
            />
          </Panel>
        </>
      )}
    </>
  );
}
function PlanFields({ plan = {} }: { plan?: Row }) {
  return (
    <>
      <Field label="Title">
        <input name="name" required minLength={3} defaultValue={plan.name} />
      </Field>
      <div className="form-grid">
        <Field label="Price in TZS">
          <input
            name="price_tzs"
            type="number"
            min={1}
            max={10000000}
            required
            defaultValue={plan.price_tzs || 3000}
          />
        </Field>
        <Field label="Duration in days">
          <input
            name="days"
            type="number"
            min={1}
            max={366}
            required
            defaultValue={plan.days || 30}
          />
        </Field>
      </div>
      <Field label="Status">
        <select name="active" defaultValue={String(plan.active ?? true)}>
          <option value="true">
            <Trans value={"Active"} />
          </option>
          <option value="false">
            <Trans value={"Unavailable"} />
          </option>
        </select>
      </Field>
    </>
  );
}
const planBody = (f: FormData) => ({
  name: f.get("name"),
  price_tzs: Number(f.get("price_tzs")),
  days: Number(f.get("days")),
  premium: true,
  active: f.get("active") === "true",
});
export function Plans() {
  const { data, error } = useLoad<Row[]>("/admin/plans"),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={tr("Plans")}
        description="Manage demonstration premium plans for your school."
      />
      <Notice error>{error}</Notice>
      <div className="two-columns">
        <Panel title={t("Create plan")}>
          <ActionForm
            label="Create plan"
            onSubmit={(f) => post("/admin/plans", planBody(f))}
          >
            <PlanFields />
          </ActionForm>
        </Panel>
        <div>
          {data?.map((p) => (
            <Panel key={p.id} title={p.name}>
              {p.school_id ? (
                <ActionForm
                  label="Save changes"
                  onSubmit={(f) => patch(`/admin/plans/${p.id}`, planBody(f))}
                >
                  <PlanFields plan={p} />
                </ActionForm>
              ) : (
                <>
                  <p>
                    <Trans value={" TZS "} />
                    {p.price_tzs.toLocaleString()} / {p.days}
                    <Trans value={" days "} />
                  </p>
                  <Badge>
                    <Trans value={"Shared demonstration plan"} />
                  </Badge>
                  <p className="text-sm mt-4">
                    <Trans
                      value={
                        " Shared plans are provisioned out of band. Create a school plan to manage its price and availability. "
                      }
                    />
                  </p>
                </>
              )}
            </Panel>
          ))}
        </div>
      </div>
    </>
  );
}
export function Subscriptions({ payments = false }: { payments?: boolean }) {
  const { data, error } = useLoad<Row[]>("/admin/subscriptions"),
    { t } = useI18n();
  return (
    <>
      <Heading
        title={payments ? "Payments" : "Subscriptions"}
        description="Monitor simulated transactions and entitlement states within your school."
      />
      <Notice>
        <Trans
          value={
            " Simulated provider only. Active status requires a verified payment and an unexpired subscription. Suspension and cancellation immediately deny premium access. "
          }
        />
      </Notice>
      <Notice error>{error}</Notice>
      <Panel>
        <Table
          rows={data}
          columns={[
            [
              t("Users"),
              (r) => (
                <>
                  {r.user_name}
                  <small>
                    <Trans value={"Subscription "} />
                    {r.id}
                  </small>
                </>
              ),
            ],
            ["Amount", (r) => `TZS ${r.payment?.amount_tzs.toLocaleString()}`],
            [
              "Payment",
              (r) => (
                <>
                  <Badge>{r.payment?.status}</Badge>
                  <small>{r.payment?.provider_reference}</small>
                </>
              ),
            ],
            ["Subscription", (r) => <Badge>{r.status}</Badge>],
            [
              "Expires",
              (r) =>
                r.expires_at
                  ? new Date(r.expires_at + "Z").toLocaleDateString()
                  : "—",
            ],
            [
              "Actions",
              (r) => (
                <div className="actions">
                  {r.payment?.status === "pending" &&
                    r.status === "pending_payment" && (
                      <ActionButton
                        onClick={() => post(`/payments/${r.payment.id}/verify`)}
                      >
                        {t("Verify payment")}
                      </ActionButton>
                    )}
                  {!payments && r.status !== "cancelled" && (
                    <>
                      <ActionButton
                        onClick={() =>
                          patch(`/admin/subscriptions/${r.id}`, {
                            status:
                              r.status === "active" ? "suspended" : "active",
                          })
                        }
                      >
                        {t(r.status === "active" ? "Suspend" : "Restore")}
                      </ActionButton>
                      <ActionButton
                        onClick={() =>
                          patch(`/admin/subscriptions/${r.id}`, {
                            status: "cancelled",
                          })
                        }
                      >
                        {t("Cancel")}
                      </ActionButton>
                    </>
                  )}
                </div>
              ),
            ],
          ]}
        />
      </Panel>
    </>
  );
}
export function Audit() {
  const { data, error } = useLoad<Row[]>("/admin/audit");
  return (
    <>
      <Heading
        title={tr("Audit trail")}
        description="Recent account, academic, recommendation and payment actions in your school."
      />
      <Notice error>{error}</Notice>
      <Panel>
        <Table
          rows={data}
          columns={[
            ["Time in UTC", (r) => r.created_at],
            ["Actor ID", (r) => r.actor_id],
            ["Action", (r) => r.action],
            ["Entity", (r) => r.entity],
            ["Detail", (r) => r.detail],
          ]}
        />
      </Panel>
    </>
  );
}
