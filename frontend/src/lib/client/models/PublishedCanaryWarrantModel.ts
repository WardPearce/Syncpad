/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type PublishedCanaryWarrantModel = {
    _id: any;
    next_canary: string;
    issued: string;
    signature: string;
    btc_latest_block: string;
    statement?: string;
    file_hashes?: Record<string, any>;
    concern: PublishedCanaryWarrantModel.concern;
    canary_id: any;
    user_id: any;
    active: boolean;
};

export namespace PublishedCanaryWarrantModel {

    export enum concern {
        NONE = 'none',
        MILD = 'mild',
        MODERATE = 'moderate',
        SEVERE = 'severe',
    }


}

