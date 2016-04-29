from termLinkSSH import *

log = open('rebootLog', 'a+')


tl = termLinkSSH('192.168.94.1', 'root', 'saf&scur/4OH1', log)
termCmd = TermCmd(tl)
termCmd.reboot()
termCmd.login()
termCmd.termcfgStatus()
tl.close()
