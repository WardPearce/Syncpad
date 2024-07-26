/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class PrivacyService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * IpProgressing
     * @returns void
     * @throws ApiError
     */
    public controllersAccountPrivacyIpProgressingDisallowIpProgressing(): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/account/privacy/ip-progressing/disallow',
        });
    }

    /**
     * IpProgressingConsent
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountPrivacyIpProgressingConsentIpProgressingConsent(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/privacy/ip-progressing/consent',
        });
    }

}
