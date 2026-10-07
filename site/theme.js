// Tema claro / oscuro. Se carga en <head> para aplicar el tema antes de pintar la página.
// Sin elección guardada se sigue la preferencia del sistema; el botón alterna y la recuerda.
(() => {
  const KEY = 'qiskit:theme';
  const sys = () => matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved) document.documentElement.dataset.theme = saved;
  const current = () => document.documentElement.dataset.theme || sys();
  const label = () => current() === 'light' ? '☾' : '☀';
  window.toggleTheme = () => {
    const next = current() === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem(KEY, next); } catch (e) {}
    document.querySelectorAll('.theme-btn').forEach(b => { b.textContent = label(); b.title = 'Cambiar a tema ' + (current() === 'light' ? 'oscuro' : 'claro'); });
    dispatchEvent(new Event('themechange'));
  };
  addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.theme-btn').forEach(b => { b.textContent = label(); b.title = 'Cambiar a tema ' + (current() === 'light' ? 'oscuro' : 'claro'); b.onclick = window.toggleTheme; });
  });
  matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
    if (!document.documentElement.dataset.theme) dispatchEvent(new Event('themechange'));
  });
})();
