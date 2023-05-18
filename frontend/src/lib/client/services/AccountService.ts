/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateUserModel } from '../models/CreateUserModel';
import type { PublicUserModel } from '../models/PublicUserModel';
import type { UserLoginSignatureModel } from '../models/UserLoginSignatureModel';
import type { UserModel } from '../models/UserModel';
import type { UserToSignModel } from '../models/UserToSignModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AccountService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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
                401: `No permission -- see authorization schemes`,
            },
        });
    }

    /**
     * Logout
     * Logout of User account
     * @returns any Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersAccountEmailLogoutLogout(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/account/{email}/logout',
        });
    }

    /**
     * OtpSetup
     * Used to confirm OTP is completed
     * @param email
     * @param otp
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountEmailSetupOtpOtpSetup(
        email: string,
        otp: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/{email}/setup/otp',
            path: {
                'email': email,
            },
            query: {
                'otp': otp,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Public
     * Public KDF details
     * @param email
     * @returns PublicUserModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersAccountEmailPublicPublic(
        email: string,
    ): CancelablePromise<PublicUserModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/account/{email}/public',
            path: {
                'email': email,
            },
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
                404: `Nothing matches the given URI`,
            },
        });
    }

    /**
     * CreateAccount
     * Create a user account
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
