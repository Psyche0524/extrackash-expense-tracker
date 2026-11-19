# Extrackash – Expense Tracker

**Track your expenses. Grow your savings.**
A mobile-first web app for logging income and spending, managing wallets, budgets and goals, and seeing what's ahead.
Built by a team of 3 with Django, HTML, CSS and JavaScript.
Design: [Figma](https://www.figma.com/design/E1OFOlFfNvk1xL3djQGqXV/Untitled?node-id=0-1)

## Main features

| Area | What you can do |
|---|---|
| Accounts | Sign up with name + email, log in, first-account setup, edit profile |
| Dashboard | Greeting with insight, last-7-days spending, payments due, monthly forecast |
| Transactions | Add expense/income with calculator keypad, category chips (+ your own), time, receipt photo, tags; history grouped by day with search and filters |
| Wallets | GCash, Maya, banks, cash and credit cards as coloured cards; net worth (assets − liabilities); groups; transfers (incl. outside accounts and fees) |
| Planning | Budgets (daily → yearly), goals, planned/recurring payments, travel, tags, 30-day cashflow |
| Debts | Loans, installments and money owed to you, with "record payment" |
| Investments | Holdings, portfolio value and gain |
| Reports | Week / month / year by category, 6-month chart, CSV export |
| Households | Shared spending with an equal split |
| System settings | Appearance (System / Light / Dark), export, delete account |

## Technology stack

| Part | Tech |
|---|---|
| Backend | Python 3.12+, Django 5.2 |
| Frontend | Django templates, HTML, CSS (one design system), small vanilla JavaScript |
| Database | SQLite for development |
| Design | Figma (exports kept locally in `Figma Design/`, not committed) |
| CI | GitHub Actions runs the test suite on every pull request |

## Repository structure

```text
extrackash-expense-tracker/
├── apps/                    One Django app per feature
│   ├── accounts/            Sign up, log in, set up, profile
│   ├── dashboard/           Home screen
│   ├── transactions/        Expenses & income, history, receipts
│   ├── wallets/             Accounts/wallets, cards, transfers
│   ├── planning/            Budgets, goals, planned payments, travel, tags, cashflow
│   ├── debts/               Loans, installments, money owed to you
│   ├── investments/         Holdings
│   ├── reports/             Reports and CSV export
│   ├── households/          Shared finances
│   ├── system_settings/     Settings, appearance, delete account
│   └── core/                Shared helpers, {% icon %} and |peso tags, seed_demo
├── config/                  Django settings and root URLs
├── templates/               Shared layouts (base.html, form.html, partials)
├── static/
│   ├── css/                 style.css (design system, light + dark)
│   ├── js/                  app.js
│   ├── icons/               icons.svg (line-icon sprite)
│   ├── images/              logo, mascot
│   └── fonts/               (Plus Jakarta Sans loads from Google Fonts)
├── docs/                    Architecture notes
├── tests/                   Test suite
├── .github/                 CI workflow, issue and PR templates
├── CONTRIBUTING.md          Team workflow
├── requirements.txt
└── manage.py
```

Each feature app follows the same layout: `models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`,
`migrations/` and `templates/<app>/`. See [docs/architecture.md](docs/architecture.md) for how they connect.

## Installation (Windows)

```bash
git clone https://github.com/Psyche0524/extrackash-expense-tracker.git
cd extrackash-expense-tracker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux: use `source .venv/bin/activate`.

## Database setup

```bash
python manage.py migrate
python manage.py seed_demo          # optional: demo account with sample data (prints the login)
python manage.py createsuperuser    # optional: for /admin
```

`db.sqlite3` is local to each developer and is never committed.

## Run the app

```bash
python manage.py runserver 0.0.0.0:8000
```

- On your PC: http://127.0.0.1:8000 (press F12 → Ctrl+Shift+M for phone view)
- On your phone (same Wi-Fi): `http://YOUR-PC-IP:8000` (find the IP with `ipconfig`)

Run the tests before every pull request:

```bash
python manage.py test
```

## Environment variables

Development needs none. For deployment, copy the names from [.env.example](.env.example) and set them on the server:
`DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`.

## Team

| Developer | Area | Apps |
|---|---|---|
| Developer 1 – Psyche0524 | Core & experience | `accounts`, `dashboard`, `system_settings`, `households`, shared design (`templates/`, `static/`) |
| Developer 2 – MVDeguzman | Money in & out | `transactions`, `wallets`, `debts` |
| Developer 3 – Nasju17 | Planning & insights | `planning`, `investments`, `reports` |

Assignments can change; update this table when they do.

## Git workflow

```text
feature/<app> ──PR──► develop ──PR (when stable)──► main
```

- `main`: stable, release-ready. Only updated from `develop`.
- `develop`: shared integration branch. All feature PRs target it.
- `feature/<app>`: one per app (`feature/accounts`, `feature/wallets`, …), always started from the latest `develop`.

Both `main` and `develop` are protected: changes need a pull request and one approval.
Full guide: [CONTRIBUTING.md](CONTRIBUTING.md).
