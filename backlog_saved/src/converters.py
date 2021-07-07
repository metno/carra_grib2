import eccodes as ecc
import numpy as np
import numpy.ma as ma
import sys


# converter functions #

     

print("Apply converter on %s" % sys.argv[1])

ifile = sys.argv[1].rstrip()
ofile = sys.argv[2].rstrip()

#            param leveltype level function
task_dict = {"71":{"ml":{"65":{"func":ma.multiply,"args":100}}},
             "239":{"sfc":{"0":{"func":ma.divide,"args":9.81}}},
             "190":{"sfc":{"800":{"func":ma.multiply,"args":100}}}
             }


with ecc.GribFile(ifile) as gf,open(ofile,'wb') as gfo:
    nmsg = len(gf)
    for i in range(nmsg):
        msg = ecc.GribMessage(gf)
        iop =str(msg["indicatorOfParameter"])
        iotol = str(msg["indicatorOfTypeOfLevel"])
        level = str(msg["level"])
        found = False
        if str(iop) in task_dict:
            if iotol in task_dict[iop]:
                if level in task_dict[iop][iotol]:
                    print("found",iop,iotol,level)
                    this = task_dict[iop][iotol][level]
                    invalues = ma.masked_values(msg["values"],msg["missingValue"])
                    outvalues = this["func"](invalues,this["args"])
                    msg_out = ecc.GribMessage(clone=msg)
                    msg_out["values"] = outvalues.filled(fill_value=msg["missingValue"])
                    msg_out.write(gfo)
                    found = True
        if not found:
            msg.write(gfo)
