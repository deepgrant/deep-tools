from distutils.core import setup
from distutils.command.install import install
import os
import shutil

class issue(Exception):
    def __init__(self, errorStr):
        self.errorStr = errorStr
    def __str__(self):
        return repr(self.errorStr)

class post_install(install):

    def copyStuff(self, dataDir, destDir):
        if os.path.isdir(dataDir) == False:
            os.makedirs(dataDir)

        _bsDir = os.path.abspath(destDir)

        if os.path.exists(_bsDir) == False:
            raise issue('No files at: ' % (_bsDir,))

        _files = [_bsDir+'/'+_file for _file in os.listdir(_bsDir)]
        for _file in _files:
            print 'copying %s -> %s' % (_file, dataDir,)
            shutil.copy2(_file, dataDir)

    def run(self):

        install.run(self)


setup(cmdclass     = {'install': post_install},
      name         = 'deeptools',
      description  = 'Deep Tools',
      author       = 'Deep Grant',
      author_email = 'ralph.wiggum@icloud.com',
      url          = 'http://deepis.com',
      version      = '0.1',
      packages     = ['deep',
                      'deep.tools',
                      ],
      scripts      = ['scripts/clusterDb.py',
                      ]
      )
