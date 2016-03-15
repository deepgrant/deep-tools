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

import argparse
import commands
import os
import shlex
import shutil
import subprocess
import string
import sys

import deep.tools.exception as exception


class issue(exception.issue):
    def __init__(self, errorStr):
        exception.issue.__init__(self, errorStr)

class DeepSQLSetup(object):
    """
    Cluster and standalone setup of DeepSQL
    """
    def __init__(self, version = 'deepsql-5.7.11'):
        """
        """
        self.__version = version
        self.__basedir = None

    def setDevDir(self, basedir= '~/Development/deep'):

        _basedir = os.path.expanduser(basedir)

        if False == os.path.exists(_basedir):
            raise issue('Does not exist: %s' % (basedir,))

        _temp    = string.Template('${bd}/THIRDPARTY/trunk/MySQL/deep/install/'\
                                   'dist/${distribution}/usr/local/mysql')

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
        print 80*'#'
        print command
        print 80*'#'

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

    def _executeDumpOutput(self, command, outFile):
        """
        Execute the command and write the STDOUT to a file.
        """
        print 80*'#'
        print command
        print 80*'#'

        _proc = subprocess.Popen(args   = command,
                                 shell  = True,
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.STDOUT)

        _out = _proc.communicate()[0]

        _outfile = open(outFile, 'w')
        _outfile.write(_out)
        _outfile.close()

    def cli(self, mysqlData):
        """
        Start the MySQL CLI.
        """
        _temp = string.Template('${basedir}/bin/mysql '                 \
                                '-u root '                              \
                                '--socket=/tmp/${socket}.sock '         \
        )

        _cmd = _temp.substitute(basedir = self.__basedir,
                                socket  = mysqlData)

        os.system(_cmd)
        return;

    def startdb(self, mysqlData, serverId, port, slave, db):
        """
        Start a single DeepSQL daemon
        """
        # Initialize the datadir if it is not there.
        _data = self.getDataDir(mysqlData)

        self.initdb(_data, serverId)

        if True == slave:
            _tSM = string.Template('--binlog_do_db=${db} --replicate-do-db=${db} --relay-log=${datadir}/mysql-relay-bin.log ')
            _db  = _tSM.substitute(db = db,
                                   datadir = _data)
        else:
            _tSM = string.Template('--binlog_do_db=${db}' )
            _db  = _tSM.substitute(db = db)

        _temp = string.Template('${basedir}/bin/mysqld '                \
                                '--socket=/tmp/${socket}.sock '         \
                                '--basedir="${basedir}" '               \
                                '--datadir="${datadir}" '               \
                                '--default-storage-engine=deep '        \
                                '--deep_log_level_debug=ON '            \
                                '--bind-address=0.0.0.0 '               \
                                '--port=${port} '                       \
                                '--server-id=${server} '                \
                                '--master-info-repository=TABLE '       \
                                '--relay_log_info_repository=TABLE '    \
                                '--log-bin=${datadir}/mysql-bin.log '   \
                                '--gtid-mode=ON '                       \
                                '--enforce-gtid-consistency=ON '        \
                                '--gtid-executed-compression-period=0 ' \
                                '--binlog-format=ROW '                  \
                                '--binlog-checksum=CRC32 '              \
                                '${db} '                                \

        )

        _cmd = _temp.substitute(basedir = self.__basedir,
                                datadir = _data,
                                port    = port,
                                socket  = mysqlData,
                                server  = serverId,
                                db      = _db)

        _cmd = shlex.split(_cmd)

        return self._execute(_cmd)


    def initdb(self, datadir, serverId):
        """
        Initialize the datadir
        """
        if True == os.path.exists(datadir):
            return None

        _temp = string.Template('${basedir}/bin/mysqld '                \
                                '--initialize-insecure '                \
                                '--deep-dynamic-resources=1 '           \
                                '--basedir=${basedir} '                 \
                                '--datadir=${datadir} '                 \
                                '--server-id=${server} '                \
                                '--log-bin=${datadir}/mysql-bin.log '   \
                                '--gtid-mode=ON '                       \
                                '--enforce-gtid-consistency=ON '        \
                                '--gtid-executed-compression-period=0 ' \
        )

        _cmd  = _temp.substitute(basedir = self.__basedir,
                                 datadir = datadir,
                                 server  = serverId)

        _cmd  = shlex.split(_cmd)

        return self._execute(_cmd)


    def dumpMasterDb(self, mysqlData, snapshot):
        """
        Dump the master DB database to a snapshot SQL file.
        """
        _temp = string.Template('${basedir}/bin/mysqldump '             \
                                '-u root '                              \
                                '--socket=/tmp/${socket}.sock '         \
                                '--all-databases '                      \
                                '--flush-privileges '                   \
                                '--single-transaction '                 \
                                '--master-data=2 '                      \
                                '--flush-logs '                         \
                                '--triggers '                           \
                                '--routines '                           \
                                '--events '                             \
                                '--hex-blob '                           \
        )

        _cmd = _temp.substitute(socket   = mysqlData,
                                basedir  = self.__basedir)

        return self._executeDumpOutput(_cmd, snapshot)

################################################################################

def main():
    _parser = argparse.ArgumentParser(description='DeepSQL instance setup.')

    _parser.add_argument('--data',
                         required=True,
                         action='store',
                         dest='data',
                         help='Data Store location for the DB files.',
                         default='deepsql')

    _parser.add_argument('--base',
                         action='store',
                         dest='base',
                         help='Path to the base location for the DeepSQL installation.',
                         default='~/Development/deep')

    _parser.add_argument('--db',
                         action='store',
                         dest='db',
                         help='The database to replicate.',
                         default='test')

    _parser.add_argument('--port',
                         action='store',
                         dest='port',
                         help='Change the DeepSQL server port.',
                         type=int,
                         default=3306)

    _parser.add_argument('--rel',
                         action='store',
                         dest='version',
                         help='DeepSQL version',
                         default='deepsql-5.7.11')

    _parser.add_argument('--server',
                         action='store',
                         dest='server',
                         help='Server ID <int>',
                         type=int,
                         default=1)

    _parser.add_argument('--snapshot',
                         action='store',
                         dest='snapshot',
                         help='Dump the MySQL databases of the data directory to a SQL file',
                         default=None)

    #
    # Boolean Parameters
    #
    _parser.add_argument('--cli',
                         action='store_true',
                         dest='cli',
                         help='Login to the MySQL CLI instead of starting a DeepSQL server instance.',
                         default=False)

    _parser.add_argument('--rm',
                         action='store_true',
                         help='Delete the data directory when DeepSQL exits.',
                         default=False)

    _parser.add_argument('--slave',
                         action='store_true',
                         dest='slave',
                         help='Setting up this is a slave. If not specified then assume \'master\'',
                         default=False)

    _args  = _parser.parse_args()
    _setup = DeepSQLSetup(_args.version)
    _setup.setDevDir(_args.base)

    if False == _args.cli:
        if None != _args.snapshot:
            _snapshot = os.path.expanduser(_args.snapshot)

            _setup.dumpMasterDb(_args.data,
                                _snapshot)
        else:
            _setup.startdb(_args.data,
                           _args.server,
                           _args.port,
                           _args.slave,
                           _args.db)

            if True == _args.rm:
                _pwd = _setup.getDataDir(_args.data)
                if (True == os.path.exists(_pwd) and True == os.path.isdir(_pwd)):
                    shutil.rmtree(_pwd, ignore_errors=True)
    else:
        _setup.cli(_args.data)

    sys.exit(0)

if __name__ == "__main__":
    main()
