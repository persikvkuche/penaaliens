from setuptools import setup, Extension

module = Extension(
    'file_search',
    sources=['finder_mod.c', 'finder.c']
)

setup(
    name='FileSearchModule',
    version='1.0',
    description='iluha koldun sdelal bodun',
    ext_modules=[module]
)
