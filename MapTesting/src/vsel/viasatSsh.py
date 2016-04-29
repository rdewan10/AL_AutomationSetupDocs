#!/usr/bin/env python

import pexpect


# Value added SSH objects for ssh & scp
class viasatSsh():

        def __init__(self, host, usern, passw, log=None):
            self.host = host
            self.usern = usern
            self.passw = passw
            self.log = log

        def getFile(self, srcfn, dstfn):
            cmd="scp {}@{}:{} {}".format(self.usern, self.host, srcfn, dstfn)
            child = pexpect.spawn(cmd)
            try:
                child.expect('continue connecting (yes/no)?', timeout=5)
                child.sendline('yes')
            except pexpect.TIMEOUT:
                pass;
            except pexpect.EOF:
                pass;

            child.expect('assword:')
            child.sendline(self.passw)

            try:
                child.expect(pexpect.EOF, timeout=180)
            except pexpect.EOF:
                pass;

    #########################################################################
    #  MAIN Launch the poller and run until a stop signal (SIGUSR1) is received
    #########################################################################
if __name__ == '__main__':

        #vsshTerm = viasatSsh("192.168.100.1", "root", "TCD:Doesn\'tCare1Bit")
        #vsshTerm.getFile("/test/syslogMsgs", "./results/termSyslog.log")
        vsshRtnms = viasatSsh("192.168.144.8", "root", "viasat")
        vsshRtnms.getFile("/usr/local/rtnms/log/rtnms.log", "./results/rtnmsSyslog.log")
