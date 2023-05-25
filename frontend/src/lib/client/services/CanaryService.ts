/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CanaryModel } from '../models/CanaryModel';
import type { CreateCanaryModel } from '../models/CreateCanaryModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class CanaryService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * CreateCanary
     * Create a canary for a given domain
     * @param requestBody
     * @returns CanaryModel Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryCreateCreateCanary(
        requestBody: CreateCanaryModel,
    ): CancelablePromise<CanaryModel> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * UpdateLogo
     * Update logo for given domain
     * @param domain
     * @param formData
     * @returns any Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryDomainLogoUpdateUpdateLogo(
        domain: string,
        formData: Blob,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/controllers/canary/{domain}/logo/update',
            path: {
                'domain': domain,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
