import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import runserver
from django.utils import autoreload

from twisted.internet import reactor
from twisted.python import threadpool
from twisted.web import server, wsgi

class Command(runserver.BaseRunserverCommand):
    help = "Starts a twisted Web server."

    requires_model_validation = False

    def handle(self, addrport='', *args, **options):
        super(Command, self).handle(addrport, *args, **options)

    def inner_run(self, *args, **options):
        from django.conf import settings
        from django.utils import translation

        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        self.stdout.write("Validating models...\n\n")
        self.validate(display_num_errors=True)
        self.stdout.write((
             "Django version %(version)s, using settings %(settings)r\n"
             "Twisted web server is running at http://%(addr)s:%(port)s/\n"
             "Quit the server with %(quit_command)s.\n"
        ) % {
             "version": self.get_version(),
             "settings": settings.SETTINGS_MODULE,
             "addr": self._raw_ipv6 and '[%s]' % self.addr or self.addr,
             "port": self.port,
             "quit_command": quit_command,
         })

        application = self.get_handler(*args, **options)

        pool = threadpool.ThreadPool()
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        wsgi_resource = wsgi.WSGIResource(reactor, pool, application)
        site = server.Site(wsgi_resource)

        reactor.listenTCP(int(self.port), site, interface=self.addr)
        reactor.run(installSignalHandlers=0)
