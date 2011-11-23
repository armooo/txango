from mock import Mock, sentinel

from django.core.files.storage import Storage

import txango.resource as resource

class TestStaticResource(object):
    def test_prefix(self, monkeypatch):
        settings = Mock(name='settings')
        settings.STATIC_URL = '/static/'
        monkeypatch.setattr(resource, 'settings', settings)
        File = Mock(name='file', return_value=sentinel.file)
        monkeypatch.setattr(resource.static, 'File', File)

        storage = Mock(name='storage')
        storage.path.return_value = '/tmp/file1'
        storage.prefix = 'test'
        finder = Mock(name='finder')
        finder.list.return_value = (('img/1.jpg', storage), )

        sr = resource.StaticResource([finder], None)

        r = sr.getChildWithDefault('static', None)
        r = r.getChildWithDefault('test', None)
        r = r.getChildWithDefault('img', None)
        r = r.getChildWithDefault('1.jpg', None)

        assert r == sentinel.file
        File.assert_called_with('/tmp/file1')

    def test_no_prefix(self, monkeypatch):
        settings = Mock(name='settings')
        settings.STATIC_URL = '/static/'
        monkeypatch.setattr(resource, 'settings', settings)
        File = Mock(name='file', return_value=sentinel.file)
        monkeypatch.setattr(resource.static, 'File', File)

        storage = Mock(spec=Storage, name='storage')
        storage.path.return_value = '/tmp/file1'
        finder = Mock(name='finder')
        finder.list.return_value = (('img/1.jpg', storage), )

        sr = resource.StaticResource([finder], None)

        r = sr.getChildWithDefault('static', None)
        r = r.getChildWithDefault('img', None)
        r = r.getChildWithDefault('1.jpg', None)

        assert r == sentinel.file
        File.assert_called_with('/tmp/file1')

    def test_no_static_url(self, monkeypatch):
        settings = Mock(name='settings')
        settings.STATIC_URL = None
        monkeypatch.setattr(resource, 'settings', settings)

        storage = Mock(spec=Storage, name='storage')
        storage.path.return_value = '/tmp/file1'
        finder = Mock(name='finder')
        finder.list.return_value = (('img/1.jpg', storage), )

        sr = resource.StaticResource([finder], None)

    def test_default(self, monkeypatch):
        settings = Mock(name='settings')
        settings.STATIC_URL = '/static/'
        monkeypatch.setattr(resource, 'settings', settings)

        request = Mock(name='request')
        request.prepath = ['admin']
        request.postpath = ['magic']

        sr = resource.StaticResource([], sentinel.default)
        r = sr.getChildWithDefault('admin', request) 

        assert r == sentinel.default
        assert request.prepath == []
        assert request.postpath == ['admin', 'magic']

def test_django_resource(monkeypatch):
    pool = Mock(name='pool')
    ThreadPool = Mock(name='ThreadPool', return_value=pool)
    monkeypatch.setattr(resource.threadpool, 'ThreadPool', ThreadPool)
    reactor = Mock(name='reactor')
    monkeypatch.setattr(resource, 'reactor', reactor)
    WSGIResource = Mock(name='WSGIResource', return_value=sentinel.wsgir)
    monkeypatch.setattr(resource.wsgi, 'WSGIResource', WSGIResource)
    StaticResource = Mock(name='StaticResource', return_value=sentinel.staticr)
    monkeypatch.setattr(resource, 'StaticResource', StaticResource)

    r = resource.django_resource(sentinel.app)

    reactor.callWhenRunning.assert_called_with(pool.start)
    reactor.addSystemEventTrigger.assert_called_with('after',
                                                     'shutdown',
                                                     pool.stop)
    WSGIResource.assert_called_with(reactor, pool, sentinel.app)
    assert r == sentinel.staticr
