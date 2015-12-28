import inspect
def lineid():
    return inspect.currentframe().f_back.f_lineno
class throttler():
    def __init__(self,func,cap,active=True):
        self.func = func
        self.cap = cap
        self.times = {}
        self.active = active
    def __call__(self,oid,arg):
        self.times.setdefault(oid,0)
        result = self.func(arg)
        if self.active==True:
            if self.times[oid] < self.cap:
               input("\U0001f604 "*3)
            self.times[oid] = self.times[oid] + 1
        return result

