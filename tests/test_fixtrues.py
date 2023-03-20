from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import pytest
import requests

from pytypest import fixtures


class Global:
    attr: int = 42


def test_get_request(isolated, scoped) -> None:
    with scoped('function'):
        req = fixtures.get_request()
        assert req.function is test_get_request
        assert req.scope == 'function'


def test_get_request__not_active() -> None:
    msg = 'pytest plugin is not active'
    with pytest.raises(RuntimeError, match=msg):
        fixtures.get_request()


def test_make_temp_dir(isolated, scoped) -> None:
    with scoped('function'):
        path = fixtures.make_temp_dir()
        assert path.is_dir()


def test_make_temp_dir__basename(isolated, scoped) -> None:
    with scoped('function'):
        path = fixtures.make_temp_dir('hello', numbered=False)
        assert path.is_dir()
        assert path.name == 'hello'


def test_chdir(isolated, scoped) -> None:
    dir1 = Path(os.getcwd())
    with scoped('function'):
        fixtures.chdir(dir1.parent)
        dir2 = Path(os.getcwd())
        assert dir2 == dir1.parent


def test_get_pytest_fixture(isolated, scoped, tmp_path) -> None:
    with scoped('function'):
        path = fixtures.get_pytest_fixture('tmp_path')
        assert path is tmp_path


def test_update_doctest_namespace(isolated, scoped, tmp_path) -> None:
    with scoped('function'):
        ns = fixtures.update_doctest_namespace({'a': 'b'}, c='d')
        assert ns['a'] == 'b'
        assert ns['c'] == 'd'


@pytest.mark.parametrize('given, expected', [
    (fixtures.capture_std, 'capsys'),
    (lambda: fixtures.capture_std(binary=True), 'capsysbinary'),
    (lambda: fixtures.capture_std(fd=True), 'capfd'),
    (lambda: fixtures.capture_std(binary=True, fd=True), 'capfdbinary'),
    (fixtures.capture_logs, 'caplog'),
    (fixtures.update_doctest_namespace, 'doctest_namespace'),
    (fixtures.record_warnings, 'recwarn'),
])
def test_proxying(isolated, scoped, given, expected, request) -> None:
    with scoped('function'):
        fixt1 = request.getfixturevalue(expected)
        fixt2 = fixtures.get_pytest_fixture(expected)
        fixt3 = given()
        assert fixt1 is fixt2
        assert fixt2 is fixt3


def test_defer(isolated, scoped) -> None:
    log = []
    with scoped('function'):
        fixtures.defer(lambda: log.append(1))
        assert log == []
    assert log == [1]


def test_defer__no_scope(isolated, scoped) -> None:
    msg = 'cannot find ScopeManager for `function` scope'
    with pytest.raises(LookupError, match=msg):
        fixtures.defer(lambda: None)
    with scoped('class'):
        with pytest.raises(LookupError, match=msg):
            fixtures.defer(lambda: None)


def test_enter_context(isolated, scoped) -> None:
    log = []

    @contextmanager
    def man():
        log.append('enter')
        yield 17
        log.append('exit')

    with scoped('function'):
        res = fixtures.enter_context(man())
        assert log == ['enter']
        assert res == 17
    assert log == ['enter', 'exit']


def test_forbid_networking__bad_host(isolated, scoped) -> None:
    with scoped('function'):
        fixtures.forbid_networking()
        msg = 'connection to the host is not allowed'
        with pytest.raises(BaseException, match=msg):
            requests.get('https://example.com/')


def test_forbid_networking__bad_port(isolated, scoped) -> None:
    with scoped('function'):
        fixtures.forbid_networking(allowed_hosts=['example.com'])
        msg = 'connection to the port is not allowed'
        with pytest.raises(BaseException, match=msg):
            requests.get('https://example.com/')


def test_forbid_networking__allowed_host_port(isolated, scoped) -> None:
    with scoped('function'):
        fixtures.forbid_networking(
            allowed_hosts=['example.com'],
            allowed_ports=[443],
        )
        requests.get('https://example.com/')


def test_monkeypatch(isolated, scoped):
    class A:
        a = 13

    with scoped('function'):
        p = fixtures.monkeypatch()
        p.setattr(A, 'a', 54)
        assert A.a == 54


def test_setattr(isolated, scoped):
    class A:
        a = 13

    with scoped('function'):
        fixtures.setattr(A, 'a', 54)
        assert A.a == 54
    assert A.a == 13


def test_setattr__str_target(isolated, scoped):
    target = f'{Global.__module__}.{Global.__name__}'
    with scoped('function'):
        fixtures.setattr(target, 'attr', 99)
        assert Global.attr == 99
    assert Global.attr == 42


def test_delattr(isolated, scoped):
    class A:
        a = 13

    with scoped('function'):
        fixtures.delattr(A, 'a')
        assert not hasattr(A, 'a')
    assert A.a == 13


def test_delattr__str_target(isolated, scoped):
    target = f'{Global.__module__}.{Global.__name__}'
    with scoped('function'):
        fixtures.delattr(target, 'attr')
        assert not hasattr(Global, 'attr')
    assert Global.attr == 42


def test_preserve_mapping(isolated, scoped):
    d = {1: 2, 3: 4, 5: 6}
    with scoped('function'):
        fixtures.preserve_mapping(d)
        d[1] = 7
        del d[5]
        assert d == {1: 7, 3: 4}
    assert d == {1: 2, 3: 4, 5: 6}
