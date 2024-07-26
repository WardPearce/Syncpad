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
    type: SurveyQuestionModel.type;
};

export namespace SurveyQuestionModel {

    export enum type {
        '_0' = 0,
        '_1' = 1,
        '_2' = 2,
        '_3' = 3,
    }


}

