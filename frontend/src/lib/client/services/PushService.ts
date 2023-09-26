/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NftyNotification } from '../models/NftyNotification';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class PushService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * AddPush
     * Generate push notification topic
     * @param requestBody
     * @returns NftyNotification Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountNotificationsPushAddAddPush(
        requestBody: 'canary_renewals' | 'canary_subscriptions' | 'survey_submissions',
    ): CancelablePromise<NftyNotification> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/notifications/push/add',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * RemovePush
     * Remove a push notification
     * @param requestBody
     * @returns void
     * @throws ApiError
     */
    public controllersAccountNotificationsPushRemoveRemovePush(
        requestBody: 'canary_renewals' | 'canary_subscriptions' | 'survey_submissions',
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/account/notifications/push/remove',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
