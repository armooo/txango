import txango.management.commands.runserver as runserver

from mock import Mock, sentinel


def test_handle(monkeypatch):
    from django.core.management.commands.runserver import BaseRunserverCommand
    from StringIO import StringIO
    import django.conf
    import twisted.internet
    import twisted.python.threadpool
    import twisted.web.wsgi
    import twisted.web.server

    validate = Mock(name='validate')
    monkeypatch.setattr(runserver.Command, 'validate', validate)
    settings = Mock(name='settings')
    settings.SETTINGS_MODULE = '--settings module--'
    monkeypatch.setattr(runserver, 'settings', settings)
    django_resource = Mock(name='django_resource')
    django_resource.return_value = sentinel.django_resource
    monkeypatch.setattr(runserver, 'django_resource', django_resource)
    reactor = Mock(name='reactor')
    monkeypatch.setattr(runserver, 'reactor', reactor)
    site = Mock(name='site')
    monkeypatch.setattr(twisted.web.server, 'Site', site)

    cmd = runserver.Command()
    cmd.stdout = StringIO()

    options = {'use_reloader': False,
               'admin_media_path': sentinel.admin_media}
    cmd.handle(**options)

    #  test
    validate.assert_called_with(display_num_errors=True)
    site.assert_called_with(sentinel.django_resource)
    reactor.listenTCP.assert_called_with(8000, site.return_value, interface='127.0.0.1')
