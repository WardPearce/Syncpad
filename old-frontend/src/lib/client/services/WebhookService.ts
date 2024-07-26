/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WebhookModel } from '../models/WebhookModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class WebhookService {

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

}
