import unittest
import os

from os.path import join, isdir

from jarn.mkrelease.scm import Subversion

from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import TestProcess
from jarn.mkrelease.testing import quiet


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('svn://'), True)

    def testSvnSshUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('svn+ssh://'), True)

    def testHttpUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('http://'), True)

    def testHttpsUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('https://'), True)

    def testFileUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('file://'), True)

    def testBadProtocol(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('git://'), False)

    def testEmptyString(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url(''), False)


class ValidSandboxTests(SubversionSetup):

    def testSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox(self.clonedir), True)

    def testNotExists(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox('foo'), False)

    def testNotADir(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox(join(self.clonedir, 'setup.py')), False)

    def testNotACheckout(self):
        scm = Subversion()
        self.destroy(self.clonedir)
        self.assertEqual(scm.is_valid_sandbox(self.clonedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        self.assertRaises(SystemExit, scm.check_valid_sandbox, 'foo')
        self.assertRaises(SystemExit, scm.check_valid_sandbox, join(self.clonedir, 'setup.py'))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.check_valid_sandbox, self.clonedir)


class UrlFromSandboxTests(SubversionSetup):

    def testGetUrl(self):
        scm = Subversion()
        self.assertEqual(scm.get_url_from_sandbox(self.clonedir),
            'file://%s/trunk' % self.packagedir)

    def testGetAnotherUrl(self):
        scm = Subversion()
        self.assertEqual(scm.get_url_from_sandbox(join(self.clonedir, 'testpackage')),
            'file://%s/trunk/testpackage' % self.packagedir)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=1))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.clonedir)

    @quiet
    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.clonedir)


class RemoteSandboxTests(SubversionSetup):

    def testIsRemoteSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_remote_sandbox(self.clonedir), True)

    def testBadSandbox(self):
        scm = Subversion()
        self.destroy(self.clonedir)
        # Note: Always true
        self.assertEqual(scm.is_remote_sandbox(self.clonedir), True)

    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        # Note: Always true
        self.assertEqual(scm.is_remote_sandbox(self.clonedir), True)


class DirtySandboxTests(SubversionSetup):

    def testCleanSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    def testModifiedFile(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), True)

    def testRemovedFile(self):
        scm = Subversion()
        self.remove(self.clonedir)
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), True)

    def testDeletedButTrackedFile(self):
        scm = Subversion()
        self.delete(self.clonedir)
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertRaises(SystemExit, scm.check_dirty_sandbox, self.clonedir)


class UncleanSandboxTests(DirtySandboxTests):

    def testCleanSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), False)

    def testModifiedFile(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testRemovedFile(self):
        scm = Subversion()
        self.remove(self.clonedir)
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testDeletedButTrackedFile(self):
        scm = Subversion()
        self.delete(self.clonedir)
        # Note: The sandbox is reported as *unclean*
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), False)

    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertRaises(SystemExit, scm.check_unclean_sandbox, self.clonedir)


class UpdateSandboxTests(SubversionSetup):

    def testUpdateSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.update_sandbox(self.clonedir), 0)

    def testUpdateModifiedSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir) # FIXME
        self.assertEqual(scm.update_sandbox(self.clonedir), 0)

    # TODO: Test more funky changes, conflicts, etc.

    @quiet
    def testBadUpdate(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.update_sandbox, self.clonedir)

    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        # Note: The sandbox is reported as up-to-date
        self.assertEqual(scm.update_sandbox(self.clonedir), 0)

    @quiet
    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        self.assertRaises(SystemExit, scm.update_sandbox, self.clonedir)


class CheckinSandboxTests(SubversionSetup):

    def testCheckinCleanSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.checkin_sandbox(self.clonedir, 'testpackage', '2.6', False), 0)

    def testCheckinDirtySandbox(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir)
        self.assertEqual(scm.checkin_sandbox(self.clonedir, 'testpackage', '2.6', False), 0)

    def testCheckinAndPushCleanSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.checkin_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)

    def testCheckinAndPushDirtySandbox(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir)
        self.assertEqual(scm.checkin_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)
        self.verify(self.clonedir)

    @quiet
    def testBadPush(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir)
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.checkin_sandbox, self.clonedir, 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.checkin_sandbox, self.clonedir, 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        self.assertRaises(SystemExit, scm.checkin_sandbox, self.clonedir, 'testpackage', '2.6', False)


class CheckoutUrlTests(SubversionSetup):

    def testCheckoutUrl(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.checkout_url('file://'+self.packagedir, 'testclone2'), 0)
        self.assertEqual(isdir('testclone2'), True)

    @quiet
    def testBadServer(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.checkout_url, 'file://'+self.packagedir, 'testclone2')

    @quiet
    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        self.assertRaises(SystemExit, scm.checkout_url, 'file://'+self.packagedir, 'testclone2')


class TagExistsTests(SubversionSetup):

    def testTagDoesNotExist(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), False)

    def testTagExists(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.tag(self.clonedir, tagid)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)

    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.destroy(self.clonedir)
        # Note: The tag is reported as not existing
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), False)

    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        # Note: The tag is reported as not existing
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), False)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.tag(self.clonedir, tagid)
        self.assertRaises(SystemExit, scm.check_tag_exists, self.clonedir, tagid)


class TagIdTests(SubversionSetup):

    def testTagIdFromTrunk(self):
        scm = Subversion()
        self.assertEqual(scm.get_tag_id(self.clonedir, '2.6'), 'file://%s/tags/2.6' % self.packagedir)

    def testTagIdFromBranch(self):
        scm = Subversion(TestProcess(rc=0, lines=['', 'URL: file://testpackage/branches/2.x']))
        self.assertEqual(scm.get_tag_id(self.clonedir, '2.6'), 'file://testpackage/tags/2.6')

    def testTagIdFromTag(self):
        scm = Subversion(TestProcess(rc=0, lines=['', 'URL: file://testpackage/tags/2.6b2']))
        self.assertEqual(scm.get_tag_id(self.clonedir, '2.6'), 'file://testpackage/tags/2.6')

    @quiet
    def testTagIdFromBadUrl(self):
        scm = Subversion(TestProcess(rc=0, lines=['', 'URL: file://testpackage']))
        self.assertRaises(SystemExit, scm.get_tag_id, self.clonedir, '2.6')


class CreateTagTests(SubversionSetup):

    def testCreateTag(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), False)
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', False), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)

    @quiet
    def testCreateExistingTag(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', False), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)
        # Note: This works! Subversion just copies stuff into a subdirectory...
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', False), 0)
        # Note: Only on the third attempt tagging fails
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', False)

    def testCreateAndPushTag(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', True), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)
        #self.assertEqual(scm.tag_exists(self.packagedir, tagid), True)

    @quiet
    def testBadPush(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Subversion(TestProcess(rc=1))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', False)
