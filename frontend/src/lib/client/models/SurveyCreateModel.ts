/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SurveyDescriptionModel } from './SurveyDescriptionModel';
import type { SurveyKeypairModel } from './SurveyKeypairModel';
import type { SurveyQuestionModel } from './SurveyQuestionModel';
import type { SurveySecretKeyModel } from './SurveySecretKeyModel';
import type { SurveySignKeyPairModel } from './SurveySignKeyPairModel';
import type { TitleModel } from './TitleModel';

export type SurveyCreateModel = {
    title: TitleModel;
    description?: (null | SurveyDescriptionModel);
    questions: Array<SurveyQuestionModel>;
    signature: string;
    requires_login?: boolean;
    proxy_block?: boolean;
    allow_multiple_submissions?: boolean;
    requires_captcha?: boolean;
    hex_color?: (null | string);
    algorithms?: string;
    sign_keypair: SurveySignKeyPairModel;
    secret_key: SurveySecretKeyModel;
    keypair: SurveyKeypairModel;
};

