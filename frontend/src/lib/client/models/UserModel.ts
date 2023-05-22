/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AccountEd25199Modal } from './AccountEd25199Modal';
import type { AccountKeychainModal } from './AccountKeychainModal';
import type { Argon2Modal } from './Argon2Modal';
import type { OtpModel } from './OtpModel';

export type UserModel = {
    email: string;
    auth: AccountEd25199Modal;
    keychain: AccountKeychainModal;
    kdf: Argon2Modal;
    signature: string;
    algorithms?: string;
    _id: any;
    otp: OtpModel;
    email_verified?: boolean;
};

