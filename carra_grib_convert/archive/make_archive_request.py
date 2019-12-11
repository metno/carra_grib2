import eccodes as ecc


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
#        self.source = "%s.%s.%s.%s.grib2" % (self.type.lower(),self.date,self.hour+"00",self.levtype.lower())

    def write_request(self,f):
        separator = '/'
        f.write('%s,source=%s,database=%s,\n' % (self.action,self.source,self.database))
        f.write(_line('DATE',self.date))
        f.write(_line('TIME',self.hour))
        f.write(_line('ORIGIN',self.origin.upper()))
        f.write(_line('STEP',separator.join(str(x) for x in self.step)))
        # hack for sfc
        if self.levtype.lower() == "sfc".lower():
            self.expect = len(self.step)*len(self.param)
        else:
            f.write(_line('LEVELIST',separator.join(str(x) for x in self.levelist)))
        f.write(_line('PARAM',separator.join(str(x) for x in self.param)))
        f.write(_line('EXPVER',self.expver.lower()))
        f.write(_line('CLASS ',self.marsClass.upper()))
        f.write(_line('LEVTYPE',self.levtype.upper()))
        f.write(_line('TYPE',self.type.upper()))
        f.write(_line('STREAM',self.stream.upper()))
        f.write(_line('EXPECT',self.expect,eol=""))


class RequestFromGrib(Request):

    def __init__(self,gribfile,Action):
        super().__init__()
        self.source = gribfile
        self.action = Action
        self.parse_grib_file()
        self.expect = len(self.step)*len(self.param)*len(self.levelist)

    def parse_grib_file(self):
        gribfile = self.source
        self.type,self.date,self.hour,self.levtype,grib2 = gribfile.split('.')

        params = []
        levels = []
        steps = []
        with ecc.GribFile(gribfile) as gf:
            for i in range(len(gf)):
                msg = ecc.GribMessage(gf)
                params.append(msg['param'])
                levels.append(msg['level'])
                steps.append(msg['step'])
                if i == 1:
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



def _line(key,val,eol=','):
    return "    %s= %s%s\n" % (key.ljust(11),val,eol)










if __name__ == "__main__":

    import sys

    gribfile = sys.argv[1]

#    gribfile = "an.20170109.0300.hl.grib2"

    with sys.stdout as rf:
        req = RequestFromGrib(gribfile,"archive")
        req.write_request(rf)

"""
    # Height Levels
    levelist = [15,30,50,75,100,150,200,250,300,400,500]
    param = [130,54,3031,10,157,246,247]
    levtype = "hl"

    print(len(levelist)*len(param))

    # Pressure Levels
    levelist = [10,20,30,50,70,100,150,200,250,300,400,500,600,700,750,800,825,850,875,900,925,950,1000]
    param = [131,132,130,76,75,260028,129,3014,260238,60,157,260257,246,247]
    levtype = "pl"

    # Model Levels
    levelist = [i+1 for i in range(65)]
    param = [133,130,131,132,75,76,260028,260155,260257,246,247]
    levtype = "ml"

    # Surface Level
    param = [235,167,165,166,151,260057,134,3020,260260,207,260107,260108,228002,173,172,228164,3075,3074,3073,260242,228141,260509,31,34,260430,174008]
    levtype = "sfc"

    # Soil Levels
    param = [260199]
    levelist = [1,2]
    levtype = "sol"

    #whith open("archive.batch",'w') as f:
"""
exit()
