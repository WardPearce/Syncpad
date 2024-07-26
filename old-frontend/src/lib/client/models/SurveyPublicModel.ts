/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SurreyCreateIpModel } from './SurreyCreateIpModel';
import type { SurveyDescriptionModel } from './SurveyDescriptionModel';
import type { SurveyPublicKeyModel } from './SurveyPublicKeyModel';
import type { SurveyQuestionModel } from './SurveyQuestionModel';
import type { SurveySignPublicKeyModel } from './SurveySignPublicKeyModel';
import type { TitleModel } from './TitleModel';

export type SurveyPublicModel = {
    title: TitleModel;
    description?: (null | SurveyDescriptionModel);
    questions: Array<SurveyQuestionModel>;
    signature: string;
    requires_login?: boolean;
    proxy_block?: boolean;
    allow_multiple_submissions?: boolean;
    closed?: (boolean | string);
    requires_captcha?: boolean;
    hex_color?: (null | string);
    /**
     * Encryption algorithms used for survey
     */
    algorithms?: string;
    created: string;
    id: any;
    user_id: any;
    sign_keypair: SurveySignPublicKeyModel;
    keypair: SurveyPublicKeyModel;
    ip?: (null | SurreyCreateIpModel);
};

