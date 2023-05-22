/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AccountEd25199Modal } from './AccountEd25199Modal';
import type { AccountKeychainModal } from './AccountKeychainModal';
import type { AccountX25519Model } from './AccountX25519Model';
import type { Argon2Modal } from './Argon2Modal';

export type CreateUserModel = {
    email: string;
    auth: AccountEd25199Modal;
    keypair: AccountX25519Model;
    keychain: AccountKeychainModal;
    kdf: Argon2Modal;
    ip_lookup_consent?: boolean;
    signature: string;
    algorithms?: string;
};

