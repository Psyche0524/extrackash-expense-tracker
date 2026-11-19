// Small page helpers. Every page still works without JavaScript.

// Calculator keypad on the Add screen: builds an expression in the amount box, = works it out.
const keypad = document.querySelector('.keypad');
if (keypad) {
  const input = document.getElementById(keypad.dataset.for);
  const solve = () => {
    const expr = input.value.replace(/%/g, '/100');
    if (!/^[\d+\-*/.() ]+$/.test(expr)) return;  // only numbers and + - * / . ( ), nothing else runs
    try {
      const result = Function(`"use strict"; return (${expr})`)();
      if (Number.isFinite(result)) input.value = Math.round(result * 100) / 100;
    } catch { /* half-typed expression: leave it for the user to fix */ }
  };
  keypad.addEventListener('click', (e) => {
    const k = e.target.dataset.k;
    if (!k) return;
    if (k === 'back') input.value = input.value.slice(0, -1);
    else if (k === 'clear') input.value = '';
    else if (k === '=') solve();
    else input.value += k;
  });
  input.form.addEventListener('submit', solve);
}

// Transfer: swap the From and To accounts, and show what arrives (amount; the fee is charged on top).
const swap = document.querySelector('[data-swap]');
if (swap) {
  const from = document.getElementById('id_account');
  const to = document.getElementById('id_to_account');
  swap.addEventListener('click', () => { [from.value, to.value] = [to.value, from.value]; });
  const amount = document.getElementById('id_amount');
  const receive = document.querySelector('[data-receive]');
  const show = () => {
    const n = parseFloat(amount.value) || 0;
    receive.textContent = '₱' + n.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };
  amount.addEventListener('input', show);
  show();
}

// Theme: System / Light / Dark picker in Settings. base.html applies it on load; this keeps it live.
const root = document.documentElement;
const systemDark = matchMedia('(prefers-color-scheme: dark)');
// The current choice lives in this variable; saving it is a bonus. Some browsers (VS Code's preview,
// private mode) block localStorage, and the picker must still switch the theme there.
let themePick = 'system';
try { themePick = localStorage.getItem('theme') || 'system'; } catch { /* blocked: keep 'system' */ }
const applyTheme = () => {
  const dark = themePick === 'dark' || (themePick === 'system' && systemDark.matches);
  root.dataset.theme = dark ? 'dark' : 'light';
  document.querySelector('meta[name=theme-color]').content = dark ? '#0c1411' : '#f3f7f4';
};
systemDark.addEventListener('change', applyTheme);  // follow the phone when it switches at sunset
const picker = document.querySelector('[data-theme-picker]');
if (picker) {
  picker.querySelector(`input[value="${themePick}"]`).checked = true;
  picker.addEventListener('change', (e) => {
    themePick = e.target.value;
    try { localStorage.setItem('theme', themePick); } catch { /* blocked: works until the page is left */ }
    applyTheme();
  });
}

// Close the + menu when tapping outside it.
document.addEventListener('click', (e) => {
  const fab = document.querySelector('.fab[open]');
  if (fab && !fab.contains(e.target)) fab.open = false;
});
