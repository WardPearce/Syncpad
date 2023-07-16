/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CanaryEd25519Model } from './CanaryEd25519Model';
import type { DomainVerification } from './DomainVerification';

export type CanaryModel = {
    domain: string;
    about: string;
    signature: string;
    algorithms?: string;
    hex_color?: (null | string);
    _id: any;
    logo?: (null | string);
    user_id: any;
    created: string;
    keypair: CanaryEd25519Model;
    domain_verification: DomainVerification;
};

