/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SurveyCreateModel } from '../models/SurveyCreateModel';
import type { SurveyModel } from '../models/SurveyModel';
import type { SurveyPublicModel } from '../models/SurveyPublicModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SurveyService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * PublicSurvey
     * Get a survey
     * @param surveyId
     * @returns SurveyPublicModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSurveySurveyIdPublicPublicSurvey(
        surveyId: string,
    ): CancelablePromise<SurveyPublicModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/survey/{survey_id}/public',
            path: {
                'survey_id': surveyId,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * CreateSurvey
     * Create a survey
     * @param requestBody
     * @returns SurveyModel Document created, URL follows
     * @throws ApiError
     */
    public controllersSurveyCreateCreateSurvey(
        requestBody: SurveyCreateModel,
    ): CancelablePromise<SurveyModel> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/survey/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

}
