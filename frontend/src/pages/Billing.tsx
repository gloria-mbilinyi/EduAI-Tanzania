import { useAuth } from "../contexts/Auth";
import { useI18n } from "../i18n";
import { useLoad } from "../hooks/useLoad";
import { post, download, Row } from "../services/api";
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

export function Billing() {
  const { user } = useAuth(),
    { t } = useI18n(),
    { data, error } = useLoad("/billing"),
    { data: plans } = useLoad<Row[]>("/plans");
  return (
    <>
      <Heading
        title="Subscriptions"
        description="Core learning is free. Explore premium teacher tools through a verified demo subscription."
      />
      <Notice>
        Academic simulation only. No M-Pesa, Airtel Money, Mixx by Yas, banking
        or real-money integration is connected. The backend checks its simulated
        provider ledger before activation.
      </Notice>
      <Notice error>{error}</Notice>
      <Panel
        title={t(data?.premium ? "Premium active" : "Basic access")}
        action={<Badge>{data?.premium ? "Active" : "Free core access"}</Badge>}
      >
        <ActionForm
          label="Simulated payment"
          onSubmit={(f) =>
            post("/billing/checkout", {
              plan_id: Number(f.get("plan_id")),
              demo_scenario: f.get("scenario"),
            })
          }
        >
          <div className="form-grid">
            <Field label="Choose plan">
              <select name="plan_id" required defaultValue="">
                <option value="" disabled>
                  {t("Choose plan")}
                </option>
                {plans
                  ?.filter(
                    (p) => !p.school_id || p.school_id === user?.school_id,
                  )
                  .map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} · TZS {p.price_tzs.toLocaleString()} / {p.days}{" "}
                      days
                    </option>
                  ))}
              </select>
            </Field>
            <Field label="Demo provider outcome">
              <select name="scenario">
                <option value="success">Successful simulation</option>
                <option value="failed">Failed simulation</option>
                <option value="rejected">Rejected simulation</option>
              </select>
            </Field>
          </div>
        </ActionForm>
      </Panel>
      <Panel title="Transaction history">
        {data?.subscriptions?.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Plan</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Expires</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {data.subscriptions.map((s: Row) => (
                  <tr key={s.id}>
                    <td>
                      {s.plan}
                      <small>{s.payment?.provider_reference}</small>
                    </td>
                    <td>TZS {s.payment?.amount_tzs.toLocaleString()}</td>
                    <td>
                      <Badge>{s.status}</Badge>
                      <small>Payment: {s.payment?.status}</small>
                    </td>
                    <td>
                      {s.expires_at
                        ? new Date(s.expires_at + "Z").toLocaleDateString()
                        : "—"}
                    </td>
                    <td>
                      {s.payment?.status === "pending" &&
                        s.status === "pending_payment" && (
                          <ActionButton
                            onClick={() =>
                              post(`/payments/${s.payment.id}/verify`)
                            }
                          >
                            {t("Verify payment")}
                          </ActionButton>
                        )}
                      {s.payment?.status === "verified" && (
                        <ActionButton
                          onClick={() =>
                            download(
                              `/payments/${s.payment.id}/receipt`,
                              "demo-receipt.txt",
                            )
                          }
                        >
                          {t("Receipt")}
                        </ActionButton>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty />
        )}
      </Panel>
    </>
  );
}
