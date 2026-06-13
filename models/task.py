"""
task.py - Task model for the project tracker.

A Task belongs to exactly one Project and can be assigned to a User.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


VALID_STATUSES = {"pending", "in-progress", "complete"}


class Task:
    """
    Represents a unit of work within a Project.

    Attributes:
        task_id (str): Unique identifier (UUID).
        title (str): Short description of the task.
        status (str): One of 'pending', 'in-progress', 'complete'.
        assigned_to (Optional[str]): Name of the user assigned to this task.
    """

    # Class-level counter for human-readable IDs (used in display only)
    _counter: int = 0

    def __init__(
        self,
        title: str,
        status: str = "pending",
        assigned_to: Optional[str] = None,
        task_id: Optional[str] = None,
    ):
        """
        Initialise a Task.

        Args:
            title (str): Task title.
            status (str): Initial status (default 'pending').
            assigned_to (Optional[str]): Assignee name.
            task_id (Optional[str]): Existing ID for loading from file.
        """
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {VALID_STATUSES}.")

        self.task_id: str = task_id or str(uuid.uuid4())[:8]
        self.title: str = title.strip()
        self._status: str = status
        self.assigned_to: Optional[str] = assigned_to

        Task._counter += 1

    @property
    def status(self) -> str:
        """Return task status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Set task status after validation."""
        if value not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {VALID_STATUSES}.")
        self._status = value

    def complete(self):
        """Mark this task as complete."""
        self._status = "complete"

    def to_dict(self) -> dict:
        """Serialise task to a dictionary for JSON persistence."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self._status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Deserialise a Task from a dictionary.

        Args:
            data (dict): Dictionary with task fields.

        Returns:
            Task: Reconstructed Task instance.
        """
        return cls(
            title=data["title"],
            status=data.get("status", "pending"),
            assigned_to=data.get("assigned_to"),
            task_id=data.get("task_id"),
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id!r}, title={self.title!r}, "
            f"status={self._status!r}, assigned_to={self.assigned_to!r})"
        )
