export function concat(value: string, maxLength: number = 18): string {
    return value.length > maxLength ? `${value.substring(0, maxLength)}...` : value
}

export function timeout(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function getCookie(name: string): string {
  let match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  if (match) return match[2];
}