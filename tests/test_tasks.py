import txango.tasks

from mock import Mock, sentinel


def test_nonblocking_task(monkeypatch):
    reactor = Mock(name='reactor')
    monkeypatch.setattr(txango.tasks, 'reactor', reactor)
    threads = Mock(name='threads')
    monkeypatch.setattr(txango.tasks, 'threads', threads)

    task = txango.tasks.Task(sentinel.func, False)
    task.delay(sentinel.a, b=sentinel.b)

    reactor.callFromThread.assert_called_with(sentinel.func,
                                              sentinel.a,
                                              b=sentinel.b)


def test_blocking_task(monkeypatch):
    reactor = Mock(name='reactor')
    monkeypatch.setattr(txango.tasks, 'reactor', reactor)
    threads = Mock(name='threads')
    monkeypatch.setattr(txango.tasks, 'threads', threads)

    def call_it(f):
        f()
    reactor.callFromThread.side_effect = call_it

    task = txango.tasks.Task(sentinel.func, True)
    task.delay(sentinel.a, b=sentinel.b)

    threads.deferToThread.assert_called_with(sentinel.func,
                                             sentinel.a,
                                             b=sentinel.b)
