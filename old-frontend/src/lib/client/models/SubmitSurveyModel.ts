/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SurveyAnswerModel } from './SurveyAnswerModel';

export type SubmitSurveyModel = {
    answers: Array<SurveyAnswerModel>;
    ip_key?: (null | string);
};

