/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionModel } from '../models/SessionModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SessionService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * GetSessions
     * List active sessions
     * @returns SessionModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSessionGetSessions(): CancelablePromise<Array<SessionModel>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/session',
        });
    }

}
