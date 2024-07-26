import { SurveyQuestionModel } from './../../lib/client/models/SurveyQuestionModel';

export type rawChoice = {
  id: number;
  choice: string;
};

export type rawQuestion = {
  id: number;
  regex: string | null;
  description: string | null;
  choices: rawChoice[];
  required: boolean;
  question: string;
  type: SurveyQuestionModel.type;
};

export type rawSurveyQuestions = {
  [key: number]: rawQuestion;
};