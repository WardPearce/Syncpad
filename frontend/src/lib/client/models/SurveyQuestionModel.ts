/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SurveyChoicesModel } from './SurveyChoicesModel';
import type { SurveyDescriptionModel } from './SurveyDescriptionModel';
import type { SurveyQuestionsModel } from './SurveyQuestionsModel';
import type { SurveyRegexModel } from './SurveyRegexModel';

export type SurveyQuestionModel = {
    id: number;
    regex?: (null | SurveyRegexModel);
    description?: (null | SurveyDescriptionModel);
    question: SurveyQuestionsModel;
    choices?: (null | Array<SurveyChoicesModel>);
    required?: boolean;
    type: string;
};

