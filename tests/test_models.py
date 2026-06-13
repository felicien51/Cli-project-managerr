"""
test_models.py - Unit tests for User, Project, and Task models.

Run with:  pytest tests/ -v
"""

import pytest
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.task import Task
from models.project import Project
from models.user import User
from models.person import Person


# ── Person ────────────────────────────────────────────────────────────────────

class TestPerson:
    def test_create_person(self):
        p = Person("Alice", "alice@example.com")
        assert p.name == "Alice"
        assert p.email == "alice@example.com"

    def test_name_setter(self):
        p = Person("Alice", "alice@example.com")
        p.name = "  Bob  "
        assert p.name == "Bob"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            p = Person("Alice", "alice@example.com")
            p.name = "   "

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            Person("Alice", "not-an-email")


# ── Task ──────────────────────────────────────────────────────────────────────

class TestTask:
    def test_create_task(self):
        t = Task("Fix bug")
        assert t.title == "Fix bug"
        assert t.status == "pending"
        assert t.assigned_to is None

    def test_task_with_assignee(self):
        t = Task("Write docs", assigned_to="Dev")
        assert t.assigned_to == "Dev"

    def test_complete_task(self):
        t = Task("Deploy")
        t.complete()
        assert t.status == "complete"

    def test_set_valid_status(self):
        t = Task("Review PR")
        t.status = "in-progress"
        assert t.status == "in-progress"

    def test_invalid_status_raises(self):
        t = Task("Test")
        with pytest.raises(ValueError):
            t.status = "unknown"

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Task("  ")

    def test_serialise_roundtrip(self):
        t = Task("Build API", status="in-progress", assigned_to="Alex")
        d = t.to_dict()
        t2 = Task.from_dict(d)
        assert t2.title == t.title
        assert t2.status == t.status
        assert t2.assigned_to == t.assigned_to
        assert t2.task_id == t.task_id


# ── Project ───────────────────────────────────────────────────────────────────

class TestProject:
    def test_create_project(self):
        p = Project("Alpha")
        assert p.title == "Alpha"
        assert p.tasks == []

    def test_add_task(self):
        p = Project("Alpha")
        t = Task("Task 1")
        p.add_task(t)
        assert len(p.tasks) == 1

    def test_get_task_by_title(self):
        p = Project("Alpha")
        t = Task("Task A")
        p.add_task(t)
        found = p.get_task_by_title("task a")  # case-insensitive
        assert found is t

    def test_get_task_by_id(self):
        p = Project("Alpha")
        t = Task("Task A")
        p.add_task(t)
        assert p.get_task_by_id(t.task_id) is t

    def test_pending_and_completed_tasks(self):
        p = Project("Alpha")
        t1 = Task("T1")
        t2 = Task("T2")
        t2.complete()
        p.add_task(t1)
        p.add_task(t2)
        assert len(p.pending_tasks()) == 1
        assert len(p.completed_tasks()) == 1

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Project("")

    def test_serialise_roundtrip(self):
        p = Project("Beta", description="A project", due_date="2026-06-01")
        p.add_task(Task("T1"))
        d = p.to_dict()
        p2 = Project.from_dict(d)
        assert p2.title == "Beta"
        assert p2.description == "A project"
        assert len(p2.tasks) == 1


# ── User ──────────────────────────────────────────────────────────────────────

class TestUser:
    def test_create_user(self):
        u = User("Zach", "zach@dev.io")
        assert u.name == "Zach"
        assert u.projects == []

    def test_add_project(self):
        u = User("Zach", "zach@dev.io")
        p = Project("My Project")
        u.add_project(p)
        assert len(u.projects) == 1

    def test_get_project_by_title(self):
        u = User("Zach", "zach@dev.io")
        p = Project("My Project")
        u.add_project(p)
        assert u.get_project_by_title("my project") is p

    def test_get_project_by_id(self):
        u = User("Zach", "zach@dev.io")
        p = Project("My Project")
        u.add_project(p)
        assert u.get_project_by_id(p.project_id) is p

    def test_serialise_roundtrip(self):
        u = User("Zach", "zach@dev.io")
        p = Project("P1")
        p.add_task(Task("T1"))
        u.add_project(p)
        d = u.to_dict()
        u2 = User.from_dict(d)
        assert u2.name == "Zach"
        assert len(u2.projects) == 1
        assert len(u2.projects[0].tasks) == 1

    def test_inheritance(self):
        """User should be a subclass of Person."""
        u = User("Dev", "dev@io.com")
        assert isinstance(u, Person)
