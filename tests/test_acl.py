from .base_config_test import BaseConfigTest, fmod

import webtest
import os

from six.moves.urllib.parse import urlencode


# ============================================================================
class TestACLApp(BaseConfigTest):
    @classmethod
    def setup_class(cls):
        super(TestACLApp, cls).setup_class('config_test_access.yaml')

    def query(self, url, coll='pywb'):
        params = {}
        params['url'] = url
        return self.testapp.get('/{coll}/cdx?'.format(coll=coll) + urlencode(params, doseq=1))

    def test_excluded_url(self):
        resp = self.query('http://www.iana.org/')

        assert len(resp.text.splitlines()) == 0

        self.testapp.get('/pywb/mp_/http://www.iana.org/', status=404)

    def test_blocked_url(self):
        resp = self.query('http://www.iana.org/about/')

        assert len(resp.text.splitlines()) == 1

        resp = self.testapp.get('/pywb/mp_/http://www.iana.org/about/', status=451)

        assert 'Access Blocked' in resp.text

    def test_allowed_more_specific(self):
        resp = self.query('http://www.iana.org/_css/2013.1/fonts/opensans-semibold.ttf')

        assert resp.status_code == 200

        assert len(resp.text.splitlines()) > 0

        resp = self.testapp.get('/pywb/mp_/http://www.iana.org/_css/2013.1/fonts/opensans-semibold.ttf', status=200)

        assert resp.content_type == 'application/octet-stream'

    def test_default_rule_blocked(self):
        resp = self.query('http://httpbin.org/anything/resource.json')

        assert len(resp.text.splitlines()) > 0

        resp = self.testapp.get('/pywb/mp_/http://httpbin.org/anything/resource.json', status=451)

        assert 'Access Blocked' in resp.text

    def test_allowed_different_coll_acl_list(self):
        resp = self.query('http://httpbin.org/anything/resource.json', coll='pywb-acl-list')

        assert len(resp.text.splitlines()) > 0

        resp = self.testapp.get('/pywb-acl-list/mp_/http://httpbin.org/anything/resource.json')

        assert '"http://httpbin.org/anything/resource.json"' in resp.text

    def test_allowed_different_coll_acl_dir(self):
        resp = self.query('http://httpbin.org/anything/resource.json', coll='pywb-acl-dir')

        assert len(resp.text.splitlines()) > 0

        resp = self.testapp.get('/pywb-acl-dir/mp_/http://httpbin.org/anything/resource.json')

        assert '"http://httpbin.org/anything/resource.json"' in resp.text



