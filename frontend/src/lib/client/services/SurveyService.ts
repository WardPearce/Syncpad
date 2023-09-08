/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubmitSurveyModel } from '../models/SubmitSurveyModel';
import type { SurveyCreateModel } from '../models/SurveyCreateModel';
import type { SurveyModel } from '../models/SurveyModel';
import type { SurveyPublicModel } from '../models/SurveyPublicModel';
import type { SurveyResultModel } from '../models/SurveyResultModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SurveyService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * GetResponse
     * Get a survey response
     * @param surveyId
     * @param page
     * @returns SurveyResultModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSurveySurveyIdResponsesPageGetResponse(
        surveyId: string,
        page: number,
    ): CancelablePromise<SurveyResultModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/survey/{survey_id}/responses/{page}',
            path: {
                'survey_id': surveyId,
                'page': page,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * CloseSurvey
     * Closes survey submission, also clears IP hashes
     * @param surveyId
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersSurveySurveyIdCloseCloseSurvey(
        surveyId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/survey/{survey_id}/close',
            path: {
                'survey_id': surveyId,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * StreamResponses
     * Stream survey responses using ndjson (not realtime)
     * @param surveyId
     * @returns string Stream Response
     * @throws ApiError
     */
    public controllersSurveySurveyIdResponsesStreamResponses(
        surveyId: string,
    ): CancelablePromise<string> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/survey/{survey_id}/responses',
            path: {
                'survey_id': surveyId,
            },
            responseHeader: 'content-length',
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * PublicSurvey
     * Get a survey public details
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
     * GetSurvey
     * Get a survey
     * @param surveyId
     * @returns SurveyModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSurveySurveyIdGetSurvey(
        surveyId: string,
    ): CancelablePromise<SurveyModel> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/survey/{survey_id}',
            path: {
                'survey_id': surveyId,
            },
            errors: {
                400: `Bad request syntax or unsupported method`,
            },
        });
    }

    /**
     * SubmitSurvey
     * Submit answers to a survey
     * @param surveyId
     * @param requestBody
     * @param captcha
     * @returns any Document created, URL follows
     * @throws ApiError
     */
    public controllersSurveySurveyIdSubmitSubmitSurvey(
        surveyId: string,
        requestBody: SubmitSurveyModel,
        captcha?: (null | string),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/controllers/survey/{survey_id}/submit',
            path: {
                'survey_id': surveyId,
            },
            query: {
                'captcha': captcha,
            },
            body: requestBody,
            mediaType: 'application/json',
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

    /**
     * ListSurveys
     * List surveys
     * @returns SurveyModel Request fulfilled, document follows
     * @throws ApiError
     */
    public controllersSurveyListListSurveys(): CancelablePromise<Array<SurveyModel>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/controllers/survey/list',
        });
    }

}
