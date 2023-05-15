/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Argon2Modal } from '../models/Argon2Modal';
import type { CreateUserModel } from '../models/CreateUserModel';
import type { UserLoginSignatureModel } from '../models/UserLoginSignatureModel';
import type { UserModel } from '../models/UserModel';
import type { UserToSignModel } from '../models/UserToSignModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AccountService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Kdf
     * Public KDF details
     * @param email
     * @returns Argon2Modal Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersAccountEmailKdfKdf(
        email: string,
    ): CancelablePromise<Argon2Modal> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/account/{email}/kdf',
            path: {
                'email': email,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Login
     * Validate signature and OTP code
     * @param captcha
     * @param email
     * @param requestBody
     * @param otp
     * @returns UserModel Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountEmailLoginLogin(
        captcha: string,
        email: string,
        requestBody: UserLoginSignatureModel,
        otp?: (null | string),
    ): CancelablePromise<UserModel> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/{email}/login',
            path: {
                'email': email,
            },
            query: {
                'captcha': captcha,
                'otp': otp,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * ToSign
     * Used to generate a unique code to sign.
     * @param email
     * @returns UserToSignModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersAccountEmailToSignToSign(
        email: string,
    ): CancelablePromise<UserToSignModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/account/{email}/to-sign',
            path: {
                'email': email,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * CreateAccount
     * @param captcha
     * @param requestBody
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountCreateCreateAccount(
        captcha: string,
        requestBody: CreateUserModel,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/create',
            query: {
                'captcha': captcha,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
