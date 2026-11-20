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
const savedTheme = () => { try { return localStorage.getItem('theme') || 'system'; } catch { return 'system'; } };
const applyTheme = () => {
  const pick = savedTheme();
  const dark = pick === 'dark' || (pick === 'system' && systemDark.matches);
  root.dataset.theme = dark ? 'dark' : 'light';
  document.querySelector('meta[name=theme-color]').content = dark ? '#0c1411' : '#f3f7f4';
};
systemDark.addEventListener('change', applyTheme);  // follow the phone when it switches at sunset
const picker = document.querySelector('[data-theme-picker]');
if (picker) {
  picker.querySelector(`input[value="${savedTheme()}"]`).checked = true;
  picker.addEventListener('change', (e) => {
    try { localStorage.setItem('theme', e.target.value); } catch { /* private mode: applies for this page only */ }
    applyTheme();
  });
}

document.addEventListener('click', (e) => {
  const fab = document.querySelector('.fab[open]');
  if (fab && !fab.contains(e.target)) fab.open = false;
});

document.querySelectorAll('.password-toggle').forEach((button) => {
  button.addEventListener('click', () => {
    const wrapper = button.closest('.password-wrapper');
    const input = wrapper.querySelector('input');

    const isHidden = input.type === 'password';

    input.type = isHidden ? 'text' : 'password';

    button.setAttribute(
      'aria-label',
      isHidden ? 'Hide password' : 'Show password'
    );

    button.setAttribute('aria-pressed', String(isHidden));
  });
});

document.querySelectorAll('.toggle-password').forEach((button) => {
  button.addEventListener('click', () => {
    const wrapper = button.closest('.password-field');
    const input = wrapper.querySelector('input');

    const isPassword = input.type === 'password';

    input.type = isPassword ? 'text' : 'password';

    button.setAttribute(
      'aria-label',
      isPassword ? 'Hide password' : 'Show password'
    );

    button.setAttribute('aria-pressed', isPassword);

    button.innerHTML = isPassword
      ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2">
           <path d="M3 3l18 18"/>
           <path d="M10.6 10.6a2 2 0 002.8 2.8"/>
           <path d="M9.9 5.2A11 11 0 0112 5c6.5 0 10 7 10 7a16 16 0 01-4 4.5"/>
           <path d="M6.2 6.2C3.5 8 2 12 2 12s3.5 7 10 7c1 0 2-.2 2.9-.5"/>
         </svg>`
      : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2">
           <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/>
           <circle cx="12" cy="12" r="3"/>
         </svg>`;
  });
});