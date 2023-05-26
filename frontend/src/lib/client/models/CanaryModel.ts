/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CanaryEd25519Model } from './CanaryEd25519Model';
import type { DomainVerification } from './DomainVerification';

export type CanaryModel = {
    domain: string;
    about: string;
    keypair: CanaryEd25519Model;
    signature: string;
    algorithms?: string;
    _id: any;
    logo?: (null | string);
    user_id: any;
    created: string;
    domain_verification: DomainVerification;
};

