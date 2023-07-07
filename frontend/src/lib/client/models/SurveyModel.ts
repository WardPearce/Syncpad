/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SurveyDescriptionModel } from './SurveyDescriptionModel';
import type { SurveyPublicKeyModel } from './SurveyPublicKeyModel';
import type { SurveyQuestionModel } from './SurveyQuestionModel';
import type { SurveySecretKeyModel } from './SurveySecretKeyModel';
import type { SurveySignPublicKeyModel } from './SurveySignPublicKeyModel';
import type { TitleModel } from './TitleModel';

export type SurveyModel = {
    title: TitleModel;
    description?: (null | SurveyDescriptionModel);
    questions: Array<SurveyQuestionModel>;
    signature: string;
    requires_login?: boolean;
    proxy_block?: boolean;
    allow_multiple_submissions?: boolean;
    sign_keypair: SurveySignPublicKeyModel;
    secret_key: SurveySecretKeyModel;
    keypair: SurveyPublicKeyModel;
    created: string;
    _id: any;
    user_id: any;
};

