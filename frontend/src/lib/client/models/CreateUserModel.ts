/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AccountAuthModal } from './AccountAuthModal';
import type { AccountEd25199Modal } from './AccountEd25199Modal';
import type { AccountKeychainModal } from './AccountKeychainModal';
import type { AccountX25519Model } from './AccountX25519Model';
import type { Argon2Modal } from './Argon2Modal';

export type CreateUserModel = {
    email: string;
    auth: AccountAuthModal;
    keypair: AccountX25519Model;
    sign_keypair: AccountEd25199Modal;
    keychain: AccountKeychainModal;
    kdf: Argon2Modal;
    ip_lookup_consent?: boolean;
    signature: string;
    algorithms?: string;
};

