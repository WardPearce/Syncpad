/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DescriptionModel } from './DescriptionModel';
import type { KeypairModel } from './KeypairModel';
import type { SecretKeyModel } from './SecretKeyModel';
import type { SignKeyPairModel } from './SignKeyPairModel';
import type { SurveyQuestionModel } from './SurveyQuestionModel';
import type { TitleModel } from './TitleModel';

export type SurveyModel = {
    title: TitleModel;
    description?: (null | DescriptionModel);
    questions: Array<SurveyQuestionModel>;
    signature: string;
    requires_login?: boolean;
    proxy_block?: boolean;
    allow_multiple_submissions?: boolean;
    created: string;
    _id: any;
    user_id: any;
    sign_keypair: SignKeyPairModel;
    keypair: KeypairModel;
    secret_key: SecretKeyModel;
};

