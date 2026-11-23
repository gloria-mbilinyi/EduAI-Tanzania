import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { I18nProvider, useI18n } from "../i18n";
import { AuthProvider } from "../contexts/Auth";
import { Dashboard, menus } from "../layouts/Dashboard";
import { ActionForm, Field } from "../components/UI";
import { Courses } from "../pages/Academics";
import { api, post } from "../services/api";
const response = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
function Language() {
  const { t, toggle } = useI18n();
  return (
    <>
      <h1>{t("Assignments")}</h1>
      <button onClick={toggle}>Switch</button>
    </>
  );
}
function wrap(child: React.ReactNode) {
  return render(
    <MemoryRouter>
      <I18nProvider>
        <AuthProvider>{child}</AuthProvider>
      </I18nProvider>
    </MemoryRouter>,
  );
}
describe("bilingual interface and role navigation", () => {
  it("switches navigation labels and the document language", () => {
    render(
      <I18nProvider>
        <Language />
      </I18nProvider>,
    );
    expect(screen.getByRole("heading")).toHaveTextContent("Assignments");
    fireEvent.click(screen.getByText("Switch"));
    expect(screen.getByRole("heading")).toHaveTextContent("Kazi za nyumbani");
    expect(document.documentElement.lang).toBe("sw");
  });
  it("renders only student navigation for a student session", () => {
    sessionStorage.setItem(
      "eduai-user",
      JSON.stringify({ id: 3, name: "Amina Demo", role: "student" }),
    );
    wrap(<Dashboard />);
    expect(
      screen.getByRole("link", { name: "My courses" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: "Payments" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Sign out" }),
    ).toBeInTheDocument();
  });
  it("defines usable navigation for every required role", () => {
    expect(Object.keys(menus)).toEqual([
      "student",
      "teacher",
      "parent",
      "admin",
    ]);
    for (const items of Object.values(menus)) {
      expect(items.length).toBeGreaterThan(5);
      expect(new Set(items.map((x) => x[0])).size).toBe(items.length);
    }
  });
});
describe("real interface states", () => {
  it("shows an action failure instead of a success state", async () => {
    wrap(
      <ActionForm
        onSubmit={async () => {
          throw new Error("Course access denied");
        }}
      >
        <Field label="Title">
          <input name="title" defaultValue="Draft" />
        </Field>
      </ActionForm>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Course access denied",
    );
    expect(screen.queryByText("Save changes ✓")).not.toBeInTheDocument();
  });
  it("submits form values and confirms successful persistence", async () => {
    const save = vi.fn(async (f: FormData) => {
      expect(f.get("title")).toBe("Fractions");
    });
    wrap(
      <ActionForm onSubmit={save}>
        <Field label="Title">
          <input name="title" defaultValue="Fractions" />
        </Field>
      </ActionForm>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Save changes");
    expect(save).toHaveBeenCalledOnce();
  });
  it("filters course cards using user input", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      response([
        {
          id: 1,
          title: "Algebra foundations",
          subject: "Mathematics",
          form: "Form 2",
          description: "Practice",
        },
        {
          id: 2,
          title: "Living things",
          subject: "Biology",
          form: "Form 2",
          description: "Cells",
        },
      ]),
    );
    wrap(<Courses />);
    expect(await screen.findByText("Algebra foundations")).toBeInTheDocument();
    fireEvent.change(screen.getByRole("searchbox"), {
      target: { value: "biology" },
    });
    expect(screen.queryByText("Algebra foundations")).not.toBeInTheDocument();
    expect(screen.getByText("Living things")).toBeInTheDocument();
  });
});
describe("API client contract", () => {
  it("adds bearer authentication without putting credentials in a URL", async () => {
    sessionStorage.setItem("eduai-token", "unit-test-token");
    const fetch = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(response({ ok: true }));
    await post("/recommendations/1/review", {
      decision: "rejected",
      comment: "Revise",
    });
    expect(fetch).toHaveBeenCalledWith(
      "/api/recommendations/1/review",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer unit-test-token",
        }),
      }),
    );
  });
  it("surfaces structured API validation failures", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      response(
        { detail: [{ loc: ["body", "score"], msg: "must be <= 100" }] },
        422,
      ),
    );
    await expect(api("/submissions/1/grade")).rejects.toThrow(
      "score: must be <= 100",
    );
  });
  it("surfaces offline errors", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(
      new TypeError("Failed to fetch"),
    );
    await expect(api("/courses")).rejects.toThrow("Failed to fetch");
  });
});
