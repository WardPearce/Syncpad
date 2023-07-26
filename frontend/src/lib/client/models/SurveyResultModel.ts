/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SurveyAnswerModel } from './SurveyAnswerModel';

export type SurveyResultModel = {
    answers: Array<SurveyAnswerModel>;
    ip_key?: (null | string);
    survey_id: any;
    created: string;
};

