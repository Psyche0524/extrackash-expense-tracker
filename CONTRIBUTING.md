# Contributing to Extrackash

Three of us work on this repo at the same time. These rules keep `main` and `develop` working.

## 1. Start from the latest `develop`

```bash
git switch develop
git pull
```

## 2. Switch to your feature branch

Each app has its own branch: `feature/accounts`, `feature/dashboard`, `feature/transactions`, `feature/wallets`,
`feature/planning`, `feature/debts`, `feature/investments`, `feature/reports`, `feature/households`,
`feature/system-settings`.

```bash
git switch feature/wallets
git merge develop          # bring in everyone else's merged work first
```

For a quick bug fix outside your area, make a short-lived branch instead: `git switch -c fix/<what> develop`.

## 3. Work, then test

- Keep changes inside your app folder (`apps/<app>/`) where you can.
- Shared files (`templates/base.html`, `static/css/style.css`, `static/js/app.js`, `config/`, `apps/core/`)
  affect everyone: tell the team before changing them, and keep those changes small.
- Changed a model? Run `python manage.py makemigrations` and commit the new migration file.
- Run `python manage.py test` and check your screens at phone size before pushing.

## 4. Commit with a prefix

| Prefix | Use for |
|---|---|
| `feat:` | New functionality |
| `fix:` | Bug fixes |
| `refactor:` | Code restructuring, same behaviour |
| `style:` | Visual/CSS changes |
| `docs:` | Documentation |
| `test:` | Tests |
| `chore:` | Maintenance (dependencies, config) |

Example: `feat: add monthly budget rollover`

## 5. Push and open a pull request into `develop`

```bash
git push -u origin feature/wallets
```

On GitHub, open a pull request **into `develop`** and fill in the template.

## 6. Review

- One teammate reviews: reads the change, pulls the branch, runs it, checks it on a phone.
- The automatic test check must be green.
- Ask questions in the PR; push fixes to the same branch.

## 7. Merge

- After approval, merge into `develop`.
- Feature branches stay (one per app) for the next task: merge `develop` into them before starting again.

## 8. Releases (`develop` → `main`)

When `develop` is stable (before a presentation, checkpoint or submission):

1. Test `develop` together on real phones.
2. Open a pull request from `develop` into `main` titled `Release vX.Y`.
3. After approval and merge, create a GitHub Release with the tag `vX.Y`.

## Never commit

`db.sqlite3`, `.venv/`, `.env`, `media/` (uploaded photos), `Figma Design/`, passwords or secret keys.
They are already in `.gitignore`. If one shows up in `git status`, don't add it.
