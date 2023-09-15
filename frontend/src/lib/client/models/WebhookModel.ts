/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type WebhookModel = {
    url: any;
    type: WebhookModel.type;
};

export namespace WebhookModel {

    export enum type {
        CANARY_RENEWALS = 'canary_renewals',
        CANARY_SUBSCRIPTIONS = 'canary_subscriptions',
        SURVEY_SUBMISSIONS = 'survey_submissions',
    }


}

