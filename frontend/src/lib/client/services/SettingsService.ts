/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Documents } from '../models/Documents';
import type { Enabled } from '../models/Enabled';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SettingsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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

}
