import os
import eccodes as ecc
import argparse
import sys

class Request(object):

    def __init__(self,Action=None,Source=None,Date=None,Hour=None,Origin=None,Type=None,Step=None,Levelist=None,Param=None,Levtype=None,
                 Database="marsscratch",Expver="prod",Class="RR",Stream="oper"):
        """ Construct a request for mars"""
        self.action = Action
        self.source = Source
        self.database = Database
        self.date = Date
        self.hour = Hour
        self.origin = Origin
        self.type = Type
        self.step = Step if type(Step) == list else [Step]
        self.param = Param if type(Param) == list else [Param]
        self.levelist = Levelist if type(Levelist) == list else [Levelist]
        self.levtype = Levtype
        self.expver = Expver
        self.marsClass = Class
        self.stream = Stream
        self.expect = len(self.step)*len(self.param)*len(self.levelist)

    def write_request(self,f):
        separator = '/'
        if self.database:
            f.write('%s,source=%s,database=%s,\n' % (self.action,self.source,self.database))
        else:
            f.write('%s,source=%s,\n' % (self.action,self.source))
        f.write(_line('DATE',self.date))
        f.write(_line('TIME',self.hour))
        f.write(_line('ORIGIN',self.origin.upper()))
        f.write(_line('STEP',separator.join(str(x) for x in self.step)))
        if self.levtype.lower() != "sfc".lower():
            f.write(_line('LEVELIST',separator.join(str(x) for x in self.levelist)))
        f.write(_line('PARAM',separator.join(str(x) for x in self.param)))
        f.write(_line('EXPVER',self.expver.lower()))
        f.write(_line('CLASS ',self.marsClass.upper()))
        f.write(_line('LEVTYPE',self.levtype.upper()))
        f.write(_line('TYPE',self.type.upper()))
        f.write(_line('STREAM',self.stream.upper()))
        f.write(_line('EXPECT',self.expect,eol=""))


class RequestFromGrib(Request):

    def __init__(self,gribfile,Action,Database='marsscratch'):
        super().__init__(Database=Database)
        self.source = gribfile
        self.action = Action
        self.parse_grib_file()

    def parse_grib_file(self):
        gribfile = self.source
        self.type,dummy1,self.date,self.hour,dummy2,grib2 = os.path.basename(gribfile).split('.')

        params = []
        levels = []
        steps = []
        with ecc.GribFile(gribfile) as gf:
            nfields = len(gf)
            for i in range(len(gf)):
                msg = ecc.GribMessage(gf)
                params.append(msg['param'])
                levels.append(msg['level'])
                steps.append(msg['step'])
                if i == 1:
                    self.date = str(msg["dataDate"])
                    self.hour = "%04d" % int(msg["dataTime"])

                    if str(msg['suiteName']) == '1':
                        self.origin = "no-ar-ce"
                    elif str(msg['suiteName']) == '2':
                        self.origin = "no-ar-cw"
                    elif str(msg['suiteName']) == '3':
                        self.origin = "no-ar-pa"
                    else:
                        print("unknown origin/suiteName")
                        exit(1)

        param = list(set(params))
        param.sort()
        self.param = param
        levelist = list(set(levels))
        levelist.sort()
        levelist.reverse()
        self.levelist = levelist
        step = list(set(steps))
        step.sort()
        self.step = step
        self.expect = nfields


def _line(key,val,eol=','):
    return "    %s= %s%s\n" % (key.ljust(11),val,eol)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='dump mars request from input gribfile')
    parser.add_argument('filename',type=str,help='grib file name')
    parser.add_argument('--database',type=str,default='marsscratch',help='mars database')

    args = parser.parse_args()

    gribfile = args.filename
 
    if args.database == "mars":
        database = None
    else:
        database = args.database

    with sys.stdout as rf:
        req = RequestFromGrib(gribfile,"archive",database)
        req.write_request(rf)

exit()
