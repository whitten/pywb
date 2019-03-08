from pywb.warcserver.test.testutils import BaseTestClass, key_ts_res

from pywb.warcserver.index.indexsource import XmlQueryIndexSource
from pywb.warcserver.index.aggregator import SimpleAggregator

from mock import patch
import pytest


# ============================================================================
def mock_get(self, url):
    string = ''
    if 'type%3Aurlquery' in url:
        if 'http%253A%252F%252Fexample.com%252Fsome%252Fpath' in url:
            string = URL_RESPONSE_2

        elif 'http%253A%252F%252Fexample.com%252F' in url:
            string = URL_RESPONSE_1

    elif 'type%3Aprefixquery' in url:
        string = PREFIX_QUERY

    class MockResponse(object):
        def __init__(self, string):
            self.string = string

        @property
        def text(self):
            return self.string

        @property
        def content(self):
            return self.string.encode('utf-8')

        def raise_for_status(self):
            pass


    return MockResponse(string)


# ============================================================================
class TestXmlQueryIndexSource(BaseTestClass):
    @classmethod
    def setup_class(cls):
        super(TestXmlQueryIndexSource, cls).setup_class()

        cls.xmlpatch = patch('pywb.warcserver.index.indexsource.etree', cls._get_etree())
        cls.xmlpatch.start()

    @classmethod
    def _get_etree(cls):
        import xml.etree.ElementTree as etree
        return etree

    @classmethod
    def teardown_class(cls):
        cls.xmlpatch.stop()
        super(TestXmlQueryIndexSource, cls).teardown_class()

    def do_query(self, params):
        return SimpleAggregator({'source': XmlQueryIndexSource('http://localhost:8080/path')})(params)

    @patch('pywb.warcserver.index.indexsource.requests.sessions.Session.get', mock_get)
    def test_exact_query(self):
        res, errs = self.do_query({'url': 'http://example.com/'})
        expected = """\
com,example)/ 20180112200243 example.warc.gz
com,example)/ 20180216200300 example.warc.gz"""
        assert(key_ts_res(res) == expected)
        assert(errs == {})


    @patch('pywb.warcserver.index.indexsource.requests.sessions.Session.get', mock_get)
    def test_exact_query_2(self):
        res, errs = self.do_query({'url': 'http://example.com/some/path'})
        expected = """\
com,example)/some/path 20180112200243 example.warc.gz
com,example)/some/path 20180216200300 example.warc.gz"""
        assert(key_ts_res(res) == expected)
        assert(errs == {})


    @patch('pywb.warcserver.index.indexsource.requests.sessions.Session.get', mock_get)
    def test_prefix_query(self):
        res, errs = self.do_query({'url': 'http://example.com/', 'matchType': 'prefix'})
        expected = """\
com,example)/ 20180112200243 example.warc.gz
com,example)/ 20180216200300 example.warc.gz
com,example)/some/path 20180112200243 example.warc.gz
com,example)/some/path 20180216200300 example.warc.gz"""
        assert(key_ts_res(res) == expected)
        assert(errs == {})


# ============================================================================
class TestXmlQueryIndexSourceLXML(TestXmlQueryIndexSource):
    @classmethod
    def _get_etree(cls):
        pytest.importorskip('lxml.etree')
        import lxml.etree
        return lxml.etree


# ============================================================================
URL_RESPONSE_1 = """
<wayback>
   <results>
       <result>
         <compressedoffset>10</compressedoffset>
         <mimetype>text/html</mimetype>
         <file>example.warc.gz</file>
         <redirecturl>-</redirecturl>
         <urlkey>com,example)/</urlkey>
         <digest>7NZ7K6ZTRC4SOJODXH3S4AGZV7QSBWLF</digest>
         <httpresponsecode>200</httpresponsecode>
         <robotflags>-</robotflags>
         <url>http://example.ccom/</url>
         <capturedate>20180112200243</capturedate>
      </result>
      <result>
         <compressedoffset>29570</compressedoffset>
         <mimetype>text/html</mimetype>
         <file>example.warc.gz</file>
         <redirecturl>-</redirecturl>
         <urlkey>com,example)/</urlkey>
         <digest>LCKPKJJU5VPEN6HUJZ6JUYRGTPFD7ZC3</digest>
         <httpresponsecode>200</httpresponsecode>
         <robotflags>-</robotflags>
         <url>http://example.com/</url>
         <capturedate>20180216200300</capturedate>
      </result>
   </results>
</wayback>
"""

URL_RESPONSE_2 = """
<wayback>
   <results>
       <result>
         <compressedoffset>10</compressedoffset>
         <mimetype>text/html</mimetype>
         <file>example.warc.gz</file>
         <redirecturl>-</redirecturl>
         <urlkey>com,example)/some/path</urlkey>
         <digest>7NZ7K6ZTRC4SOJODXH3S4AGZV7QSBWLF</digest>
         <httpresponsecode>200</httpresponsecode>
         <robotflags>-</robotflags>
         <url>http://example.com/some/path</url>
         <capturedate>20180112200243</capturedate>
      </result>
      <result>
         <compressedoffset>29570</compressedoffset>
         <mimetype>text/html</mimetype>
         <file>example.warc.gz</file>
         <redirecturl>-</redirecturl>
         <urlkey>com,example)/some/path</urlkey>
         <digest>LCKPKJJU5VPEN6HUJZ6JUYRGTPFD7ZC3</digest>
         <httpresponsecode>200</httpresponsecode>
         <robotflags>-</robotflags>
         <url>http://example.com/some/path</url>
         <capturedate>20180216200300</capturedate>
      </result>
  </results>
</wayback>
"""

PREFIX_QUERY = """
<wayback>
    <results>
        <result>
            <urlkey>com,example)/</urlkey>
            <originalurl>http://example.com/</originalurl>
            <numversions>2</numversions>
            <numcaptures>2</numcaptures>
            <firstcapturets>20180112200243</firstcapturets>
            <lastcapturets>20180216200300</lastcapturets>
        </result>
        <result>
            <urlkey>com,example)/some/path</urlkey>
            <originalurl>http://example.com/some/path</originalurl>
            <numversions>2</numversions>
            <numcaptures>2</numcaptures>
            <firstcapturets>20180112200243</firstcapturets>
            <lastcapturets>20180216200300</lastcapturets>
        </result>
    </results>
</wayback>
"""