
from mapbunMain import mapbun
from nlgMain import nlg
import sys, subprocess

class alam(object):

    def __init__(self, groupId, lock=False):
        self.groupId = groupId
        if (lock):
            self.map = mapbun(groupId)
            self.map.mapbunConf(lock=True)

    ############################################################################
    # Starts the test corresponding to testType by calling the appropriate
    # methods in mapbunMain.py
    ############################################################################
    def alamTestStart(self, testId, trickle=False, upload=False, fllock=False, precedence=False,nlgstart=False, nlgtermstart=False, nlgstop=False, logout=False, relogin=False, reboot=False):

        # Handle mapbundle tests
        if (upload or trickle or fllock or precedence):

            self.map = mapbun(self.groupId)
            self.map.mapbunConf()
            sys.stdout.flush()

            self.map.conf.updateGroupConfig(self.groupId, dict(Status='running'))

            if (upload):
                print('Starting mapbun Upload Test\n')
                sys.stdout.flush()
                print(self.map.mapbunUpload(testId, True))

            if (trickle):
                print('Starting mapbun Trickle Test\n')
                sys.stdout.flush()
                print(self.map.mapbunTrickle(testId))

            if (fllock):
                print('Starting mapbun FLLock Test\n')
                sys.stdout.flush()
                print(self.map.mapbunFLLock(testId))

            if (precedence):
                print('Starting mapbun Precedence Test\n')
                sys.stdout.flush()
                print(self.map.mapbunPrecedence(testId))

            self.map.conf.updateGroupConfig(self.groupId, dict(Status='complete'))

        # Handle NLG tests
        if (nlgstart or nlgtermstart or nlgstop or logout or relogin or reboot):
            self.nlg = nlg(self.groupId)
            sys.stdout.flush()

            if (nlgstart or nlgtermstart):
                self.nlg.conf.updateGroupConfig(self.groupId, dict(Status='running'))
                cmd = ['./nlgMain.py {} {}'.format(self.groupId, nlgtermstart)]
                subprocess.Popen(cmd, shell=True)

            if (nlgstop):
                self.nlg.nlgStopPoll()

            if (logout):
                print('Starting nlg Logout Test\n')
                self.nlg.nlgNmsVmtCommand("logout")

            if (relogin):
                print('Starting nlg Relogin Test\n')
                self.nlg.nlgNmsVmtCommand("relogin")

            if (reboot):
                print('Starting nlg Reboot Test\n')
                self.nlg.nlgNmsVmtCommand("reboot")

        sys.stdout.flush()
