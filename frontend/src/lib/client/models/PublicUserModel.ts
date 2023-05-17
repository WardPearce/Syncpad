/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Argon2Modal } from './Argon2Modal';

export type PublicUserModel = {
    kdf: Argon2Modal;
    otp_completed?: boolean;
};

