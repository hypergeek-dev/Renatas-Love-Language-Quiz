export type AnswerKey = "A" | "B";

export type PublicQuestion = {
  id: number;
  scene: string;
  prompt: string;
  choices: Record<AnswerKey, string>;
};

export type SessionResponse = {
  id: string;
  current_question: number;
  completed: boolean;
  answered_count: number;
  total_questions: number;
  question: PublicQuestion | null;
  answers: Record<string, AnswerKey>;
};

export type ResultDimension = {
  key: string;
  name: string;
  score: number;
  percentage: number;
  interpretation: string;
};

export type ResultResponse = {
  completed: boolean;
  primary: { key: string; name: string; percentage: number };
  secondary: { key: string; name: string; percentage: number };
  profile_shape: "Focused" | "Blended" | "Broad";
  summary: string;
  dimensions: ResultDimension[];
  percent_total: number;
};
