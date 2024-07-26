/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type UserLoginSignatureModel = {
    /**
     * to_sign signed with ed25519 private key, base64 encoded
     */
    signature: string;
    /**
     * Overwrites the default JWT expire days to only one day
     */
    one_day_login?: boolean;
    _id: string;
};

