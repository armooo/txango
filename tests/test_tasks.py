import datetime

from mock import Mock, sentinel
import pytest

import txango.tasks


def pytest_funcarg__reactor(request):
    reactor = Mock(name='reactor')
    def call_it(f, *args, **kwargs):
        f(*args, **kwargs)
    reactor.callFromThread.side_effect = call_it
    return reactor


def test_nonblocking_task(monkeypatch, reactor):
    monkeypatch.setattr(txango.tasks, 'reactor', reactor)
    threads = Mock(name='threads')
    monkeypatch.setattr(txango.tasks, 'threads', threads)


    func = Mock(name='func')

    task = txango.tasks.Task(func, False)
    task.delay(sentinel.a, b=sentinel.b)

    func.assert_called_with(sentinel.a,
                            b=sentinel.b)


def test_blocking_task(monkeypatch, reactor):
    monkeypatch.setattr(txango.tasks, 'reactor', reactor)
    threads = Mock(name='threads')
    monkeypatch.setattr(txango.tasks, 'threads', threads)

    task = txango.tasks.Task(sentinel.func, True)
    task.delay(sentinel.a, b=sentinel.b)

    threads.deferToThread.assert_called_with(sentinel.func,
                                             sentinel.a,
                                             b=sentinel.b)

def test_apply_async_eta_countdown():
    task = txango.tasks.Task(None, None)
    
    with pytest.raises(Exception) as excinfo:
        task.apply_async(countdown=True, eta=True)
    assert excinfo.value.message == \
        'eta and countdown can not both be supplied'


def test_apply_async_eta(monkeypatch, reactor):
    monkeypatch.setattr(txango.tasks, 'reactor', reactor)

    task = txango.tasks.Task(None, None)
    task._in_reactor = Mock()

    eta = datetime.datetime.now() + datetime.timedelta(seconds=60)
    task.apply_async(eta=eta)

    assert 58 < task._in_reactor.call_args[0][2] <= 60


def test_apply_async_countdown(monkeypatch, reactor):
    monkeypatch.setattr(txango.tasks, 'reactor', reactor)

    task = txango.tasks.Task(None, None)

    task.apply_async(countdown=120)

    assert reactor.callLater.call_args[0][0] == 120
