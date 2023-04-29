export function concat(value: string, maxLength: number = 18): string {
    return value.length > maxLength ? `${value.substring(0, maxLength)}...` : value
}
