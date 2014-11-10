from bricks.staticfiles import StaticCss, StaticJs

asset_prefix = 'bricks:test/test_components/static/'

testcss = StaticCss('testcss', asset=asset_prefix + 'css/style.css')
testjs = StaticJs('jstest', asset=asset_prefix + 'js/what.js')

externalcss = StaticCss('externalcss', asset='http://www.somecdn.com/style.css')
externaljs = StaticJs('externaljs', asset='http://www.somecdn.com/what.js')
