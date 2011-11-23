import sys
from optparse import make_option

from django.conf import settings
from django.core.management.commands import runserver

from twisted.internet import reactor
from twisted.web import server

from txango.resource import django_resource


class Command(runserver.BaseRunserverCommand):
    help = "Starts a twisted Web server."

    def inner_run(self, *args, **options):
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

        applacation = self.get_handler(*args, **options)
        site = server.Site(django_resource())
        reactor.listenTCP(int(self.port), site, interface=self.addr)
        reactor.run(installSignalHandlers=0)
