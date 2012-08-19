import tempfile
import time
import random

from os.path import split

from process import Process
from chdir import ChdirStack
from exit import err_exit


class SCP(object):
    """Secure copy and FTP abstraction."""

    def __init__(self, process=None):
        self.process = process or Process()

    def delay(self):
        time.sleep(random.choice([0.2, 0.3, 0.4]))

    def run_scp(self, distfile, location):
        if not self.process.quiet:
            print 'running scp_upload'
            self.delay()
            dir, basename = split(distfile)
            print 'Uploading dist/%(basename)s to %(location)s' % locals()

        rc, lines = self.process.popen(
            'scp "%(distfile)s" "%(location)s"' % locals(),
            echo=False)
        if rc == 0:
            if not self.process.quiet:
                print 'OK'
            return rc
        err_exit('ERROR: scp failed')

    def run_sftp(self, distfile, location):
        if not self.process.quiet:
            print 'running sftp_upload'
            self.delay()
            dir, basename = split(distfile)
            print 'Uploading dist/%(basename)s to %(location)s' % locals()

        with tempfile.NamedTemporaryFile(prefix='sftp-') as file:
            file.write('put "%(distfile)s"\n' % locals())
            file.write('bye\n')
            file.flush()
            cmdfile = file.name
            rc, lines = self.process.popen(
                'sftp -b "%(cmdfile)s" "%(location)s"' % locals(),
                echo=False)
            if rc == 0:
                if not self.process.quiet:
                    print 'OK'
                return rc
            err_exit('ERROR: sftp failed')

