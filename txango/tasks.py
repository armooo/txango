from twisted.internet import reactor
from twisted.internet import threads


class Task(object):
    """
        Wraps a callable so it can be used as a Task.

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
        if self._blocking:
            # We should setup our own thread pool
            # Do we need to deferToThread from the IO thread not sure if it is
            # thread safe so lets play it safe
            def f():
                threads.deferToThread(self._func, *args, **kwargs)
            reactor.callFromThread(f)
        else:
            reactor.callFromThread(self._func, *args, **kwargs)


    def __repr__(self):
        return '<Task blocking=%s for %r>' % (self._blocking, self._func)


def task(f):
    return Task(f, True)


def twisted_task(f):
    return Task(f, False)
