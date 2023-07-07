/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DescriptionModel } from './DescriptionModel';
import type { KeypairModel } from './KeypairModel';
import type { SecretKeyModel } from './SecretKeyModel';
import type { SignKeyPairModel } from './SignKeyPairModel';
import type { SurveyQuestionModel } from './SurveyQuestionModel';
import type { TitleModel } from './TitleModel';

export type SurveyCreateModel = {
    title: TitleModel;
    description?: (null | DescriptionModel);
    questions: Array<SurveyQuestionModel>;
    signature: string;
    requires_login?: boolean;
    proxy_block?: boolean;
    allow_multiple_submissions?: boolean;
    sign_keypair: SignKeyPairModel;
    secret_key: SecretKeyModel;
    keypair: KeypairModel;
};

