from setuptools import setup

requires = [
    'setuptools',
    'webob',
    'ceramic_forms',
    'mako'
]

links = [
    'git+https://github.com/Zer0-/Ceramic-Forms.git#egg=ceramic_forms'
]

setup(
    name='bricks',
    version='0.0',
    description='Creation of small, extendable web components.',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Philipp Volguine',
    author_email='phil.volguine@gmail.com',
    packages=['bricks'],
    include_package_data=True,
    install_requires=requires,
    dependency_links=links,
)
