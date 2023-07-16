/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type SurveyAnswerModel = {
    id: number;
    answer: Array<string>;
    type: SurveyAnswerModel.type;
};

export namespace SurveyAnswerModel {

    export enum type {
        '_0' = 0,
        '_1' = 1,
        '_2' = 2,
        '_3' = 3,
    }


}

