/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Documents } from '../models/Documents';
import type { Enabled } from '../models/Enabled';
import type { NotificationWebhooks } from '../models/NotificationWebhooks';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SettingsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Enabled
     * @returns Enabled Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSettingsEnabledEnabled(): CancelablePromise<Enabled> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/settings/enabled',
        });
    }

    /**
     * NotificationWebhooks
     * @returns NotificationWebhooks Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSettingsNotificationWebhooksNotificationWebhooks(): CancelablePromise<NotificationWebhooks> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/settings/notification/webhooks',
        });
    }

    /**
     * Documents
     * @returns Documents Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSettingsDocumentsDocuments(): CancelablePromise<Documents> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/settings/documents',
        });
    }

}
