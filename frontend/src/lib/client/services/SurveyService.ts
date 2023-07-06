/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SurveyCreateModel } from '../models/SurveyCreateModel';
import type { SurveyModel } from '../models/SurveyModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SurveyService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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
