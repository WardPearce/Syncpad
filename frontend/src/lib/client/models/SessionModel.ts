/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SessionLocationModel } from './SessionLocationModel';

export type SessionModel = {
    expires: string;
    record_kept_till: string;
    created: string;
    location: SessionLocationModel;
    device?: (null | string);
    user_id: any;
    _id: any;
};

