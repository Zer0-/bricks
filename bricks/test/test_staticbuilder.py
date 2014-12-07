import unittest
from os.path import join
from bricks import Bricks
from bricks.static_manager import StaticManager
from bricks.static_builder import establish_static_assets
from bricks.test.test_components.testcomponents import (
    testcss,
    testjs,
    externalcss,
    externaljs,
)

def file_contents_match(filepath, str_content):
    with open(filepath, 'r') as f:
        filecontents = f.read()
    return filecontents == str_content

class Settings(dict):
    provides = ['json_settings']

    def __init__(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self['served_static_dir'] = self.tmp
        self['served_static_url'] = 'http://localhost:8888/'

    def cleanup(self):
        from shutil import rmtree
        rmtree(self.tmp)

class TestStaticBuilder(unittest.TestCase):
    def setUp(self):
        self.pbricks = Bricks()
        for c in [
            Settings,
            StaticManager,
            testcss,
            testjs,
            externaljs,
            externalcss
        ]:
            self.pbricks.add(c)

    def tearDown(self):
        self.pbricks.components['json_settings'].cleanup()

    def testSimpleStaticCopy(self):
        establish_static_assets(self.pbricks)
        out_dir = self.pbricks.components['json_settings']['served_static_dir']
        ftests = [
            ('test_components/static/style.css', 'body{background-color: teal;}\n'),
            ('test_components/static/what.js', 'function(){};\n')
        ]
        for fname, contents in ftests:
            match = file_contents_match(join(out_dir, fname), contents)
            self.assertTrue(match)

    def testAssetUrls(self):
        js = self.pbricks.components[testjs]
        css = self.pbricks.components[testcss]
        ext_css = self.pbricks.components[externalcss]
        asseturls = [
            (js, 'http://localhost:8888/test_components/static/what.js'),
            (css, 'http://localhost:8888/test_components/static/style.css'),
            (ext_css, 'http://www.somecdn.com/style.css'),
        ]
        for asset, url in asseturls:
            self.assertEqual(asset.url, url)

if __name__ == '__main__':
    unittest.main()
