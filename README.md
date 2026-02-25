# Afrah

A simple, fast CLI task manager. Keep track of what matters — from your terminal.

## Features

- Add, complete, and delete tasks
- Priority levels: `low`, `medium`, `high`
- Persistent storage (JSON)
- Filter tasks by status or priority
- Clean, readable output

## Quick Start

```bash
python afrah.py add "Buy groceries" --priority high
python afrah.py list
python afrah.py done 1
python afrah.py list --filter pending
python afrah.py delete 1
```

## Commands

| Command | Description |
|---------|-------------|
| `add <task>` | Add a new task |
| `list` | List all tasks |
| `done <id>` | Mark a task as complete |
| `delete <id>` | Delete a task |

### Options for `add`

| Option | Values | Default |
|--------|--------|---------|
| `--priority` | `low`, `medium`, `high` | `medium` |

### Options for `list`

| Option | Values | Description |
|--------|--------|-------------|
| `--filter` | `pending`, `done`, `all` | Filter by status (default: `all`) |
| `--priority` | `low`, `medium`, `high` | Filter by priority |

## Installation

No dependencies beyond the Python standard library.

```bash
git clone <repo>
cd Afrah
python afrah.py list
```

Tasks are stored in `tasks.json` in the same directory.
