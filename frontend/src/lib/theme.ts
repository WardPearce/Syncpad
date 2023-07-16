export async function getDynamicTheme(mode?: string): Promise<Record<string, string>> {
  const themes: string = await window.ui("theme")[mode ? mode : (ui("mode") as string)];
  let themeVars = {};
  themes.split(";").forEach(keyVar => {
    let [key, value] = keyVar.split(":");
    themeVars[key] = value;
  });
  return themeVars;
}


export function getCurrentThemePrimary(): string {
  let themeColor = import.meta.env.VITE_THEME;

  try {
    const themeLocalStorage = localStorage.getItem("theme");
    if (themeLocalStorage) {
      themeColor = themeLocalStorage;
    }
  } catch { }

  return themeColor;
}
