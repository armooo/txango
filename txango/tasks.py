import datetime

from twisted.internet import reactor
from twisted.internet import threads


class Task(object):
    """
        Wraps a callable so it can be used as a Task. This is a celeryish task
        api.

        func: The callable which will run
        blocking: Is this callable going to block
    """
    def __init__(self, func, blocking):
        self._func = func
        self._blocking = blocking

    def delay(self, *args, **kwargs):
        """
            Starts this task in the background.
        """
        return self.apply_async(args, kwargs)

    def apply_async(self, args=None, kwargs=None, countdown=None, eta=None):
        if eta and countdown:
            raise Exception('eta and countdown can not both be supplied')
        if eta:
            td = eta - datetime.datetime.now()
            countdown = td.days * 24 * 3600 + td.seconds + \
                        td.microseconds / 10**6
        reactor.callFromThread(self._in_reactor, args, kwargs, countdown)

    def _in_reactor(self, args, kwargs, countdown):
        if countdown:
            reactor.callLater(countdown, self._run, args, kwargs)
        else:
            self._run(args, kwargs)

    def _run(self, args, kwargs):
        if self._blocking:
            threads.deferToThread(self._func, *args, **kwargs)
        else:
            self._func(*args, **kwargs)

    def __repr__(self):
        return '<Task blocking=%s for %r>' % (self._blocking, self._func)


def task(f):
    return Task(f, True)


def twisted_task(f):
    return Task(f, False)
