# stashenv

A CLI tool for securely storing and switching between named `.env` profiles per project.

---

## Installation

```bash
pip install stashenv
```

Or with pipx (recommended):

```bash
pipx install stashenv
```

---

## Usage

```bash
# Save your current .env as a named profile
stashenv save production

# List all saved profiles for the current project
stashenv list

# Switch to a different profile
stashenv load staging

# Delete a profile
stashenv delete old-profile
```

Profiles are stored securely per project directory, so switching between environments is fast and safe.

---

## How It Works

`stashenv` detects your current project by its directory path and stores named `.env` snapshots in an encrypted local vault (`~/.stashenv`). Switching profiles overwrites your active `.env` with the selected snapshot — no more manual copying or accidental commits.

---

## Commands

| Command | Description |
|---|---|
| `stashenv save <name>` | Save current `.env` as a named profile |
| `stashenv load <name>` | Load a profile into `.env` |
| `stashenv list` | List all profiles for the current project |
| `stashenv delete <name>` | Delete a saved profile |

---

## License

MIT © 2024