/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type CreateCanaryWarrantModel = {
    next: CreateCanaryWarrantModel.next;
};

export namespace CreateCanaryWarrantModel {

    export enum next {
        TOMORROW = 'tomorrow',
        WEEK = 'week',
        FORTNIGHT = 'fortnight',
        MONTH = 'month',
        QUARTER = 'quarter',
        YEAR = 'year',
    }


}

