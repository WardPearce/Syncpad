/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AccountEd25199Modal } from './AccountEd25199Modal';
import type { AccountKeychainModal } from './AccountKeychainModal';
import type { Argon2Modal } from './Argon2Modal';

export type CreateUserModel = {
    email: string;
    auth: AccountEd25199Modal;
    keychain: AccountKeychainModal;
    kdf: Argon2Modal;
    signature: string;
    algorithms?: string;
};

