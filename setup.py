from setuptools import setup

requires = [
    'pyramid',
    'pyramid_mako'
]

setup(
    name='pyramid_bricks',
    version='0.0',
    description='Creation of small, extendable web components.',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Philipp Volguine',
    author_email='phil.volguine@gmail.com',
    packages=['pyramid_bricks'],
    include_package_data=True,
    install_requires=requires,
)
