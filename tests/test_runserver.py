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

    #  patchs for get_handler
    ahm = Mock(name='amh', return_value=sentinel.amh_instance)
    monkeypatch.setattr(runserver, 'AdminMediaHandler', ahm)
    base_get_handler = Mock(name='base_get_handler',
                            return_value=sentinel.handler)
    monkeypatch.setattr(BaseRunserverCommand, 'get_handler', base_get_handler)

    # patchs inner_run
    validate = Mock(name='validate')
    monkeypatch.setattr(runserver.Command, 'validate', validate)
    settings = Mock(name='settings')
    settings.SETTINGS_MODULE = '--settings module--'
    monkeypatch.setattr(django.conf, 'settings', settings)
    thread_pool = Mock(name='thread_pool')
    thread_pool.return_value.start = sentinel.tp_start
    thread_pool.return_value.stop = sentinel.tp_stop
    monkeypatch.setattr(twisted.python.threadpool, 'ThreadPool', thread_pool)
    reactor = Mock(name='reactor')
    monkeypatch.setattr(runserver, 'reactor', reactor)
    wsgi_resource = Mock(name='wsgi_resource')
    monkeypatch.setattr(twisted.web.wsgi, 'WSGIResource', wsgi_resource)
    site = Mock(name='site')
    monkeypatch.setattr(twisted.web.server, 'Site', site)

    cmd = runserver.Command()
    cmd.stdout = StringIO()

    options = {'use_reloader': False,
               'admin_media_path': sentinel.admin_media}
    cmd.handle(**options)

    #  test
    ahm.assert_called_with(sentinel.handler, sentinel.admin_media)
    validate.assert_called_with(display_num_errors=True)
    reactor.callWhenRunning.assert_called_with(sentinel.tp_start)
    reactor.addSystemEventTrigger.assert_called_with('after',
                                                     'shutdown',
                                                      sentinel.tp_stop)
    wsgi_resource.assert_called_with(reactor,
                                    thread_pool.return_value,
                                    sentinel.amh_instance)
    site.assert_called_with(wsgi_resource.return_value)
    reactor.listenTCP.assert_called_with(8000, site.return_value, interface='127.0.0.1')
