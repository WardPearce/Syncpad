/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DocumentCanaryWarrantModel } from './DocumentCanaryWarrantModel';

export type PublishedCanaryWarrantModel = {
    id: any;
    next_canary: string;
    issued: string;
    /**
     * Hash signature, base64 encoded
     */
    signature: string;
    btc_latest_block: string;
    statement?: string;
    concern: PublishedCanaryWarrantModel.concern;
    canary_id: any;
    user_id: any;
    active: boolean;
    documents: Array<DocumentCanaryWarrantModel>;
};

export namespace PublishedCanaryWarrantModel {

    export enum concern {
        NONE = 'none',
        MILD = 'mild',
        MODERATE = 'moderate',
        SEVERE = 'severe',
    }


}

