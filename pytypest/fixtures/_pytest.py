from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

import pytest

from .._fixture_factory import fixture
from .._hub import hub


@fixture
def get_request() -> pytest.FixtureRequest:
    if hub.request is None:
        raise RuntimeError('pytest plugin is not active')
    return hub.request


@fixture
def get_pytest_fixture(name: str) -> Any:
    request = get_request()
    return request.getfixturevalue(name)


@fixture
def capture_std(*, binary: bool = False, fd: bool = False) -> pytest.CaptureFixture:
    """Capture stdout and stderr.
    """
    root = 'fd' if fd else 'sys'
    suffix = 'binary' if binary else ''
    return get_pytest_fixture(f'cap{root}{suffix}')


@fixture
def capture_logs() -> pytest.LogCaptureFixture:
    return get_pytest_fixture('caplog')


@fixture
def record_warnings() -> pytest.WarningsRecorder:
    return get_pytest_fixture('recwarn')


@fixture
def make_temp_dir(basename: str | None = None, numbered: bool = True) -> Path:
    factory: pytest.TempPathFactory = get_pytest_fixture('tmp_path_factory')
    if basename is not None:
        return factory.mktemp(basename=basename, numbered=numbered)
    return factory.getbasetemp()


@fixture
def monkeypatch() -> Iterator[pytest.MonkeyPatch]:
    patcher = pytest.MonkeyPatch()
    yield patcher
    patcher.undo()


@fixture
def setattr(
    target: object | str,
    name: str,
    value: object,
    *,
    must_exist: bool = True,
) -> Iterator[None]:
    patcher = pytest.MonkeyPatch()
    if isinstance(target, str):
        patcher.setattr(f'{target}.{name}', value, raising=must_exist)
    else:
        patcher.setattr(target, name, value, raising=must_exist)
    yield
    patcher.undo()


@fixture
def delattr(
    target: object | str,
    name: str,
    *,
    must_exist: bool = True,
) -> Iterator[None]:
    """Delete attribute of an object.
    """
    patcher = pytest.MonkeyPatch()
    if isinstance(target, str):
        patcher.delattr(f'{target}.{name}', raising=must_exist)
    else:
        patcher.delattr(target, name, raising=must_exist)
    yield
    patcher.undo()
