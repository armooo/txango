from django.conf import settings
import django.core.handlers.wsgi
from django.contrib.staticfiles import finders

from twisted.internet import reactor
from twisted.python import threadpool
from twisted.web import server, wsgi, resource, static

class StaticResource(resource.Resource):
    """
    Resource to server static content like django.contrib.staticfiles.

    Set up a resource tree to host all of the static files returned by the
    finders in the list. All requests which can not be served by the static
    content are sent to default.
    """
    def __init__(self, finders, default):
        resource.Resource.__init__(self)
        self._default = default

        if settings.STATIC_URL:
            self._add_files_from_finders(finders)

    def _add_files_from_finders(self, finders):
        for finder in finders:
            for path, storage in finder.list([]):
                file_path = storage.path(path)
                if getattr(storage, 'prefix', None):
                    path = '%s/%s' % (storage.prefix, path)
                self._add_static_file(path, file_path)

    def _add_static_file(self, path, fn):
        path = settings.STATIC_URL.split('/') + path.split('/')
        path = [seg for seg in path if seg]

        parent = self
        for seg in path[:-1]:
            next_parent = parent.children.get(seg)
            if not next_parent:
                next_parent = resource.Resource()
                parent.putChild(seg, next_parent)
            parent = next_parent
        new_file = static.File(fn)
        parent.putChild(path[-1], new_file)

    def getChild(self, path, request):
        #  Hack the request so it ignores me
        request.prepath.pop()
        request.postpath.insert(0, path)
        return self._default


def django_resource(application=None):
    if not application:
        application = django.core.handlers.wsgi.WSGIHandler()

    pool = threadpool.ThreadPool()
    reactor.callWhenRunning(pool.start)
    reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
    wsgi_resource = wsgi.WSGIResource(reactor, pool, application)
    return StaticResource(finders.get_finders(), wsgi_resource)
