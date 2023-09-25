/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DefaultService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * CsrfGet
     * Get a CSRF token to use in later requests
     * @returns any Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCsrfCsrfGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/csrf',
        });
    }

}
