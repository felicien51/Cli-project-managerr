"""
test_storage_validators.py - Tests for storage persistence and validators.

Run with:  pytest tests/ -v
"""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import save_data, load_data
from utils.validators import validate_email, validate_date, validate_non_empty


# ── Storage ───────────────────────────────────────────────────────────────────

class TestStorage:
    def _make_users(self):
        u = User("Sam", "sam@test.com")
        p = Project("Proj A", due_date="2026-01-01")
        p.add_task(Task("T1", status="complete"))
        p.add_task(Task("T2"))
        u.add_project(p)
        return {u.user_id: u}

    def test_save_and_load_roundtrip(self):
        users = self._make_users()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            path = tf.name

        try:
            save_data(users, path)
            loaded = load_data(path)
            assert len(loaded) == 1
            loaded_user = next(iter(loaded.values()))
            assert loaded_user.name == "Sam"
            assert len(loaded_user.projects) == 1
            assert len(loaded_user.projects[0].tasks) == 2
        finally:
            os.unlink(path)

    def test_load_missing_file_returns_empty(self):
        result = load_data("/tmp/does_not_exist_xyz.json")
        assert result == {}

    def test_load_corrupt_file_returns_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tf:
            tf.write("NOT JSON {{{{")
            path = tf.name
        try:
            result = load_data(path)
            assert result == {}
        finally:
            os.unlink(path)

    def test_save_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "nested", "dir", "data.json")
            save_data({}, path)
            assert os.path.exists(path)


# ── Validators ────────────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_email(self):
        assert validate_email("user@example.com") == "user@example.com"

    def test_valid_email_strips_whitespace(self):
        assert validate_email("  user@example.com  ") == "user@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            validate_email("not-an-email")

    def test_invalid_email_no_at_raises(self):
        with pytest.raises(ValueError):
            validate_email("nodomain")

    def test_valid_date(self):
        assert validate_date("2026-06-01") == "2026-06-01"

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            validate_date("01/06/2026")

    def test_non_empty_valid(self):
        assert validate_non_empty("  hello  ") == "hello"

    def test_non_empty_empty_raises(self):
        with pytest.raises(ValueError):
            validate_non_empty("   ")
