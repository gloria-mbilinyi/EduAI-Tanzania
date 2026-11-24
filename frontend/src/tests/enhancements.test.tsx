import { it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider, tr } from "../i18n";
import { AttemptHistory } from "../pages/AssignmentWorkflows";
import { MathAnswer } from "../pages/AI";

it("retains all attempts and distinguishes the official score from earlier marks", () => {
  render(
    <I18nProvider>
      <AttemptHistory
        official={3}
        attempts={[45, 80, 100].map((score, i) => ({
          id: i + 1,
          number: i + 1,
          content: `Solution ${i + 1}`,
          grade: { score, feedback: `Feedback ${i + 1}` },
        }))}
      />
    </I18nProvider>,
  );
  expect(screen.getAllByRole("progressbar")).toHaveLength(3);
  expect(screen.getByText("Official score")).toBeInTheDocument();
  expect(screen.getByText("Solution 1")).toBeInTheDocument();
  expect(screen.getByText("100% · Feedback 3")).toBeInTheDocument();
});

it("translates assessment controls and role-specific guidance with structured keys", () => {
  for (const key of [
    "Attempt history",
    "Maximum attempts",
    "Official grading policy",
    "Review questions and submissions",
    "Manage school accounts and activate verified teachers.",
    "Access is granted only after your school verifies the family link.",
    "Invalid credentials or account awaiting activation",
  ]) {
    expect(tr(key, "sw")).not.toBe(key);
    expect(tr(key, "en")).toBe(key);
  }
});

it("renders powers and untrusted tutor text without executing markup", () => {
  const { container } = render(
    <MathAnswer text={"3*x^2 + 2\n<script>bad()</script>"} />,
  );
  expect(container.querySelector("sup")).toHaveTextContent("2");
  expect(container.querySelector("script")).toBeNull();
  expect(screen.getByText("<script>bad()</script>")).toBeInTheDocument();
});
