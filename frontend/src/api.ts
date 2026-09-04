import type { AnswerKey, ResultResponse, SessionResponse } from "./types";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

export function createSession(previousSessionId?: string | null) {
  return request<SessionResponse>("/api/session", {
    method: "POST",
    body: JSON.stringify({ previous_session_id: previousSessionId ?? null })
  });
}

export function answerQuestion(sessionId: string, questionId: number, selectedAnswer: AnswerKey) {
  return request<SessionResponse>(`/api/session/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify({ question_id: questionId, selected_answer: selectedAnswer })
  });
}

export function goBack(sessionId: string) {
  return request<SessionResponse>(`/api/session/${sessionId}/back`, { method: "POST" });
}

export function resetSession(sessionId: string) {
  return request<SessionResponse>(`/api/session/${sessionId}/reset`, { method: "POST" });
}

export function getResult(sessionId: string) {
  return request<ResultResponse>(`/api/session/${sessionId}/result`);
}
