/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CanaryEd25519Model } from './CanaryEd25519Model';

export type CreateCanaryModel = {
    domain: string;
    about: string;
    keypair: CanaryEd25519Model;
    algorithms?: string;
};

