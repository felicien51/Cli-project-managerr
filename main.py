"""
main.py - CLI entry point for the Project Tracker tool.

Uses argparse with subcommands to provide a clean, user-focused interface.

Commands
--------
  add-user        Add a new user
  list-users      List all users
  add-project     Add a project to a user
  list-projects   List projects for a user (or all users)
  add-task        Add a task to a project
  list-tasks      List tasks in a project
  complete-task   Mark a task as complete
  update-task     Update task status
  search          Search projects by keyword
  delete-user     Remove a user
  delete-project  Remove a project from a user
"""

import argparse
import logging
import sys

from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import load_data, save_data, DEFAULT_DATA_PATH
from utils.display import (
    print_users,
    print_projects,
    print_tasks,
    print_search_results,
    success,
    error,
    info,
)
from utils.validators import validate_email, validate_date, validate_non_empty

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("tracker.log"), logging.NullHandler()],
)
logger = logging.getLogger(__name__)

# ── Global state ──────────────────────────────────────────────────────────────

USERS = {}  # Dict[str, User] – loaded at startup


def _save():
    """Persist current state to disk."""
    save_data(USERS, DEFAULT_DATA_PATH)


def _find_user_by_name(name: str):
    """
    Locate a User by name (case-insensitive).

    Args:
        name (str): User name to search.

    Returns:
        User or None.
    """
    name_lower = name.strip().lower()
    for user in USERS.values():
        if user.name.lower() == name_lower:
            return user
    return None


# ── Sub-command handlers ──────────────────────────────────────────────────────


def cmd_add_user(args):
    """
    Handle the add-user command.

    Creates a new User and persists it.
    """
    try:
        name = validate_non_empty(args.name, "Name")
        email = validate_email(args.email)
    except ValueError as exc:
        error(str(exc))
        return

    if _find_user_by_name(name):
        error(f"A user named '{name}' already exists.")
        return

    user = User(name=name, email=email)
    USERS[user.user_id] = user
    _save()
    success(f"User '{name}' created with ID {user.user_id}.")
    logger.info("Created user %s (%s).", name, user.user_id)


def cmd_list_users(args):
    """
    Handle the list-users command.

    Displays a formatted table of all users.
    """
    print_users(USERS)


def cmd_add_project(args):
    """
    Handle the add-project command.

    Creates a Project and adds it to the specified user.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    try:
        title = validate_non_empty(args.title, "Title")
        due = validate_date(args.due_date) if args.due_date else ""
    except ValueError as exc:
        error(str(exc))
        return

    if user.get_project_by_title(title):
        error(f"User '{user.name}' already has a project titled '{title}'.")
        return

    project = Project(
        title=title,
        description=args.description or "",
        due_date=due,
    )
    user.add_project(project)
    _save()
    success(f"Project '{title}' added to {user.name} (ID {project.project_id}).")
    logger.info("Created project %s for user %s.", project.project_id, user.user_id)


def cmd_list_projects(args):
    """
    Handle the list-projects command.

    Shows projects for a named user, or all users if --all is set.
    """
    if args.all:
        for user in USERS.values():
            print_projects(user)
        return

    if not args.user:
        error("Provide --user <name> or use --all.")
        return

    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    print_projects(user)


def cmd_add_task(args):
    """
    Handle the add-task command.

    Creates a Task and adds it to the specified project.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    project = user.get_project_by_title(args.project)
    if not project:
        error(f"No project titled '{args.project}' found for {user.name}.")
        return

    try:
        title = validate_non_empty(args.title, "Task title")
    except ValueError as exc:
        error(str(exc))
        return

    task = Task(title=title, assigned_to=args.assigned_to)
    project.add_task(task)
    _save()
    success(f"Task '{title}' added to project '{project.title}' (ID {task.task_id}).")
    logger.info("Created task %s in project %s.", task.task_id, project.project_id)


def cmd_list_tasks(args):
    """
    Handle the list-tasks command.

    Displays all tasks within the specified project.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    project = user.get_project_by_title(args.project)
    if not project:
        error(f"No project titled '{args.project}' found for {user.name}.")
        return

    print_tasks(project)


def cmd_complete_task(args):
    """
    Handle the complete-task command.

    Marks a task as 'complete'.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    project = user.get_project_by_title(args.project)
    if not project:
        error(f"No project titled '{args.project}' found for {user.name}.")
        return

    task = project.get_task_by_title(args.task)
    if not task:
        error(f"No task titled '{args.task}' found in project '{project.title}'.")
        return

    task.complete()
    _save()
    success(f"Task '{task.title}' marked as complete.")
    logger.info("Task %s completed in project %s.", task.task_id, project.project_id)


def cmd_update_task(args):
    """
    Handle the update-task command.

    Updates the status of a specific task.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    project = user.get_project_by_title(args.project)
    if not project:
        error(f"No project titled '{args.project}' found for {user.name}.")
        return

    task = project.get_task_by_title(args.task)
    if not task:
        error(f"No task titled '{args.task}' found in project '{project.title}'.")
        return

    try:
        task.status = args.status
    except ValueError as exc:
        error(str(exc))
        return

    _save()
    success(f"Task '{task.title}' status updated to '{args.status}'.")
    logger.info("Task %s status -> %s.", task.task_id, args.status)


def cmd_search(args):
    """
    Handle the search command.

    Searches all projects across all users for a keyword in title or description.
    """
    keyword = args.keyword.lower()
    results = []
    for user in USERS.values():
        for project in user.projects:
            if keyword in project.title.lower() or keyword in project.description.lower():
                results.append({"user": user, "project": project})

    print_search_results(results)
    info(f"{len(results)} result(s) for '{args.keyword}'.")


def cmd_delete_user(args):
    """
    Handle the delete-user command.

    Removes a user and all their data from the system.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    del USERS[user.user_id]
    _save()
    success(f"User '{user.name}' and all their projects have been deleted.")
    logger.info("Deleted user %s.", user.user_id)


def cmd_delete_project(args):
    """
    Handle the delete-project command.

    Removes a project from a user.
    """
    user = _find_user_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'.")
        return

    project = user.get_project_by_title(args.project)
    if not project:
        error(f"No project titled '{args.project}' found for {user.name}.")
        return

    user.projects.remove(project)
    _save()
    success(f"Project '{project.title}' removed from {user.name}.")
    logger.info("Deleted project %s from user %s.", project.project_id, user.user_id)


# ── Parser construction ───────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the top-level argument parser with all subcommands.

    Returns:
        argparse.ArgumentParser: Fully configured parser.
    """
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="📋  Project Tracker CLI — manage users, projects, and tasks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py add-user --name "Alex" --email alex@dev.io
  python main.py add-project --user "Alex" --title "CLI Tool" --due-date 2026-12-31
  python main.py add-task --user "Alex" --project "CLI Tool" --title "Implement add-task"
  python main.py complete-task --user "Alex" --project "CLI Tool" --task "Implement add-task"
  python main.py search --keyword "CLI"
        """,
    )

    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # ── add-user ──────────────────────────────────────────────────────────────
    p_add_user = sub.add_parser("add-user", help="Create a new user.")
    p_add_user.add_argument("--name", required=True, help="User display name.")
    p_add_user.add_argument("--email", required=True, help="User email address.")
    p_add_user.set_defaults(func=cmd_add_user)

    # ── list-users ────────────────────────────────────────────────────────────
    p_list_users = sub.add_parser("list-users", help="List all users.")
    p_list_users.set_defaults(func=cmd_list_users)

    # ── add-project ───────────────────────────────────────────────────────────
    p_add_proj = sub.add_parser("add-project", help="Add a project to a user.")
    p_add_proj.add_argument("--user", required=True, help="Owner user name.")
    p_add_proj.add_argument("--title", required=True, help="Project title.")
    p_add_proj.add_argument("--description", default="", help="Project description.")
    p_add_proj.add_argument("--due-date", dest="due_date", default="", help="Due date (YYYY-MM-DD).")
    p_add_proj.set_defaults(func=cmd_add_project)

    # ── list-projects ─────────────────────────────────────────────────────────
    p_list_proj = sub.add_parser("list-projects", help="List projects for a user.")
    p_list_proj.add_argument("--user", default="", help="User name.")
    p_list_proj.add_argument("--all", action="store_true", help="List projects for all users.")
    p_list_proj.set_defaults(func=cmd_list_projects)

    # ── add-task ──────────────────────────────────────────────────────────────
    p_add_task = sub.add_parser("add-task", help="Add a task to a project.")
    p_add_task.add_argument("--user", required=True, help="Owner user name.")
    p_add_task.add_argument("--project", required=True, help="Project title.")
    p_add_task.add_argument("--title", required=True, help="Task title.")
    p_add_task.add_argument("--assigned-to", dest="assigned_to", default=None, help="Assignee name.")
    p_add_task.set_defaults(func=cmd_add_task)

    # ── list-tasks ────────────────────────────────────────────────────────────
    p_list_tasks = sub.add_parser("list-tasks", help="List tasks in a project.")
    p_list_tasks.add_argument("--user", required=True, help="Owner user name.")
    p_list_tasks.add_argument("--project", required=True, help="Project title.")
    p_list_tasks.set_defaults(func=cmd_list_tasks)

    # ── complete-task ─────────────────────────────────────────────────────────
    p_complete = sub.add_parser("complete-task", help="Mark a task as complete.")
    p_complete.add_argument("--user", required=True, help="Owner user name.")
    p_complete.add_argument("--project", required=True, help="Project title.")
    p_complete.add_argument("--task", required=True, help="Task title.")
    p_complete.set_defaults(func=cmd_complete_task)

    # ── update-task ───────────────────────────────────────────────────────────
    p_update = sub.add_parser("update-task", help="Update the status of a task.")
    p_update.add_argument("--user", required=True, help="Owner user name.")
    p_update.add_argument("--project", required=True, help="Project title.")
    p_update.add_argument("--task", required=True, help="Task title.")
    p_update.add_argument(
        "--status",
        required=True,
        choices=["pending", "in-progress", "complete"],
        help="New status.",
    )
    p_update.set_defaults(func=cmd_update_task)

    # ── search ────────────────────────────────────────────────────────────────
    p_search = sub.add_parser("search", help="Search projects by keyword.")
    p_search.add_argument("--keyword", required=True, help="Search term.")
    p_search.set_defaults(func=cmd_search)

    # ── delete-user ───────────────────────────────────────────────────────────
    p_del_user = sub.add_parser("delete-user", help="Delete a user and all their data.")
    p_del_user.add_argument("--user", required=True, help="User name to delete.")
    p_del_user.set_defaults(func=cmd_delete_user)

    # ── delete-project ────────────────────────────────────────────────────────
    p_del_proj = sub.add_parser("delete-project", help="Delete a project from a user.")
    p_del_proj.add_argument("--user", required=True, help="Owner user name.")
    p_del_proj.add_argument("--project", required=True, help="Project title to delete.")
    p_del_proj.set_defaults(func=cmd_delete_project)

    return parser


# ── Entry point ───────────────────────────────────────────────────────────────


def main():
    """Load data, parse arguments, and dispatch to the appropriate handler."""
    global USERS
    USERS = load_data()

    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
