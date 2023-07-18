/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type Argon2Modal = {
    /**
     * Salt used for deriving account key, base64 encoded
     */
    salt: string;
    /**
     * Time cost
     */
    time_cost?: number;
    /**
     * Memory cost
     */
    memory_cost?: number;
};

