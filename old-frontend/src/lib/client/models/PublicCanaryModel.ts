/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PublicKeyModel } from './PublicKeyModel';

export type PublicCanaryModel = {
    domain: string;
    about: string;
    signature: string;
    /**
     * Algorithms used for canary
     */
    algorithms?: string;
    hex_color?: (null | string);
    id: any;
    logo?: (null | string);
    user_id: any;
    created: string;
    keypair: PublicKeyModel;
};

