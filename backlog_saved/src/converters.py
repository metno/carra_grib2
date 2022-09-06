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


with open(ifile) as gf, open(ofile, 'wb') as gfo:
    #nmsg = len(gf)
    out_msgs = []
    while True:
        msg = ecc.codes_grib_new_from_file(gf)
        ifmsg is None:
            break
        iop =str(ecc.codes_get(msg, "indicatorOfParameter"))
        iotol = str(ecc.codes_get(msg, "indicatorOfTypeOfLevel"))
        level = str(ecc.codes_get(msg, "level"))
        found = False
        if str(iop) in task_dict:
            if iotol in task_dict[iop]:
                if level in task_dict[iop][iotol]:
                    print("found",iop,iotol,level)
                    this = task_dict[iop][iotol][level]
                    invalues = ma.masked_values(ecc.codes_get_values(msg),ecc_codes_get(msg, "missingValue"))
                    outvalues = this["func"](invalues,this["args"])
                    msg_out = ecc.codes_clone(msg)
                    ecc.codes_set_values(msg_out, outvalues.filled(fill_value=ecc.codes_get(msg, "missingValue"))
                    ecc.codes_write(msg_out, gfo)
                    found = True
        if not found:
            msg.write(gfo)
