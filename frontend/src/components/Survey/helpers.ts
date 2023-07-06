export function selectOnClick(event: Event) {
  const inputElement = event.target as HTMLInputElement;
  inputElement.select();
}
