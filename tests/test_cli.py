"""
test_cli.py - Integration tests for CLI command handlers.

Patches storage so no real files are written during tests.
Run with:  pytest tests/ -v
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import main as cli_main
from models.user import User
from models.project import Project
from models.task import Task


@pytest.fixture(autouse=True)
def reset_state():
    """Reset global USERS dict before each test and suppress saves."""
    cli_main.USERS = {}
    with patch("main._save"):
        yield


def _args(**kwargs):
    """Create a simple namespace object to pass as args."""
    ns = MagicMock()
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


# ── add-user ──────────────────────────────────────────────────────────────────

class TestAddUser:
    def test_add_user_success(self, capsys):
        cli_main.cmd_add_user(_args(name="Alice", email="alice@io.com"))
        assert len(cli_main.USERS) == 1

    def test_add_user_invalid_email(self, capsys):
        cli_main.cmd_add_user(_args(name="Alice", email="bad"))
        assert len(cli_main.USERS) == 0

    def test_add_duplicate_user(self):
        cli_main.cmd_add_user(_args(name="Alice", email="alice@io.com"))
        cli_main.cmd_add_user(_args(name="Alice", email="alice2@io.com"))
        assert len(cli_main.USERS) == 1


# ── add-project ───────────────────────────────────────────────────────────────

class TestAddProject:
    def _setup_user(self, name="Alice", email="alice@io.com"):
        cli_main.cmd_add_user(_args(name=name, email=email))
        return cli_main._find_user_by_name(name)

    def test_add_project_success(self):
        self._setup_user()
        cli_main.cmd_add_project(
            _args(user="Alice", title="Proj A", description="desc", due_date="2026-06-01")
        )
        user = cli_main._find_user_by_name("Alice")
        assert len(user.projects) == 1

    def test_add_project_no_user(self, capsys):
        cli_main.cmd_add_project(
            _args(user="Ghost", title="Proj A", description="", due_date="")
        )
        assert len(cli_main.USERS) == 0

    def test_add_project_invalid_date(self):
        self._setup_user()
        cli_main.cmd_add_project(
            _args(user="Alice", title="Proj A", description="", due_date="31/12/2026")
        )
        user = cli_main._find_user_by_name("Alice")
        assert len(user.projects) == 0


# ── add-task ──────────────────────────────────────────────────────────────────

class TestAddTask:
    def _setup(self):
        cli_main.cmd_add_user(_args(name="Alice", email="alice@io.com"))
        cli_main.cmd_add_project(
            _args(user="Alice", title="P1", description="", due_date="")
        )

    def test_add_task_success(self):
        self._setup()
        cli_main.cmd_add_task(
            _args(user="Alice", project="P1", title="T1", assigned_to=None)
        )
        user = cli_main._find_user_by_name("Alice")
        assert len(user.projects[0].tasks) == 1

    def test_add_task_no_project(self):
        cli_main.cmd_add_user(_args(name="Alice", email="alice@io.com"))
        cli_main.cmd_add_task(
            _args(user="Alice", project="Nonexistent", title="T1", assigned_to=None)
        )
        user = cli_main._find_user_by_name("Alice")
        assert user.projects == []


# ── complete-task ─────────────────────────────────────────────────────────────

class TestCompleteTask:
    def _setup(self):
        cli_main.cmd_add_user(_args(name="Alice", email="alice@io.com"))
        cli_main.cmd_add_project(
            _args(user="Alice", title="P1", description="", due_date="")
        )
        cli_main.cmd_add_task(
            _args(user="Alice", project="P1", title="T1", assigned_to=None)
        )

    def test_complete_task(self):
        self._setup()
        cli_main.cmd_complete_task(_args(user="Alice", project="P1", task="T1"))
        user = cli_main._find_user_by_name("Alice")
        assert user.projects[0].tasks[0].status == "complete"

    def test_complete_nonexistent_task(self, capsys):
        self._setup()
        cli_main.cmd_complete_task(_args(user="Alice", project="P1", task="Ghost"))
        user = cli_main._find_user_by_name("Alice")
        assert user.projects[0].tasks[0].status == "pending"


# ── search ────────────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_finds_project(self, capsys):
        cli_main.cmd_add_user(_args(name="Alice", email="alice@io.com"))
        cli_main.cmd_add_project(
            _args(user="Alice", title="API Gateway", description="REST API", due_date="")
        )
        cli_main.cmd_search(_args(keyword="API"))
        captured = capsys.readouterr()
        assert "API" in captured.out

    def test_search_no_results(self, capsys):
        cli_main.cmd_search(_args(keyword="zzznomatch"))
        captured = capsys.readouterr()
        assert "No matching" in captured.out or "0 result" in captured.out
