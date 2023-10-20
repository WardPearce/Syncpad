/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type NotificationsModel = {
    email: Array<string>;
    webhooks: Record<string, Array<string>>;
    push?: Record<string, string>;
};

