import sodium from "libsodium-wrappers-sumo";

export function base64Decode(input: string): Uint8Array {
    return sodium.from_base64(input, sodium.base64_variants.ORIGINAL);
}

export function base64Encode(input: string | Uint8Array): string {
    return sodium.to_base64(input, sodium.base64_variants.ORIGINAL);
}

export function utf8Encode(input: string): Uint8Array {
    return new TextEncoder().encode(input);
}

export function utf8Decode(input: Uint8Array): string {
    return new TextDecoder().decode(input);
}

export function rawEncoder(toEncode: Uint8Array): Uint8Array {
    return toEncode;
}
