/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type AccountX25519Model = {
    /**
     * IV for cipher text, base64 encoded.
     */
    iv: string;
    /**
     * X25519 public key, base64 encoded
     */
    public_key: string;
    /**
     * X25519 private key, encrypted with keychain, base64 encoded
     */
    cipher_text: string;
};

