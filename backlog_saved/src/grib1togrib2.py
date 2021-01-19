#!/usr/local/apps/python3/3.6.10-01/bin/python3

import sys


print("REPORTING FROM PYTHON")

out = " ".join(sys.argv)

with open("process.txt",'w') as f:
    f.write(out)

