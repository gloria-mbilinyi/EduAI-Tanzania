import {
  Link,
  NavLink,
  useNavigate,
  Navigate,
  useParams,
} from "react-router-dom";
import {
  BookOpen,
  ShieldCheck,
  Users,
  Sparkles,
  Check,
  GraduationCap,
  Globe,
} from "lucide-react";
import { Brand } from "../layouts/Dashboard";
import { useI18n } from "../i18n";
import { useAuth } from "../contexts/Auth";
import { useLoad } from "../hooks/useLoad";
import { ActionForm, Field, Notice } from "../components/UI";
import { post, Row } from "../services/api";

export function PublicHeader() {
  const { t, lang, toggle } = useI18n();
  return (
    <header className="public-header">
      <Brand />
      <nav>
        {["About", "Features", "Plans", "Contact"].map((x) => (
          <NavLink key={x} to={"/" + x.toLowerCase()}>
            {t(x)}
          </NavLink>
        ))}
      </nav>
      <div className="public-actions">
        <button className="language-button" onClick={toggle}>
          <Globe size={16} />
          {lang === "en" ? "Kiswahili" : "English"}
        </button>
        <Link className="button secondary" to="/login">
          {t("Sign in")}
        </Link>
      </div>
    </header>
  );
}
export function Public() {
  const { t } = useI18n(),
    params = useParams(),
    section = params.section || "home",
    { data: plans } = useLoad<Row[]>("/plans");
  return (
    <div className="public-page">
      <PublicHeader />
      {section === "home" ? (
        <>
          <section className="landing-hero">
            <div>
              <span className="eyebrow">
                <span className="mini-square" /> BUILT FOR TANZANIAN SCHOOLS
              </span>
              <h1>
                Every learner.
                <br />A brighter <em>possibility.</em>
              </h1>
              <p>
                Learning support that meets you where you are. Connect students,
                teachers and families through one thoughtful school workspace.
              </p>
              <div className="hero-buttons">
                <Link to="/register" className="button">
                  {t("Get started")}
                </Link>
                <Link to="/features" className="button secondary">
                  {t("Features")}
                </Link>
              </div>
              <div className="hero-proof">
                <span>
                  <Check size={17} /> English & Kiswahili
                </span>
                <span>
                  <Check size={17} /> Designed for low bandwidth
                </span>
              </div>
            </div>
            <div className="learning-art">
              <div className="art-caption">
                <Sparkles size={18} /> A little guidance goes a long way
              </div>
              <svg
                viewBox="0 0 500 340"
                role="img"
                aria-label="Illustration of learning books and a growing plant"
              >
                <circle cx="260" cy="167" r="145" fill="#e1eee4" />
                <path d="M155 250L350 210L395 237L201 281Z" fill="#e1b143" />
                <path
                  d="M155 250V270L201 302L395 257V237L201 281Z"
                  fill="#f6d780"
                />
                <path d="M120 204L315 165L360 192L166 236Z" fill="#08604c" />
                <path
                  d="M120 204V224L166 257L360 212V192L166 236Z"
                  fill="#318c73"
                />
                <path d="M200 141L344 114L386 142L242 173Z" fill="#fff" />
                <path
                  d="M200 141V162L242 192L386 163V142L242 173Z"
                  fill="#c6dcd2"
                />
                <path d="M300 115V62" stroke="#16614b" strokeWidth="7" />
                <path
                  d="M300 86C258 86 258 48 262 42C295 40 310 62 300 86M301 67C338 68 350 39 345 28C314 27 297 44 301 67"
                  fill="#369276"
                />
                <path d="M275 110H325L316 143H285Z" fill="#ddaa43" />
                <circle cx="127" cy="95" r="24" fill="#efbe56" />
                <path
                  d="M115 95H139M127 83V107"
                  stroke="#fff"
                  strokeWidth="3"
                />
                <path
                  d="M393 89L402 108L424 111L408 126L411 147L392 137L373 147L376 126L361 111L383 108Z"
                  fill="#78ae96"
                />
              </svg>
              <div className="art-card">
                <span className="art-icon">
                  <GraduationCap />
                </span>
                <div>
                  <strong>{t("Reviewed learning, connected schools.")}</strong>
                  <small>Guided by teachers. Built around learners.</small>
                </div>
              </div>
            </div>
          </section>
          <section className="feature-strip">
            {[
              [
                BookOpen,
                "Learn at your pace",
                "Notes, assignments and quizzes in one place.",
              ],
              [
                ShieldCheck,
                "Teacher guided AI",
                "Every learning pathway is reviewed before publication.",
              ],
              [
                Users,
                "Keep families connected",
                "Secure progress reports and school conversations.",
              ],
            ].map(([Icon, title, body], i) => {
              const I = Icon as typeof BookOpen;
              return (
                <article key={i}>
                  <I size={25} />
                  <h3>{String(title)}</h3>
                  <p>{String(body)}</p>
                </article>
              );
            })}
          </section>
        </>
      ) : (
        <section className="public-section">
          <span className="eyebrow">EDUAI TANZANIA</span>
          <h1>{t(section.charAt(0).toUpperCase() + section.slice(1))}</h1>
          {section === "plans" ? (
            <>
              <p>
                Academic demonstration prices in Tanzanian shillings. No real
                money is collected.
              </p>
              <div className="card-grid">
                {plans?.map((p) => (
                  <article className="panel pricing" key={p.id}>
                    <BadgeText />
                    <h2>{p.name}</h2>
                    <strong className="price">
                      TZS {p.price_tzs.toLocaleString()}
                    </strong>
                    <p>per {p.days} days</p>
                    <ul>
                      <li>Teacher quiz and lesson draft assistance</li>
                      <li>Server-verified premium entitlement</li>
                      <li>Core learning and retrieval tutor remain free</li>
                    </ul>
                    <Link className="button" to="/login">
                      {t("Choose plan")}
                    </Link>
                  </article>
                ))}
              </div>
            </>
          ) : section === "contact" ? (
            <>
              <p>
                For this academic demonstration, contact your school
                administrator directly. This form creates a message for you to
                copy; it does not send email.
              </p>
              <ActionForm
                label="Create"
                onSubmit={async (f) => {
                  await navigator.clipboard.writeText(
                    `EduAI support request\n${f.get("name")}\n${f.get("message")}`,
                  );
                }}
              >
                <Field label="Full name">
                  <input name="name" required />
                </Field>
                <Field label="Message">
                  <textarea name="message" required />
                </Field>
              </ActionForm>
            </>
          ) : section === "about" ? (
            <>
              <p>
                EduAI Tanzania is an academic secondary-school prototype
                connecting school administration with everyday learning. It
                explores how affordable browser access, bilingual content and
                teacher-supervised assistance can support schools in Tanzania.
              </p>
              <p>
                The prototype uses fictional schools and users. Classroom
                effectiveness, curriculum alignment and operational readiness
                require further evaluation with educators before any real
                deployment.
              </p>
            </>
          ) : (
            <>
              <p>
                Students study notes, submit assignments, complete automatically
                graded quizzes and follow teacher-approved learning pathways.
                Teachers manage assigned courses, review recommendations and
                prepare editable draft teaching content.
              </p>
              <p>
                Parents access only approved linked students, receive in-app
                alerts and communicate with assigned teachers. School
                administrators manage local accounts, enrollments, reports and
                demonstration subscriptions.
              </p>
              <p>
                AI assistance combines explainable performance rules with
                bilingual passage retrieval. It does not use a paid API or a
                validated predictive model.
              </p>
            </>
          )}
        </section>
      )}
      <footer className="public-footer">
        <Brand />
        <p>
          A secondary-school software engineering prototype. All demo records
          are fictional.
        </p>
        <Link to="/login">{t("Sign in")}</Link>
      </footer>
    </div>
  );
}
function BadgeText() {
  return <span className="eyebrow">LEARNING PLUS</span>;
}
export function AuthPage({ register = false }: { register?: boolean }) {
  const { login, user } = useAuth(),
    { t, lang } = useI18n(),
    navigate = useNavigate(),
    { data: schools } = useLoad<Row[]>("/schools");
  if (user) return <Navigate to="/app/overview" replace />;
  return (
    <div className="auth-page">
      <PublicHeader />
      <main className="auth-grid">
        <div className="auth-intro">
          <span className="eyebrow">A CONNECTED SCHOOL COMMUNITY</span>
          <h1>
            {register
              ? "Start your next chapter."
              : "A little progress, every day."}
          </h1>
          <p>
            One place for your learning, your teaching and the conversations
            that help students grow.
          </p>
          <div className="auth-quote">
            <BookOpen size={40} />
            <p>
              English and Kiswahili.
              <br />
              Accessible on your phone or computer.
            </p>
          </div>
        </div>
        <section className="auth-card">
          <span className="eyebrow">EDUAI WORKSPACE</span>
          <h2>{t(register ? "Register" : "Welcome back")}</h2>
          <p>
            {register
              ? "Choose your registered school to begin."
              : "Sign in with your school account."}
          </p>
          <ActionForm
            label={register ? "Register" : "Sign in"}
            onSubmit={async (f) => {
              if (register) {
                const r = await post("/auth/register", {
                  name: f.get("name"),
                  email: f.get("email"),
                  password: f.get("password"),
                  school_id: Number(f.get("school_id")),
                  role: f.get("role"),
                  language: lang,
                });
                if (!r.user.active) {
                  alert(r.message);
                  navigate("/login");
                  return;
                }
              }
              await login(String(f.get("email")), String(f.get("password")));
              navigate("/app/overview");
            }}
          >
            {register && (
              <>
                <Field label="Full name">
                  <input
                    name="name"
                    required
                    minLength={2}
                    autoComplete="name"
                  />
                </Field>
                <Field label="School">
                  <select name="school_id" required defaultValue="">
                    <option value="" disabled>
                      Select a registered school
                    </option>
                    {schools?.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Role">
                  <select name="role">
                    <option value="student">{t("Student")}</option>
                    <option value="teacher">{t("Teacher")}</option>
                    <option value="parent">{t("Parent")}</option>
                  </select>
                </Field>
              </>
            )}
            <Field label="Email address">
              <input
                name="email"
                type="email"
                required
                autoComplete="username"
                placeholder="amina@demo.eduai.test"
              />
            </Field>
            <Field label="Password">
              <input
                name="password"
                type="password"
                minLength={register ? 10 : 1}
                maxLength={128}
                required
                autoComplete={register ? "new-password" : "current-password"}
              />
            </Field>
            {register && (
              <Notice>
                New teachers require school administrator activation. Parent
                links require school verification.
              </Notice>
            )}
          </ActionForm>
          <p className="auth-switch">
            {register ? "Already registered?" : "New to EduAI?"}{" "}
            <Link to={register ? "/login" : "/register"}>
              {t(register ? "Sign in" : "Register")}
            </Link>
          </p>
        </section>
      </main>
    </div>
  );
}
