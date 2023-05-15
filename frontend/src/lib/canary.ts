import { CanaryClient } from "./client";

export const client = new CanaryClient({
    BASE: import.meta.env.VITE_API_URL
})