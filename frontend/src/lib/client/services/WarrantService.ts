/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateCanaryWarrantModel } from '../models/CreateCanaryWarrantModel';
import type { CreatedCanaryWarrantModel } from '../models/CreatedCanaryWarrantModel';
import type { PublishCanaryWarrantModel } from '../models/PublishCanaryWarrantModel';
import type { PublishedCanaryWarrantModel } from '../models/PublishedCanaryWarrantModel';
import type { UploadDocumentCanaryWarrantModel } from '../models/UploadDocumentCanaryWarrantModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class WarrantService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * PublishedWarrant
     * Get a canary warrant
     * @param canaryId
     * @param page
     * @returns PublishedCanaryWarrantModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryPublishedCanaryIdPagePublishedWarrant(
        canaryId: string,
        page: number,
    ): CancelablePromise<PublishedCanaryWarrantModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/published/{canary_id}/{page}',
            path: {
                'canary_id': canaryId,
                'page': page,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Publish
     * Publish a canary
     * @param warrantId
     * @param requestBody
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryWarrantWarrantIdPublishPublish(
        warrantId: string,
        requestBody: PublishCanaryWarrantModel,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/warrant/{warrant_id}/publish',
            path: {
                'warrant_id': warrantId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * UploadDocument
     * Upload a canary warrant document
     * @param warrantId
     * @param formData
     * @returns any Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryWarrantWarrantIdDocumentUploadDocument(
        warrantId: string,
        formData: Array<UploadDocumentCanaryWarrantModel>,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/controllers/canary/warrant/{warrant_id}/document',
            path: {
                'warrant_id': warrantId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * CreateWarrant
     * Create a warrant for a canary
     * @param domain
     * @param otp
     * @param requestBody
     * @returns CreatedCanaryWarrantModel Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryDomainCreateWarrantCreateWarrant(
        domain: string,
        otp: string,
        requestBody: CreateCanaryWarrantModel,
    ): CancelablePromise<CreatedCanaryWarrantModel> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/{domain}/create/warrant',
            path: {
                'domain': domain,
            },
            query: {
                'otp': otp,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
