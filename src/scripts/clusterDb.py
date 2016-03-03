#!/usr/bin/env python

################################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Deep Grant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import commands
import os
import shlex
import subprocess
import string
import sys

import deep.tools.exception as exception


class issue(exception.issue):
    def __init__(self, errorStr):
        exception.issue.__init__(self, errorStr)


#function clusterinitdb() {
#  cdmysql "$1"
#
#  ./bin/mysqld --initialize-insecure --deep-dynamic-resources=1 --basedir="${PWD}" --datadir="${PWD}/data1"
#  ./bin/mysqld --initialize-insecure --deep-dynamic-resources=1 --basedir="${PWD}" --datadir="${PWD}/data2"
#  ./bin/mysqld --initialize-insecure --deep-dynamic-resources=1 --basedir="${PWD}" --datadir="${PWD}/data3"
#}

__cluster = """
[ndbd default]
noofreplicas=1

[ndbd]
hostname=localhost
id=2

[ndbd]
hostname=localhost
id=3

[ndb_mgmd]
id = 1
hostname=localhost

[mysqld]
id=4
hostname=localhost

[mysqld]
id=5
hostname=localhost

"""

_my_conf = """
[mysqld]
ndb-nodeid=${node}
ndbcluster
datadir=${datadir}
basedir=${basedir}
port=${port}
server-id=${server}
log-bin
"""

class DeepSQLSetup(object):
    """
    Cluster and standalone setup of DeepSQL
    """
    def __init__(self, version = 'deepsql-5.7.11'):
        """
        """
        self.__version = version
        self.__basedir = None

    def setDevDir(self, basedir= '~/Development/deep/'):

        _basedir = os.path.expanduser(basedir)

        if False == os.path.exists(_basedir):
            raise issue('Does not exist: %s' % (basedir,))

        _temp    = string.Template('${bd}/THIRDPARTY/trunk/MySQL/deep/install/dist/${distribution}/usr/local/mysql')

        self.__basedir = _temp.substitute(bd           = _basedir,
                                          distribution = self.__version,)


        if False == os.path.exists(self.__basedir):
            raise issue('Does not exist: %s' % (self.__basedir,))

    def getDataDir(self, suffix='data'):
        """
        Configure the datadir off the basedir
        """
        if None == self.__basedir:
            raise issue('The baseDir has not been setup!')

        _datadir = self.__basedir + ('/%s' % (suffix,))
        return _datadir

    def _execute(self, command):
        """
        Execute and track the output of the subprocess.
        """
        _proc = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)


        while True:
            output = _proc.stdout.readline()
            if output == '' and _proc.poll() is not None:
                break
            if output:
                print output.strip()
            rc = _proc.poll()

        return rc

    def startdb(self):
        """
        Start a single DeepSQL daemon
        """
        # Initialize the datadir if it is not there.
        _data = self.getDataDir()

        self.initdb(_data)

        _temp = string.Template('${basedir}/bin/mysqld --socket=/tmp/mysql.sock --basedir="${basedir}" --datadir="${datadir}" --default-storage-engine=deep --deep_log_level_debug=ON --bind-address=0.0.0.0')

        _cmd  = _temp.substitute(basedir = self.__basedir,
                                 datadir = _data)

        _cmd = shlex.split(_cmd)

        return self._execute(_cmd)


    def initdb(self, datadir):
        """
        Initialize the datadir
        """
        if True == os.path.exists(datadir):
            return None

        _temp = string.Template('${basedir}/bin/mysqld --initialize-insecure --deep-dynamic-resources=1 --basedir=${basedir} --datadir=${datadir}')

        _cmd  = _temp.substitute(basedir = self.__basedir,
                                 datadir = datadir)

        _cmd  = shlex.split(_cmd)

        return self._execute(_cmd)

    def clusterCfg(self):
        """
        Configure a local MySQL cluster.
        """
        _data = self.getDataDir('data1')
        _temp = string.Template(_my_conf)
        _my   = _temp.substitute(basedir = self.__basedir,
                                 datadir = _data,
                                 node    = 4,
                                 port    = 3306,
                                 server  = 1)

        self.initdb(_data)

################################################################################

if __name__ == "__main__":
    _setup = DeepSQLSetup()
    _setup.setDevDir()

    #_cwd = _setup.getDataDir()
    #_setup.startdb()

    _setup.clusterCfg()
