"""
display.py - Rich-powered display helpers for CLI output.

Uses the `rich` package for formatted tables, panels, and styled text.
"""

from typing import Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

from models.user import User
from models.project import Project
from models.task import Task

console = Console()

# ── Status colour map ───────────────────────────────────────────────────────

STATUS_STYLES: Dict[str, str] = {
    "pending": "yellow",
    "in-progress": "cyan",
    "complete": "green",
}


def _status_text(status: str) -> Text:
    """Return a rich Text object coloured by status."""
    colour = STATUS_STYLES.get(status, "white")
    return Text(status, style=colour)


# ── User display ─────────────────────────────────────────────────────────────


def print_users(users: Dict[str, User]) -> None:
    """
    Print all users in a formatted table.

    Args:
        users (Dict[str, User]): User mapping from storage.
    """
    if not users:
        console.print("[bold red]No users found.[/bold red]")
        return

    table = Table(title="👥  Registered Users", box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Name", style="bold")
    table.add_column("Email", style="cyan")
    table.add_column("Projects", justify="right")

    for user in users.values():
        table.add_row(
            user.user_id,
            user.name,
            user.email,
            str(len(user.projects)),
        )

    console.print(table)


# ── Project display ───────────────────────────────────────────────────────────


def print_projects(user: User) -> None:
    """
    Print all projects belonging to a user.

    Args:
        user (User): The user whose projects to display.
    """
    if not user.projects:
        console.print(
            f"[bold yellow]{user.name}[/bold yellow] has no projects yet."
        )
        return

    table = Table(
        title=f"📁  Projects for {user.name}",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("ID", style="dim", width=10)
    table.add_column("Title", style="bold")
    table.add_column("Description")
    table.add_column("Due Date", style="magenta")
    table.add_column("Tasks", justify="right")
    table.add_column("Done", justify="right")

    for project in user.projects:
        done = len(project.completed_tasks())
        table.add_row(
            project.project_id,
            project.title,
            project.description or "—",
            project.due_date or "—",
            str(len(project.tasks)),
            f"[green]{done}[/green]",
        )

    console.print(table)


# ── Task display ──────────────────────────────────────────────────────────────


def print_tasks(project: Project) -> None:
    """
    Print all tasks within a project.

    Args:
        project (Project): The project whose tasks to display.
    """
    if not project.tasks:
        console.print(
            f"[bold yellow]{project.title}[/bold yellow] has no tasks yet."
        )
        return

    table = Table(
        title=f"✅  Tasks in '{project.title}'",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("ID", style="dim", width=10)
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Assigned To")

    for task in project.tasks:
        table.add_row(
            task.task_id,
            task.title,
            _status_text(task.status),
            task.assigned_to or "—",
        )

    console.print(table)


# ── Search results ────────────────────────────────────────────────────────────


def print_search_results(results: List[dict]) -> None:
    """
    Display project search results across all users.

    Args:
        results (List[dict]): Each dict has keys 'user', 'project'.
    """
    if not results:
        console.print("[bold red]No matching projects found.[/bold red]")
        return

    table = Table(title="🔍  Search Results", box=box.ROUNDED, show_lines=True)
    table.add_column("User", style="bold")
    table.add_column("Project ID", style="dim", width=10)
    table.add_column("Title")
    table.add_column("Due Date", style="magenta")
    table.add_column("Tasks", justify="right")

    for r in results:
        table.add_row(
            r["user"].name,
            r["project"].project_id,
            r["project"].title,
            r["project"].due_date or "—",
            str(len(r["project"].tasks)),
        )

    console.print(table)


# ── Generic helpers ───────────────────────────────────────────────────────────


def success(message: str) -> None:
    """Print a green success message."""
    console.print(f"[bold green]✔  {message}[/bold green]")


def error(message: str) -> None:
    """Print a red error message."""
    console.print(f"[bold red]✘  {message}[/bold red]")


def info(message: str) -> None:
    """Print a cyan informational message."""
    console.print(f"[cyan]ℹ  {message}[/cyan]")
