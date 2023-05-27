/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CanaryEd25519Model } from './CanaryEd25519Model';

export type DomainVerification = {
    domain: string;
    about: string;
    signature: string;
    algorithms?: string;
    keypair: CanaryEd25519Model;
    completed?: boolean;
    code: string;
    code_prefixed?: string;
};

