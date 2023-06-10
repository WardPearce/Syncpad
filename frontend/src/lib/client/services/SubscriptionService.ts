/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SubscriptionService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * AmSubscribed
     * Check if user is subscribed to a canary
     * @param domain
     * @returns boolean Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersCanaryDomainSubscriptionsAmAmSubscribed(
        domain: string,
    ): CancelablePromise<boolean> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/canary/{domain}/subscriptions/am',
            path: {
                'domain': domain,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Subscribe
     * Subscribe to a canary
     * @param domain
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersCanaryDomainSubscriptionSubscribeSubscribe(
        domain: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/canary/{domain}/subscription/subscribe',
            path: {
                'domain': domain,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * Unsubscribe
     * Unsubscribe from a canary
     * @param domain
     * @returns void
     * @throws ApiError
     */
    public controllersCanaryDomainSubscriptionUnsubscribeUnsubscribe(
        domain: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/canary/{domain}/subscription/unsubscribe',
            path: {
                'domain': domain,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
