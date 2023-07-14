import { SurveyQuestionModel } from './../../lib/client/models/SurveyQuestionModel';

export type rawQuestion = {
  id: number;
  regex: string | null;
  description: string | null;
  choices: string[];
  required: boolean;
  question: string;
  type: SurveyQuestionModel.type;
};
