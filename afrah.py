#!/usr/bin/env python3
"""Afrah — a simple CLI task manager."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

TASKS_FILE = Path(__file__).parent / "tasks.json"
PRIORITIES = ("low", "medium", "high")
PRIORITY_SYMBOL = {"low": "○", "medium": "◑", "high": "●"}
STATUS_SYMBOL = {"pending": "[ ]", "done": "[✓]"}


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []
    with TASKS_FILE.open() as f:
        return json.load(f)


def save_tasks(tasks: list[dict]) -> None:
    with TASKS_FILE.open("w") as f:
        json.dump(tasks, f, indent=2)


def next_id(tasks: list[dict]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "title": args.title,
        "priority": args.priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {task['title']} [{task['priority']}]")


def cmd_list(args: argparse.Namespace) -> None:
    tasks = load_tasks()

    if args.filter != "all":
        tasks = [t for t in tasks if t["status"] == args.filter]
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]

    if not tasks:
        print("No tasks found.")
        return

    # Sort: pending before done, then by priority (high → low), then by id
    priority_order = {p: i for i, p in enumerate(reversed(PRIORITIES))}
    tasks.sort(key=lambda t: (t["status"] == "done", priority_order[t["priority"]], t["id"]))

    col_id = max(len(str(t["id"])) for t in tasks)
    print()
    for t in tasks:
        status = STATUS_SYMBOL[t["status"]]
        pri = PRIORITY_SYMBOL[t["priority"]]
        id_str = str(t["id"]).rjust(col_id)
        print(f"  {status} #{id_str}  {pri} {t['title']}")
    print()


def cmd_done(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == args.id:
            if task["status"] == "done":
                print(f"Task #{args.id} is already done.")
                return
            task["status"] = "done"
            task["completed_at"] = datetime.now().isoformat(timespec="seconds")
            save_tasks(tasks)
            print(f"Completed task #{args.id}: {task['title']}")
            return
    print(f"Task #{args.id} not found.", file=sys.stderr)
    sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    remaining = [t for t in tasks if t["id"] != args.id]
    if len(remaining) == len(tasks):
        print(f"Task #{args.id} not found.", file=sys.stderr)
        sys.exit(1)
    deleted = next(t for t in tasks if t["id"] == args.id)
    save_tasks(remaining)
    print(f"Deleted task #{args.id}: {deleted['title']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="afrah",
        description="Afrah — simple CLI task manager",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task description")
    p_add.add_argument(
        "--priority", choices=PRIORITIES, default="medium",
        help="Priority level (default: medium)",
    )
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--filter", choices=("all", "pending", "done"), default="all",
        help="Filter by status (default: all)",
    )
    p_list.add_argument(
        "--priority", choices=PRIORITIES, default=None,
        help="Filter by priority",
    )
    p_list.set_defaults(func=cmd_list)

    # done
    p_done = sub.add_parser("done", help="Mark a task as complete")
    p_done.add_argument("id", type=int, help="Task ID")
    p_done.set_defaults(func=cmd_done)

    # delete
    p_del = sub.add_parser("delete", help="Delete a task")
    p_del.add_argument("id", type=int, help="Task ID")
    p_del.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
