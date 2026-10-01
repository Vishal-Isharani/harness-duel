from pathlib import Path

import pytest

from duel import config
from duel.config import load_suite

EX = Path(__file__).resolve().parent.parent / "examples"


def test_only_keeps_selected_tasks_in_suite_order():
    suite = load_suite(EX, only=["transfer", "to-csv"])
    assert [t.id for t in suite.tasks] == ["to-csv", "transfer"]


def test_unknown_task_id_names_it_and_lists_available():
    with pytest.raises(config.InputError) as err:
        load_suite(EX, only=["to-csv", "nope"])
    msg = str(err.value)
    assert "nope" in msg
    assert "fix-zero-add" in msg and "transfer" in msg


def test_suite_without_tasks_is_an_input_error(tmp_path):
    (tmp_path / "tasks").mkdir()
    with pytest.raises(config.InputError):
        load_suite(tmp_path)
