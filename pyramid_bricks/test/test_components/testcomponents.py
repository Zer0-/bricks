from pyramid_bricks.staticfiles import StaticCss, StaticJs, ExternalCss, ExternalJs

asset_prefix = 'pyramid_bricks:test/test_components/static/'

testcss = StaticCss('testcss', asset=asset_prefix + 'css/style.css')
testjs = StaticJs('jstest', asset=asset_prefix + 'js/what.js')

externalcss = ExternalCss('externalcss', url='http://www.somecdn.com/style.css')
externaljs = ExternalJs('externaljs', url='http://www.somecdn.com/what.js')
