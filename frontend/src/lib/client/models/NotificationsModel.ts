/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type NotificationsModel = {
    email: Array<'canary_renewals' | 'canary_subscriptions' | 'survey_submissions'>;
    webhooks: Record<string, Array<string>>;
};

