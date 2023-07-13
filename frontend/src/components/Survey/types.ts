export enum SurveyAnswerType {
  "Short Answer" = "Short Answer",
  Paragraph = "Paragraph",
  "Multiple Choice" = "Multiple Choice",
  "Single Choice" = "Single Choice",
}

export type rawQuestion = {
  id: number;
  regex: string | null;
  description: string | null;
  choices: string[];
  required: boolean;
  question: string;
  type: SurveyAnswerType;
};
