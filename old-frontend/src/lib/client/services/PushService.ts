/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NftyNotificationModel } from '../models/NftyNotificationModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class PushService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * AddPush
     * Generate push notification topic
     * @param requestBody
     * @returns NftyNotificationModel Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountNotificationsPushAddAddPush(
        requestBody: string,
    ): CancelablePromise<NftyNotificationModel> {
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
     * ListPush
     * List topics
     * @returns NftyNotificationModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersAccountNotificationsPushListListPush(): CancelablePromise<Record<string, NftyNotificationModel>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/account/notifications/push/list',
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
        requestBody: string,
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
