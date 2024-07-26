/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type AccountEd25199Modal = {
    /**
     * IV for cipher text, base64 encoded.
     */
    iv: string;
    /**
     * ed25519 public key, base64 encoded
     */
    public_key: string;
    /**
     * ed25519 private key, encrypted with keychain, base64 encoded
     */
    cipher_text: string;
};

