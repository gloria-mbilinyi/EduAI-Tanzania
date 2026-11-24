import { test, expect, Page } from "@playwright/test";
const password = process.env.EDUAI_DEMO_PASSWORD;
test.skip(
  !password,
  "Set EDUAI_DEMO_PASSWORD to the password supplied to the fictional seed script.",
);
async function login(page: Page, handle: string) {
  const auth=await page.request.post('/api/auth/login',{data:{email:`${handle}@demo.eduai.test`,password}});
  const identity=await auth.json();
  await page.request.patch('/api/me/language',{headers:{Authorization:`Bearer ${identity.access_token}`},data:{language:'en'}});
  await page.goto("/login");
  await page.getByLabel("Email address").fill(`${handle}@demo.eduai.test`);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/app\/overview/);
  await expect(
    page.getByRole("heading", { name: /Welcome back/ }),
  ).toBeVisible();
}
const screenshot = (page: Page, name: string) =>
  page.screenshot({ path: `../docs/screenshots/${name}.png`, fullPage: true });
test("public landing and registration entry", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Every learner/ }),
  ).toBeVisible();
  await screenshot(page, "01-landing-desktop");
  await page.getByRole("link", { name: "Get started", exact: true }).click();
  await expect(page.getByLabel("School", { exact: true })).toBeVisible();
});
test("student dashboard shows actual courses and only approved pathways", async ({
  page,
}) => {
  await login(page, "amina");
  await expect(page.getByText("Mathematics foundations").first()).toBeVisible();
  await screenshot(page, "02-student-dashboard");
  await page
    .getByRole("link", { name: "Learning pathways", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Discovering living things",
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    page.locator(".badge").filter({ hasText: "pending_review" }),
  ).toHaveCount(0);
});
test("teacher dashboard and lesson assistance persist a reviewed draft", async ({
  page,
}) => {
  await login(page, "neema");
  await screenshot(page, "03-teacher-dashboard");
  await page
    .getByRole("link", { name: "Lesson planning", exact: true })
    .click();
  await page.getByLabel("Topic", { exact: true }).fill("Linear equations");
  await page
    .getByRole("button", { name: "Generate draft", exact: true })
    .click();
  await expect(page.getByLabel("Content", { exact: true })).toHaveValue(
    /Learning objectives/,
  );
  await page.getByRole("checkbox").check();
  await page
    .getByRole("button", { name: "Save reviewed lesson", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Linear equations", exact: true }).last(),
  ).toBeVisible();
  await screenshot(page, "04-reviewed-lesson");
});
test("parent sees approved child and academic report", async ({ page }) => {
  await login(page, "parent");
  await screenshot(page, "05-parent-dashboard");
  await page
    .getByRole("link", { name: "Linked students", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Amina Juma", exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "View report", exact: true }).click();
  await expect(
    page.getByText("Mathematics practice journal", { exact: true }),
  ).toBeVisible();
  await screenshot(page, "06-parent-report");
});
test("school administrator can inspect scoped accounts and reports", async ({
  page,
}) => {
  await login(page, "admin");
  await screenshot(page, "07-administrator-dashboard");
  await page.getByRole("link", { name: "Users", exact: true }).click();
  await expect(page.getByRole("cell", { name: /Amina Juma/ })).toBeVisible();
  await expect(page.getByText("isolated@demo.eduai.test")).toHaveCount(0);
  await page.getByRole("link", { name: "Reports", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "Mwangaza Secondary (Fictional Demo)",
      exact: true,
    }),
  ).toBeVisible();
  await screenshot(page, "08-school-report");
});
test("bilingual retrieval tutor returns a cited passage", async ({ page }) => {
  await login(page, "amina");
  await page.getByRole("link", { name: /AI tutor/ }).click();
  await page
    .getByLabel("Ask a question", { exact: true })
    .fill("How do I solve a linear equation?");
  await page.getByRole("button", { name: "Ask tutor", exact: true }).click();
  await expect(
    page.getByText(/EduAI original teaching passage M01/).first(),
  ).toBeVisible();
  await screenshot(page, "09-retrieval-tutor");
  await page.getByRole("button", { name: "Kiswahili", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Msaidizi wa masomo", exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("Uliza swali", { exact: true })
    .fill("Eleza mlinganyo wa mstari");
  await page
    .getByRole("button", { name: "Uliza msaidizi", exact: true })
    .click();
  await expect(page.getByText(/Kutatua 2x/).first()).toBeVisible();
  await screenshot(page, "10-kiswahili-tutor");
});
test("demo checkout requires a separate server verification before premium activation", async ({
  page,
}) => {
  await page.goto("/register");
  await page
    .getByLabel("Full name", { exact: true })
    .fill("Fictional Payment Test");
  await page.getByLabel("School", { exact: true }).selectOption("1");
  await page
    .getByLabel("Email address", { exact: true })
    .fill(`payment-${Date.now()}@demo.eduai.test`);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Register", exact: true }).click();
  await expect(page).toHaveURL(/app\/overview/);
  await page.getByRole("link", { name: "Subscriptions", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Basic access", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Choose plan", { exact: true }).selectOption("1");
  await page
    .getByRole("button", { name: "Simulated payment", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Verify payment", exact: true }).first(),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Basic access", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Verify payment", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "Premium active", exact: true }),
  ).toBeVisible();
  await screenshot(page, "11-verified-demo-subscription");
});
test("mobile navigation and content fit a narrow viewport", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, "amina");
  await screenshot(page, "12-student-mobile");
  await page
    .getByRole("button", { name: "Open navigation", exact: true })
    .click();
  await page.getByRole("link", { name: "My courses", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "My courses", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await screenshot(page, "13-courses-mobile");
});
