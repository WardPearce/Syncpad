import { CanaryClient } from "./client";

import { request } from "./client/core/request";
import type { CancelablePromise } from "./client/core/CancelablePromise";
import type { ApiRequestOptions } from "./client/core/ApiRequestOptions";
import { FetchHttpRequest } from "./client/core/FetchHttpRequest";
import { getCookie } from "./misc";


class CSrfHttpRequest extends FetchHttpRequest {
    public override request<T>(options: ApiRequestOptions): CancelablePromise<T> {
        let csrfToken = getCookie("csrftoken");
        if (csrfToken !== undefined) {
            if (this.config.HEADERS === undefined)
                this.config.HEADERS = {};

            this.config.HEADERS["x-csrftoken"] = csrfToken;
        }
        return request(this.config, options);
    }
}


export const client = new CanaryClient({
    BASE: import.meta.env.VITE_API_URL
}, CSrfHttpRequest)
