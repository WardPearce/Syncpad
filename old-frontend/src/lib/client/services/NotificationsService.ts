/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NftyNotificationModel } from '../models/NftyNotificationModel';
import type { WebhookModel } from '../models/WebhookModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class NotificationsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * AddWebhook
     * Add a webhook
     * @param requestBody
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountNotificationsWebhookAddAddWebhook(
        requestBody: WebhookModel,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/notifications/webhook/add',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * RemoveWebhook
     * Remove a webhook
     * @param requestBody
     * @returns void
     * @throws ApiError
     */
    public controllersAccountNotificationsWebhookRemoveRemoveWebhook(
        requestBody: WebhookModel,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/account/notifications/webhook/remove',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * AddEmail
     * Enable email notification
     * @param requestBody
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersAccountNotificationsEmailAddAddEmail(
        requestBody: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/account/notifications/email/add',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * RemoveEmail
     * Disable email notification
     * @param requestBody
     * @returns void
     * @throws ApiError
     */
    public controllersAccountNotificationsEmailRemoveRemoveEmail(
        requestBody: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/controllers/account/notifications/email/remove',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

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
