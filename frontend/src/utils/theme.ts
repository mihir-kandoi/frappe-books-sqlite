export function setDarkMode(darkMode: boolean): void {
  document.documentElement.dataset.theme = darkMode ? 'dark' : 'light';

  if (darkMode) {
    document.documentElement.classList.add(
      'dark',
      'custom-scroll',
      'custom-scroll-thumb1'
    );
    return;
  }
  document.documentElement.classList.remove('dark');
}
