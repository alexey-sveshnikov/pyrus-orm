from distutils.core import setup

setup(
    name='pyrus-orm',
    version='0.1',
    author='Alexey Sveshnikov',
    packages=['pyrus_orm'],
    requires=[
        'pyrus-api'
    ]
)
