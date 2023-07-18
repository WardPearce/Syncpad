/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type SurveySecretKeyModel = {
    /**
     * IV for cipher text, base64 encoded.
     */
    iv: string;
    /**
     * Xchacha20 secret key, encrypted with keychain, base64 encoded
     */
    cipher_text: string;
};

