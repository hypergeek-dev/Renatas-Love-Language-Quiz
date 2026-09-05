import { render, screen, waitFor } from "@testing-library/react";
import { cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import App from "./App";

const firstSession = {
  id: "session-1",
  current_question: 1,
  completed: false,
  answered_count: 0,
  total_questions: 30,
  question: {
    id: 1,
    scene: "Rain taps softly against the window.",
    prompt: "What would stay with you more?",
    choices: { A: "Tender words", B: "Unhurried time" }
  },
  answers: {}
};

describe("App", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(firstSession)
      })
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  test("creates a fresh session on initial load", async () => {
    sessionStorage.setItem("renata_session_id", "old-session");
    render(<App />);
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/session", expect.objectContaining({ method: "POST" })));
    expect(fetch).toHaveBeenCalledWith(
      "/api/session",
      expect.objectContaining({ body: JSON.stringify({ previous_session_id: "old-session" }) })
    );
    expect(sessionStorage.getItem("renata_session_id")).toBe("session-1");
  });

  test("shows the first quiz scene after Begin", async () => {
    render(<App />);
    await screen.findByText("Begin");
    await userEvent.click(screen.getByText("Begin"));
    expect(screen.getByText("Question 1 of 30")).toBeInTheDocument();
    expect(screen.getByText("Rain taps softly against the window.")).toBeInTheDocument();
  });

  test("Back on the first question returns to intro", async () => {
    render(<App />);
    await screen.findByText("Begin");
    await userEvent.click(screen.getByText("Begin"));
    await userEvent.click(screen.getByRole("button", { name: "Back" }));
    expect(screen.getByRole("button", { name: "Begin" })).toBeInTheDocument();
    expect(screen.queryByText("Question 1 of 30")).not.toBeInTheDocument();
  });

  test("shows binary A/B choices and no Both option", async () => {
    render(<App />);
    await screen.findByText("Begin");
    await userEvent.click(screen.getByText("Begin"));
    expect(screen.getByText("Tender words")).toBeInTheDocument();
    expect(screen.getByText("Unhurried time")).toBeInTheDocument();
    expect(screen.queryByText(/both/i)).not.toBeInTheDocument();
  });

  test("selecting a choice sends the corresponding answer key", async () => {
    render(<App />);
    await screen.findByText("Begin");
    await userEvent.click(screen.getByText("Begin"));
    await userEvent.click(screen.getByText("Unhurried time"));
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/api/session/session-1/answer",
        expect.objectContaining({
          body: JSON.stringify({ question_id: 1, selected_answer: "B" })
        })
      )
    );
  });
});
