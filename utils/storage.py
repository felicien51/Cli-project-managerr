"""
storage.py - Persistence layer for the project tracker.

Handles loading and saving the full user/project/task graph to a JSON file.
"""

import json
import logging
import os
from typing import Dict, List

from models.user import User

logger = logging.getLogger(__name__)

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "tracker_data.json"
)


def ensure_data_dir(path: str) -> None:
    """
    Create the directory for the data file if it does not exist.

    Args:
        path (str): Full path to the data file.
    """
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)


def save_data(users: Dict[str, User], path: str = DEFAULT_DATA_PATH) -> None:
    """
    Serialise all users (with nested projects and tasks) to a JSON file.

    Args:
        users (Dict[str, User]): Mapping of user_id -> User.
        path (str): File path to write to.

    Raises:
        IOError: If the file cannot be written.
    """
    ensure_data_dir(path)
    payload = [user.to_dict() for user in users.values()]
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        logger.debug("Data saved to %s (%d users).", path, len(payload))
    except OSError as exc:
        logger.error("Failed to save data: %s", exc)
        raise


def load_data(path: str = DEFAULT_DATA_PATH) -> Dict[str, User]:
    """
    Deserialise users (with nested projects and tasks) from a JSON file.

    Returns an empty dict if the file does not exist or is malformed.

    Args:
        path (str): File path to read from.

    Returns:
        Dict[str, User]: Mapping of user_id -> User.
    """
    if not os.path.exists(path):
        logger.debug("Data file not found at %s — starting fresh.", path)
        return {}

    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        users: Dict[str, User] = {}
        for user_data in payload:
            user = User.from_dict(user_data)
            users[user.user_id] = user
        logger.debug("Loaded %d users from %s.", len(users), path)
        return users
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.error("Corrupt data file — could not load: %s", exc)
        return {}
