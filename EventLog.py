import os
import sys

# the log need to write as csv should be special case
# the log for data transfer ...
# Can it multi-thread?
LOG_LEVEL = {'debug':0,
             'system':1,
             'info':2,
             'msg':3}

LOG_SET = {'LogIter':None,
           'source':'System',
           'LogLevel':'info',
           'LogMsg':None}

LOG_FORMAT = '[{source} : {LogIter}]: {LogMsg}'

DEF_LEVEL = 'system'

class Logger() :
    def __init__ (self,log_name,Log_format=LOG_FORMAT) :
        self.var_iter = 0
        self.log_format = Log_format
        self.source_lst = {'sys':'System',
                           'err':log_name}
        self.log_set = {'LogIter':self.cal_iter,
                        'source':log_name,
                        'LogLevel':'system',
                        'LogMsg':''}
        self.registerSource(log_name,'main')
        self.logErr = self('err',lambda : 'Error')
        self.logger = self()
        self.log_info = self(level='info')
        self.log_msg = self(level='msg')
        self.log_system = self(level='system')
        self.log_debug = self(level='debug')

    def pause(self) :
        input('Enter Any Key to continue')

    def stepByStep(self,t=1) :
        import time
        time.sleep(t)

    def showLevel(self) :
        print(self.log_set['LogLevel'])

    def registerSource(self,soucre_name,short) :
        if not soucre_name in self.source_lst :
            self.source_lst[short]=soucre_name
        return self.log_engine(soucre_name)

    def showReg(self) :
        for n in self.source_lst :
            print('{} : {}'.format(n,self.source_lst[n]))

    def displayLevel(self,level='system') :
        if level in LOG_LEVEL or level in LOG_LEVEL.values() or level == None:
            self.log_set['LogLevel'] = level
            return self.log_set['LogLevel']
        else :
            self.logErr('The level is not exists')
            return None

    def cal_iter(self):
        self.var_iter += 1
        return self.var_iter

    def log_engine(self,source,external_iter=False,csv_mode=False,def_level = DEF_LEVEL):
        if not source in self.source_lst :
            return None
        if external_iter :
            iter_gen = external_iter
        else :
            iter_gen = self.log_set['LogIter']
        def log_text_eg(msg):
            set_log = {'LogIter':iter_gen(),
                       'source':self.source_lst[source],
                       'LogMsg':msg}
            t = self.log_format.format(**set_log)
            thead_len = len(t) - len(msg)
            space = ' '*thead_len
            smsg = msg.split('\n')
            mmsg = ('\n'+space).join(smsg)
            set_log['LogMsg'] = mmsg
            return self.log_format.format(**set_log)
        return log_text_eg

    def __level(self) :
        return self.log_set['LogLevel']

    def __translateLevel(self,level) :
        if not level in LOG_LEVEL and not level in LOG_LEVEL.values() :
            return None
        else :
            if type(level) == int :
                pass
            else :
                level = LOG_LEVEL[level]
            return level

    def stdLog(self,logeg,level=DEF_LEVEL) :
        def std_logger(msg,level=level) :
            l = self.__translateLevel(level)
            ll = self.log_set['LogLevel']
            if self.__level() == None :
                return None
            if type(ll) == int :
                pass
            else :
                ll = LOG_LEVEL[ll]
            if l >= ll :
                t = logeg(msg)
                print(t)
                return t
            else:
                return None
        return std_logger

    def __call__(self,source='main',external_iter=False,level=DEF_LEVEL) :
        return self.stdLog(self.log_engine(source,external_iter),level)

setGLog = Logger('Global')
GregLogger = lambda x : setGLog.registerSource(x,x)
Glogger = lambda x : setGLog(x)
Glog_info = lambda x : setGLog(x,level='info')
Glog_msg = lambda x : setGLog(x,level='msg')
Glog_debug = lambda x : setGLog(x,level='debug')
Glog_sys = lambda x : setGLog(x,level='system')
Glogerr = lambda x : setGLog(x,lambda : 'Error')

if __name__ == '__main__' :
    a = Logger('ABC LOG')
    syslog = a('sys')
    a.displayLevel(1)
    syslog('TEST3')
    a.displayLevel(3) # the defualt for a logger do not update belong displayLevel setting
    syslog('TEST4')
    a.displayLevel(100)
    syslog('TEST1',1)
    a.displayLevel('msg')
    syslog('2','info')
