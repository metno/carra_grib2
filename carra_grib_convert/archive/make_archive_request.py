#TODO write archive.batch file

class Request(object):

    def __init__(self,Source,Date,Hour,Origin,Type,Step,Levelist,Param,Levtype,Expver="prod",Class="RR",Stream="oper"):
        self.source = Source
        self.date = Date
        self.hour = Hour
        self.origin = Origin
        self.type = Type
        self.step = Step if type(Step) == list else [int(Step)]
        self.param = Param if type(Param) == list else [int(Param)]
        self.levelist = Levelist if type(Levelist) == list else [int(Levelist)]
        self.levtype = Levtype
        self.expver = Expver
        self.marsClass = Class
        self.stream = Stream
        self.expect = len(self.step)*len(self.param)*len(self.levelist)

    def write_request(self,f):
        separator = '/'
        f.write('archive,source=%s' % self.source)
        f.write(_line('DATE', self.date))
        f.write('    TIME       = %s,' % self.hour)
        f.write('    ORIGIN     = %s,' % self.origin)
        f.write('    STEP       = %s,' % separator.join(str(x) for x in self.step))
        f.write('    LEVELIST   = %s,' % separator.join(str(x) for x in self.levelist))
        f.write('    PARAM      = %s,' % separator.join(str(x) for x in self.param))
        f.write('    EXPVER     = %s,' % self.expver)
        f.write('    CLASS      = %s,' % self.marsClass)
        f.write('    LEVTYPE    = %s,' % self.levtype)
        f.write('    TYPE       = %s,' % self.type)
        f.write('    STREAM     = %s,' % self.stream)
        f.write('    EXPECT     = %s,' % self.expect)

def _line(key,val):
    return "    %11s= %s," % (key,val)

#whith open("archive.batch",'w') as f:


