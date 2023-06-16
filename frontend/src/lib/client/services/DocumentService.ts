/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UploadDocumentCanaryWarrantModel } from '../models/UploadDocumentCanaryWarrantModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DocumentService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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

}
