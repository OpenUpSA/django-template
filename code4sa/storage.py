import codecs

import os
import fnmatch
import scss

from django.conf import settings
from django.contrib.staticfiles import finders

from whitenoise.django import GzipManifestStaticFilesStorage
from pipeline.storage import PipelineMixin
from pipeline.compilers import SubProcessCompiler


class GzipManifestPipelineStorage(PipelineMixin, GzipManifestStaticFilesStorage):
    pass


def finder(glob):
    for finder in finders.get_finders():
        for path, storage in finder.list([]):
            if fnmatch.fnmatchcase(path, glob):
                yield path, storage

# this is where pyScss looks for images and static data
scss.STATIC_ROOT = finder
scss.STATIC_URL = settings.STATIC_URL

# this is where pyScss outputs the generated/compiled files
scss.ASSETS_ROOT = os.path.join(settings.MEDIA_ROOT, 'assets/')
scss.ASSETS_URL = settings.MEDIA_URL + 'assets/'


class PyScssCompiler(SubProcessCompiler):
    output_extension = 'css'

    def match_file(self, filename):
        return filename.endswith('.scss')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        if not outdated and not force:
            return

        result = scss.compiler.compile_file(
            infile,
            search_path=settings.PYSCSS_LOAD_PATHS)

        with codecs.open(outfile, 'w', encoding='utf-8') as f:
            f.write(result)
