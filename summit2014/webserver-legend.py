from sys import argv, stdout, stderr, exit
import lmidemo.util.democolor as democolor

print democolor.hilite("Explanation of what we will do in the next step",
                       democolor.XTERM_BLUE)
print democolor.hilite("The LMIShell command being invoked",
                       democolor.XTERM_MAGENTA)
print "Feedback from the command"
print democolor.hilite("Results of the operation",
                       democolor.XTERM_GREEN)
