/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SubscriptionService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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
