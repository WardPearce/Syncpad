/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type AccountKeychainModal = {
    /**
     * IV for cipher text, base64 encoded.
     */
    iv: string;
    /**
     * Locally encrypted 32 byte key for keychain, base64 encoded
     */
    cipher_text: string;
};

