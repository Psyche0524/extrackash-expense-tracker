# Architecture

Extrackash is one Django project (`config/`) with one app per feature (`apps/`).

## How the apps depend on each other

```text
                  core  (helpers, template tags, base form widgets, seed_demo)
                   ▲
 transactions ◄── wallets ◄── debts
      ▲             ▲
      └── planning ─┘        investments   households   reports   dashboard
```

- `transactions.Transaction` is the centre: every expense, income and transfer.
- `wallets.Account` computes its balance from transactions. `Transaction.account` points back with a string
  reference (`'wallets.Account'`) so the two modules don't import each other in a loop.
- `planning`, `debts`, `dashboard` and `reports` read transactions; they don't own them.
- `core` depends on nothing in `apps/`, so any app can import from it.

## Models by app

| App | Models |
|---|---|
| transactions | `Transaction` (+ built-in expense and income categories) |
| wallets | `Account` (bank, e-wallet, cash, credit card) |
| planning | `Budget`, `Goal`, `Contribution`, `PlannedPayment`, `Trip` |
| debts | `Debt` (installment, loan, money owed to me) |
| investments | `Investment` |
| households | `Household` |
| accounts, dashboard, reports, system_settings | none (Django's `User` + other apps' models) |

## URLs

Each app has `urls.py`; `config/urls.py` includes them all at the site root. URL names are global
(no namespaces), so templates link with `{% url 'home' %}`, `{% url 'add' %}`, and so on.

## Templates and static files

All templates live in one folder, one file per screen:

```text
templates/
├── components/        navbar.html (tab bar + add menu), popups.html (toasts), page_header.html,
│                      form_field.html, mini_bars.html, transaction_row.html, plan_tabs.html
├── base.html          page frame: head, theme script, popups, content, navbar
├── form.html          every simple add/edit form
└── welcome, signup, login, setup, ready, home, history, add, transaction, wallet, cards,
    transfer, plan, budgets, budget, goals, goal, cashflow, planned, travel, tags, debts,
    investments, reports, shared, settings, delete_account (.html)
```

Views render pages by file name, e.g. `render(request, 'wallet.html', ...)`; pages include components with
`{% include 'components/transaction_row.html' %}`.

Static files:

- Static: `static/css/style.css` (design tokens, light + dark), `static/js/app.js`,
  `static/icons/<name>.svg` (one file per icon, used via `{% icon 'name' %}`; add a file there to add an icon),
  `static/images/mascot-half.png`.

## Security notes

- Every page except welcome/sign up/log in needs a login; every query is filtered by `request.user`.
- Receipt photos are served only through `transactions.views.transaction_photo`, after an ownership check.
- Secrets come from environment variables (see `.env.example`).
