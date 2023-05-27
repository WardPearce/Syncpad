/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PublicKeyModel } from './PublicKeyModel';

export type PublicCanaryModel = {
    domain: string;
    about: string;
    signature: string;
    algorithms?: string;
    _id: any;
    logo?: (null | string);
    user_id: any;
    created: string;
    keypair: PublicKeyModel;
};

