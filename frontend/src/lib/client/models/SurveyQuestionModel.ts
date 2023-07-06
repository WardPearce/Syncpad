/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChoicesModel } from './ChoicesModel';
import type { DescriptionModel } from './DescriptionModel';
import type { QuestionModel } from './QuestionModel';
import type { RegexModel } from './RegexModel';

export type SurveyQuestionModel = {
    id: number;
    regex?: (null | RegexModel);
    description?: (null | DescriptionModel);
    question?: (null | QuestionModel);
    choices?: (null | Array<ChoicesModel>);
    required?: boolean;
    type: string;
};

