/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CanaryModel } from '../models/CanaryModel';
import type { CreateCanaryModel } from '../models/CreateCanaryModel';
import type { CreateCanaryWarrantModel } from '../models/CreateCanaryWarrantModel';
import type { CreatedCanaryWarrantModel } from '../models/CreatedCanaryWarrantModel';
import type { PublicCanaryModel } from '../models/PublicCanaryModel';
import type { PublishCanaryWarrantModel } from '../models/PublishCanaryWarrantModel';
import type { PublishedCanaryWarrantModel } from '../models/PublishedCanaryWarrantModel';
import type { TrustedCanaryModel } from '../models/TrustedCanaryModel';

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
     * ListCanaries
     * List canaries for user
     * @returns CanaryModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryListListCanaries(): CancelablePromise<Array<CanaryModel>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/list',
        });
    }

    /**
     * ListTrustedCanaries
     * List trusted canaries
     * @returns TrustedCanaryModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryTrustedListListTrustedCanaries(): CancelablePromise<Record<string, TrustedCanaryModel>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/trusted/list',
        });
    }

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
     * @param hash
     * @param formData
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryWarrantWarrantIdDocumentHashUploadDocument(
        warrantId: string,
        hash: string,
        formData: Array<string>,
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

    /**
     * DeleteCanary
     * Delete a canary
     * @param domain
     * @param otp
     * @returns void
     * @throws ApiError
     */
    public controllersCanaryDomainDeleteDeleteCanary(
        domain: string,
        otp: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/canary/{domain}/delete',
            path: {
                'domain': domain,
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

    /**
     * PublicCanary
     * Get public details about canary
     * @param domain
     * @returns PublicCanaryModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryDomainPublicPublicCanary(
        domain: string,
    ): CancelablePromise<PublicCanaryModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/{domain}/public',
            path: {
                'domain': domain,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * GetTrusted
     * Get signed public key hash for a trusted canary
     * @param domain
     * @returns TrustedCanaryModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryDomainTrustedGetTrusted(
        domain: string,
    ): CancelablePromise<TrustedCanaryModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/{domain}/trusted',
            path: {
                'domain': domain,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * GetCanary
     * Get private details about a canary
     * @param domain
     * @returns CanaryModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryDomainGetCanary(
        domain: string,
    ): CancelablePromise<CanaryModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/{domain}',
            path: {
                'domain': domain,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * TrustCanary
     * Saves a canary as a trusted canary
     * @param domain
     * @param requestBody
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryDomainTrustedAddTrustCanary(
        domain: string,
        requestBody: TrustedCanaryModel,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/{domain}/trusted/add',
            path: {
                'domain': domain,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Verify
     * Verify domain ownership via DNS
     * @param domain
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryDomainVerifyVerify(
        domain: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/{domain}/verify',
            path: {
                'domain': domain,
            },
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
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryDomainLogoUpdateUpdateLogo(
        domain: string,
        formData: Array<string>,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
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

    /**
     * Unsubscribe
     * Unsubscribe from a canary
     * @param canaryId
     * @returns void
     * @throws ApiError
     */
    public controllersCanarySubscriptionCanaryIdUnsubscribeUnsubscribe(
        canaryId: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/canary/subscription/{canary_id}/unsubscribe',
            path: {
                'canary_id': canaryId,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Subscribe
     * Subscribe to a canary
     * @param canaryId
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanarySubscriptionCanaryIdSubscribeSubscribe(
        canaryId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/subscription/{canary_id}/subscribe',
            path: {
                'canary_id': canaryId,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * AmSubscribed
     * Check if user is subscribed to a canary
     * @param canaryId
     * @returns boolean Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanarySubscriptionCanaryIdAmSubscribed(
        canaryId: string,
    ): CancelablePromise<boolean> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/subscription/{canary_id}',
            path: {
                'canary_id': canaryId,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
