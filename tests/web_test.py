import unittest
import flask
import tempfile
import sys
import os
from StringIO import StringIO
from web import create_app

class WebTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def assertResponse(self, text, filename, extra_params=None, assertion=None):
        """ the caller function must be named test_<converter_id> """
        if not assertion:
            assertion = self.assertIn
        data = {}
        converter_id = sys._getframe(1).f_code.co_name[5:]
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with file(filename) as f:
            if extra_params:
                data.update(extra_params)
            data['file'] = (f, 'test.ext')
            resp = self.client.post("/convert/%s" %converter_id, data=data)
            assertion(text, resp.data)

    def test_home(self):
        resp = self.client.get("/")
        self.assertEqual(200, resp.status_code)

    def test_converters_list(self):
        resp = self.client.get("/list")
        import json
        self.assertIn('rar2list', json.loads(resp.data)['list'])

    def test_converters_params(self):
        """
        Converter params:
            id, title, convert_url, ct_input,
            ct_output, ct_schema, ct_extraparams,
            description, suffix
        """
        with self.app.test_request_context():
            resp = self.client.get("/params")
            import json
            self.assertIn(
                ['%srar2list' %self.app.config.get('PREFIX', ''), #id
                 'List of contents (%s)' %self.app.config.get('TAG', ''), #title
                 'convert/rar2list', #convert_url
                 'application/x-rar-compressed', #ct_input
                 'text/plain;charset="utf-8"', #ct_output
                 '', #ct_schema
                 [], #ct_extraparams
                 '', #description
                 ''], #suffix
                json.loads(resp.data)['list']
            )
        prefix = self.app.config.get('PREFIX', None)
        if prefix:
            self.assertIn(prefix, json.loads(resp.data).get('prefix'))

    def test_unknown_converter(self):
        data = {}
        data['file'] = (StringIO("file data"), 'file.unk')
        resp = self.client.post("/convert/unknown", data=data)
        self.assertEqual(500, resp.status_code)

    def test_gmltopng_thumb(self):
        self.assertResponse('PNG', 'tests/gml_data/world.gml')

    def test_msxls2html(self):
        self.assertResponse('test file', 'tests/xls_data/test.xls')

    def test_vndmsxls2html(self):
        self.assertResponse('test file', 'tests/xls_data/test.xls')

    def test_xsl2html(self):
        self.assertResponse('test file', 'tests/xls_data/test.xls')

    def test_ppt2html(self):
        self.assertResponse('pptHtml', 'tests/ppt_data/test.ppt')

    def test_vndmsppt2html(self):
        self.assertResponse('pptHtml', 'tests/ppt_data/test.ppt')

    def test_ziplist(self):
        self.assertResponse('fisier.txt', 'tests/zip_data/test.zip')

    def test_msword2text(self):
        self.assertResponse('test .doc file', 'tests/doc_data/test.doc')

    def test_accesstables(self):
        self.assertResponse('Purchases', 'tests/mdb_data/test.mdb')

    def test_msword2html(self):
        self.assertResponse('test .doc file', 'tests/doc_data/test.doc')

    def test_ziplist2(self):
        self.assertResponse('fisier.txt', 'tests/zip_data/test.zip')

    def test_pdftohtml(self):
        self.assertResponse('Flask&#160;Documentation', 'tests/pdf_data/sample.pdf')

    def test_odt2html(self):
        self.assertResponse('test .odt file', 'tests/odt_data/test.odt')

    def test_ods2html(self):
        self.assertResponse('test file', 'tests/ods_data/test.ods')

    @unittest.skip('broken converter?') #NOTE ask about it
    def test_flash_ext_png(self):
        data = dict(minx=None, miny=None, maxx=None, maxy=None, server=None, service=None)
        self.assertResponse('PNG', 'tests/gml_data/world.gml', extra_params=data)

    @unittest.skip('wrong command?') #NOTE ask about it
    def test_gmltoflash(self):
        self.assertResponse('test file', 'tests/ods_data/test.ods')

    @unittest.skip('command needs a schema') #TODO implement later
    def test_gmltoshp(self):
        self.assertResponse('test file', 'tests/gml_data/world.gml')

    def test_gmltokml(self):
        self.assertResponse('<kml', 'tests/gml_data/world.gml')

    @unittest.skip('command needs a country') #TODO implement later
    def test_gmltopng_thumb_bg(self):
        self.assertResponse('PNG', 'tests/gml_data/world.gml')

    def test_gmltopng(self):
        self.assertResponse('PNG', 'tests/gml_data/world.gml')

    def test_gmltopng_thumb(self):
        self.assertResponse('PNG', 'tests/gml_data/world.gml')

    @unittest.skip('command needs a country') #TODO implement later
    def test_gmltopng_bg(self):
        self.assertResponse('PNG', 'tests/gml_data/world.gml')

    def test_rar2list(self):
        self.assertResponse('fisier.txt', 'tests/rar_data/onefile.rar')

    def test_rar2list2(self):
        self.assertResponse('fisier.txt', 'tests/rar_data/onefile.rar')

    @unittest.skip('missing dbflib.py') #TODO implement later
    def test_dbf_as_html(self):
        self.assertResponse('fisier.txt', 'tests/dbf_data/test.dbf')

    def test_prj_as_html(self):
        self.assertResponse('Lambert_Conformal_Conic', 'tests/prj_data/test.prj')

    def test_list_7zip(self):
        self.assertResponse('one.txt', 'tests/sz_data/twofiles.7z')

    def test_txt_to_wkt(self):
        self.assertResponse('test file', 'tests/txt_data/test.txt')

    @unittest.skip('missing ogr2ogr') #TODO implement later
    def test_shp2kml(self):
        self.assertResponse('command not found',
                                 'tests/shp_data/test.shp',
                                 self.assertNotIn)
        self.assertResponse('<kml', 'tests/shp_data/test.shp')

    @unittest.skip('command error') #TODO implement later
    def test_shp_info(self):
        self.assertResponse('<kml', 'tests/shp_data/test.shp')

    @unittest.skip('command error') #TODO implement later
    def test_shp2img(self):
        self.assertResponse('<kml', 'tests/shp_data/test.shp')

    @unittest.skip('command error') #TODO implement later
    def test_SHP2img(self):
        self.assertResponse('Error',
                            'tests/shp_data/test.shp',
                            self.assertNotIn)
