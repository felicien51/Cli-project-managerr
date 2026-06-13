"""
project.py - Project model for the project tracker.

A Project belongs to one User and owns one-to-many Tasks.
"""

from __future__ import annotations
from typing import List, Optional
import uuid

from models.task import Task


class Project:
    """
    Represents a development project containing multiple tasks.

    Attributes:
        project_id (str): Unique identifier.
        title (str): Project title.
        description (str): Optional project description.
        due_date (str): Optional due date string (YYYY-MM-DD).
        tasks (List[Task]): List of tasks belonging to this project.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        due_date: str = "",
        project_id: Optional[str] = None,
    ):
        """
        Initialise a Project.

        Args:
            title (str): Project title.
            description (str): Brief description.
            due_date (str): Due date in YYYY-MM-DD format.
            project_id (Optional[str]): Existing ID when loading from file.
        """
        if not title.strip():
            raise ValueError("Project title cannot be empty.")

        self.project_id: str = project_id or str(uuid.uuid4())[:8]
        self.title: str = title.strip()
        self.description: str = description.strip()
        self.due_date: str = due_date.strip()
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """
        Add a Task to this project.

        Args:
            task (Task): Task instance to add.
        """
        self.tasks.append(task)

    def get_task_by_title(self, title: str) -> Optional[Task]:
        """
        Find a task by its title (case-insensitive).

        Args:
            title (str): Task title to search.

        Returns:
            Optional[Task]: Matching task or None.
        """
        title_lower = title.lower()
        for task in self.tasks:
            if task.title.lower() == title_lower:
                return task
        return None

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Find a task by its ID.

        Args:
            task_id (str): Task ID.

        Returns:
            Optional[Task]: Matching task or None.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def pending_tasks(self) -> List[Task]:
        """Return all tasks that are not yet complete."""
        return [t for t in self.tasks if t.status != "complete"]

    def completed_tasks(self) -> List[Task]:
        """Return all completed tasks."""
        return [t for t in self.tasks if t.status == "complete"]

    def to_dict(self) -> dict:
        """Serialise project (and its tasks) to a dictionary."""
        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """
        Deserialise a Project from a dictionary.

        Args:
            data (dict): Dictionary with project fields.

        Returns:
            Project: Reconstructed Project instance.
        """
        project = cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date", ""),
            project_id=data.get("project_id"),
        )
        for task_data in data.get("tasks", []):
            project.add_task(Task.from_dict(task_data))
        return project

    def __repr__(self) -> str:
        return (
            f"Project(id={self.project_id!r}, title={self.title!r}, "
            f"tasks={len(self.tasks)})"
        )
