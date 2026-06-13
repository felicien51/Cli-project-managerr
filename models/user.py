"""
user.py - User model, inheriting from Person.

Demonstrates inheritance (Person -> User) and one-to-many relationship
between User and Project.
"""

from __future__ import annotations
from typing import List, Optional
import uuid

from models.person import Person
from models.project import Project


class User(Person):
    """
    A registered user of the project tracker.

    Inherits name and email from Person.
    Owns zero or more Projects.

    Attributes:
        user_id (str): Unique identifier.
        projects (List[Project]): Projects belonging to this user.
    """

    def __init__(
        self,
        name: str,
        email: str,
        user_id: Optional[str] = None,
    ):
        """
        Initialise a User.

        Args:
            name (str): User's display name.
            email (str): User's email address.
            user_id (Optional[str]): Existing ID when loading from file.
        """
        super().__init__(name, email)
        self.user_id: str = user_id or str(uuid.uuid4())[:8]
        self.projects: List[Project] = []

    def add_project(self, project: Project) -> None:
        """
        Attach a project to this user.

        Args:
            project (Project): Project instance to add.
        """
        self.projects.append(project)

    def get_project_by_title(self, title: str) -> Optional[Project]:
        """
        Find a project by its title (case-insensitive).

        Args:
            title (str): Project title to search.

        Returns:
            Optional[Project]: Matching project or None.
        """
        title_lower = title.lower()
        for project in self.projects:
            if project.title.lower() == title_lower:
                return project
        return None

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Find a project by its ID.

        Args:
            project_id (str): Project ID.

        Returns:
            Optional[Project]: Matching project or None.
        """
        for project in self.projects:
            if project.project_id == project_id:
                return project
        return None

    def to_dict(self) -> dict:
        """Serialise user (and all nested data) to a dictionary."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "projects": [p.to_dict() for p in self.projects],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """
        Deserialise a User from a dictionary.

        Args:
            data (dict): Dictionary with user fields.

        Returns:
            User: Reconstructed User instance.
        """
        user = cls(
            name=data["name"],
            email=data["email"],
            user_id=data.get("user_id"),
        )
        for project_data in data.get("projects", []):
            user.add_project(Project.from_dict(project_data))
        return user

    def __repr__(self) -> str:
        return (
            f"User(id={self.user_id!r}, name={self.name!r}, "
            f"email={self.email!r}, projects={len(self.projects)})"
        )
