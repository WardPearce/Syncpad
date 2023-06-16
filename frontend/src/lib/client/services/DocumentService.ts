/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DocumentService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * UploadDocument
     * Upload a canary warrant document
     * @param warrantId
     * @param hash
     * @param formData
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryWarrantWarrantIdDocumentHashUploadDocument(
        warrantId: string,
        hash: string,
        formData: Array<Blob>,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/warrant/{warrant_id}/document/{hash_}',
            path: {
                'warrant_id': warrantId,
                'hash_': hash,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
