import os
import sys
import threading
import EventLog
import copy
import time

# allow to get logger object ?
# why the msg of threading is not static
# should used different log instance but manage together

#EventLog.setGLog.displayLevel(0)
#EventLog.DEF_LEVEL = 'debug'
TIME = 'SysTime'

class Event():
    def __init__(self,event_name,event_func,*argv) :
        EventLog.GregLogger(event_name)
        self.logger = EventLog.Glogger(event_name)
        self.logerr = EventLog.Glogerr(event_name)
        self.log_info = EventLog.Glog_info(event_name)
        self.log_msg = EventLog.Glog_msg(event_name)
        self.log_system = EventLog.Glog_sys(event_name)
        self.log_debug = EventLog.Glog_debug(event_name)
        self.__event_name = event_name
        self.__event_func = event_func
        self.__event_stack = None
        self.argv = argv
        self.var_iter = None
        self.__time_cost = 0
        self.__during_time = 0
        self.__return = None
        self.log_debug('Event Creating > {} | {}'.format(event_name,[str(a) for a in argv]))

    def set_logger(self,Logger_setter) :
        Logger_setter.registerSource(self.__event_name,self.__event_name)
        self.logErr = Logger_setter('err',lambda : 'Error')
        self.logger = Logger_setter(self.__event_name)
        self.log_info = Logger_setter(self.__event_name,level='info')
        self.log_msg = Logger_setter(self.__event_name,level='msg')
        self.log_system = Logger_setter(self.__event_name,level='system')
        self.log_debug = Logger_setter(self.__event_name,level='debug')

    def detail(self,time_cost=False) :
        if time_cost :
            self.__time_cost = time_cost

    def reset(self) :
        self.__event_stack = None
        self.var_iter = None
        return self

    def execute(self,var_iter=None,start=0,test=False) :
        self.var_iter = var_iter
        if not test :
            self.log_debug('Event <{}> is executing'.format(self.name()))
            r,next_event = self()
            self.log_debug('Event <{}> is completed'.format(self.name()))
        else:
            self.log_info('Test in Event <{}>'.format(self.name()))
            next_event = self.__event_stack
        time_during = start+self.__time_cost
        self.__during_time = time_during
        arg_lst = [str(a) for a in self.argv]
        if not test :
            if next_event :
                return [[r,time_during]]+next_event.execute(var_iter=r,start=time_during,test=test)
            else :
                return [[r,time_during]]
        else :
            if next_event :
                self.log_info('<{}> | {}    {} -> {}'.format(self.__event_name,arg_lst,start,time_during))
                return [time_during]+next_event.execute(start=time_during,test=test)
            else :
                self.log_info('<{}> | {}    {} -> {}'.format(self.__event_name,arg_lst,start,time_during))
                return [time_during]

    def call(self) :
        return self.argv

    def final(self) :
        return False

    def name(self) :
        return '{}'.format(self.__event_name)

    def is_single(self) :
        if self.__event_stack :
            return False
        else :
            return True

    def top(self) :
        if self.__event_stack :
            return self.__event_stack.top()
        else :
            return self

    def next_event(self):
        return self.__event_stack

    def __str__ (self):
        print_argv = len(self.argv)
        return '<\'{}\': {} args>'.format(self.__event_name,print_argv)

    def __call__(self,callback=None) :
        if callback :
            #if type(callback) == type(self) :
            if not callback == self :
                callback.top().__event_stack = self
                return callback
            else :
                return None
            #self.__event_stack = callback
            #return self.__event_stack
        else :
            using_argv = self.call()
            result = self.__event_func(*using_argv)
            self.__return = result
            if not self.final() :
                return result,self.__event_stack
            else :
                return result,None

# should establish decode and set_decoder function
class Resource():
    def __init__ (self,res_name,res_data) :
        EventLog.GregLogger(res_name)
        self.logger = EventLog.Glogger(res_name)
        self.logerr = EventLog.Glogerr(res_name)
        self.log_info = EventLog.Glog_info(res_name)
        self.log_msg = EventLog.Glog_msg(res_name)
        self.log_system = EventLog.Glog_sys(res_name)
        self.log_debug = EventLog.Glog_debug(res_name)
        self.__res_name = res_name
        self.__res_data = res_data
        self.__res_using = False
        self.__decoder = lambda x : [x]
        self.log_debug('Resource Creating > {} | {}'.format(self.__res_name,type(self.__res_data)))

    def decode(self):
        return self.__decoder(self.__res_data)

    def set_decoder(self,decode_func=lambda x : [x]):
        self.__decoder = decode_func

    def set_logger(self,Logger_setter) :
        Logger_setter.registerSource(self.__res_name,self.__res_name)
        self.logErr = Logger_setter('err',lambda : 'Error')
        self.logger = Logger_setter(self.__res_name)
        self.log_info = Logger_setter(self.__res_name,level='info')
        self.log_msg = Logger_setter(self.__res_name,level='msg')
        self.log_system = Logger_setter(self.__res_name,level='system')
        self.log_debug = Logger_setter(self.__res_name,level='debug')

    def __checkOwner(self,caller) :
        if self.__res_using and self.__res_using==caller :
            return True
        else :
            return False

    def __lock(self,caller) :
        if not self.__res_using :
            self.log_debug('Lock the resource {} by {}'.format(self,caller))
            self.__res_using = caller
            return caller
        else :
            return False

    def __unlock(self,caller) :
        if self.__checkOwner(caller) :
            self.log_debug('Release the resource {} from {}'.format(self,caller))
            self.__res_using = False
            return True
        else :
            return False

    def handler(self,caller) :
        def get_set(get=True,value=None):
            if get :
                return self.get(caller)
            elif value :
                return self.set(caller,value)
            else :
                return False
        return get_set


    def get(self,caller=None):
        if self.__checkOwner(caller):
            self.log_debug('<{}> get the data'.format(caller))
            return self.__res_data
        else :
            if caller == None :
                self.log_debug('Data is fetched')
                return self.__res_data
            else :
                self.log_debug('{} is trying to get data'.format(caller))
                return None

    def set(self,caller,data,force=False) :
        if self.__checkOwner(caller):
            if force :
                pass
            else :
                if type(self.__res_data) == type(data) :
                    pass
                else :
                    self.logerr('Not Correct Type')
                    return False
            self.log_debug('set data to -> {}'.format(data))
            self.__res_data = data
            return type(self.__res_data)
        else :
            return False

    def using(self) :
        return self.__res_using

    def set_unsafe(self,data,type_check=True) :
        if type_check :
            assert type(self.__res_data) == type(data), f'Original Type is `{type(self.__res_data)}`, and new data type is {type(data)}'
        self.log_debug('set data to -> {}'.format(data))
        self.__res_data = data
        return self

    def name(self) :
        return '{}'.format(self.__res_name)

    def __str__ (self):
        return '<\'{}\': {} >'.format(self.__res_name,type(self.__res_data))

    def __call__ (self,caller=None,relax=False) :
        if caller :
            if not relax :
                return self.__lock(caller)
            else :
                return self.__unlock(caller)
        return [self.__res_name,str(self.__res_using)]


class EventChainFramework() :
    # frame work element
    class ResEvent(Event) :
        def call(self) :
            for r in self.argv :
                assert r(self) , 'Resource {} is used'.format(r)
            return [r.handler(self) for r in self.argv]
        def final(self) :
            for r in self.argv :
                assert r(self,relax=True), 'Resource {} can not relax'.format(r)
            return False
        def get_next_event(self):
            return self.next_event()
        def get_res_name(self) :
            return [r.name() for r in self.argv]

    class EventBlock() :
        def __init__ (self,process_name,event_chain,latency=None,periodic=lambda *x: True) :
            EventLog.GregLogger(process_name)
            self.logger = EventLog.Glogger(process_name)
            self.logerr = EventLog.Glogerr(process_name)
            self.log_info = EventLog.Glog_info(process_name)
            self.log_msg = EventLog.Glog_msg(process_name)
            self.log_system = EventLog.Glog_sys(process_name)
            self.log_debug = EventLog.Glog_debug(process_name)
            self.__event_block_name = process_name
            self.__porcess_events = event_chain
            self.__res_using = {}
            self.__res_counter = 0
            self.__time_using = 0
            self.__compile_flag = False
            self.__periodic_func = periodic
            self.__latency = latency
            self.__descri = ''
            self.__run_flag = False
            self.__prcTime = None
            self.compile()

        def showExecTime(self) :
            print(f'Event <{self.__event_block_name}> : ',end='')
            if self.__prcTime :
                print('processing time =',self.__prcTime)
            else :
                print('have not been processed')

        def inject(self,eventBlock) :
            self.append_event(eventBlock.extract())
            return self

        def extract(self,index=None) :
            return self.__porcess_events

        def set_logger(self,Logger_setter) :
            Logger_setter.registerSource(self.__event_block_name,self.__event_block_name)
            self.logErr = Logger_setter('err',lambda : 'Error')
            self.logger = Logger_setter(self.__event_block_name)
            self.log_info = Logger_setter(self.__event_block_name,level='info')
            self.log_msg = Logger_setter(self.__event_block_name,level='msg')
            self.log_system = Logger_setter(self.__event_block_name,level='system')
            self.log_debug = Logger_setter(self.__event_block_name,level='debug')

        def description(self,text=None) :
            if text :
                self.__descri = text
            else :
                pass
            return '{}'.format(self.__descri)


        def reset(self) :
            self.__res_using = {r:False for r in self.__res_using}
            self.__res_counter = len(self.__res_using)
            self.__run_flag = False
            return self

        def is_run(self) :
            return self.__run_flag

        def recompile(self) :
            self.__res_using = {}
            self.__res_counter = 0
            self.__compile_flag = False
            self.compile()
            return self

        def __append_res(self,res_lst) :
            for r in res_lst :
                if r in self.__res_using :
                    pass
                else :
                    self.__res_using[r] = False
                    self.__res_counter += 1

        def name(self) :
            return '{}'.format(self.__event_block_name)

        def periodic(self,*args) :
            if self.__periodic_func == None :
                return False
            else :
                return self.__periodic_func(*args)

        def set_detail(self,latency=None,periodic=None) :
            if latency :
                self.__latency = latency
            if periodic :
                self.__periodic_func = periodic
            return self

        def is_late(self,t) :
            if not self.__latency :
                return False
            else :
                return t > self.__latency

        def append_event(self, event, cmp=True) :
            self.__compile_flag = False
            self.__run_flag = False
            self.__porcess_events = event(self.__porcess_events)
            self.log_debug('Append <{}> into <{}> '.format(event.name(),self.name()))
            if cmp :
                self.compile()

        def compile(self,start=0) :
            self.log_debug('Event Block {} is Compiling...'.format(self.name()))
            self.__run_flag = False
            current_event = self.__porcess_events
            self.__append_res(current_event.get_res_name())
            while not current_event.is_single() :
                self.log_debug('Package the event <{}>'.format(current_event))
                current_event = current_event.get_next_event()
                self.__append_res(current_event.get_res_name())
            self.log_debug('Evaluating process time...')
            r = self.__porcess_events.execute(start=start,test=True)
            self.__time_using = r.pop()
            self.__compile_flag =True
            self.log_debug('Compiled | Resource using: {}| Cost time: {}|'.format(self.show_res(),self.show_time()))
            return self

        def is_compile(self) :
            return self.__compile_flag

        def show_res(self) :
            if self.__compile_flag :
                return [r for r in self.__res_using]
            else :
                self.logerr('The event is changed, please implements compile()')
                return False

        def show_time(self) :
            if self.__compile_flag :
                return self.__time_using
            else :
                self.logerr('The event is changed, please implements compile()')
                return False

        def apply_res(self, event_block, res_index) :
            assert res_index in self.__res_using, 'Resource {} is not used in the Event Block {}'.format(res_index,self.name())
            if not self.__res_using[res_index] :
                self.__res_using[res_index] = event_block

        def trace_res(self, res_index) :
            assert res_index in self.__res_using, 'Resource {} is not used in the Event Block {}'.format(res_index,self.name())
            return self.__res_using[res_index]

        def pass_res(self, res, pass_and_run=False) :
            assert not res.using(), 'Resource {} is used by other event'.format(res.name())
            self.log_debug('Event <{}> Obtain the resource {}'.format(self.name(),res))
            self.__res_counter -= 1
            return self.__res_counter == 0

        def __call__(self,start=0,test=False) :
            import time
            self.__prcTime = time.process_time()
            self.__porcess_events.execute(start=start)
            self.__prcTime = time.process_time() - self.__prcTime
            self.__run_flag = True
            return [[self.__res_using[r],r] for r in self.__res_using if self.__res_using[r]]

        def __str__ (self) :
            return '{} | Resource using: {}| Cost time: {}|'.format(self.name(),self.show_res(),self.show_time())

    # Framework
    def __init__ (self,name) :
        self.log_setter = EventLog.Logger(name)
        self.logger = self.log_setter.logger
        self.logerr = self.log_setter.logErr
        self.log_info = self.log_setter.log_info
        self.log_msg = self.log_setter.log_msg
        self.log_system = self.log_setter.log_system
        self.log_debug = self.log_setter.log_debug
        self.event_setter = EventLog.Logger('Event')
        self.resource_setter = EventLog.Logger('Resource')
        self.block_setter = EventLog.Logger('EventBlock')
        self.__env_name = name
        self.__exec_counter = 0
        self.__show_prc_time = False
        self.__prc_interrupt = False
        self.__event_type_lst = {}
        self.__event_descri = {}
        self.__res_lst = {}
        self.__event_blocks = {}
        self.__res_link = {}
        self.__res_init = {}
        self.__sequence = []
        self.__sub_sequence = []
        self.__final_process = None
        self.__goEnd = False
        self.__instant = []
        self.__return_resource = {} # register by events return, and reset at every phase
        self.__run_flag = False
        self.__systime = self.register_res('SysTime',0)
        self.__thread_flag = False
        self.__process_time = None
        self.__res_cost_time = {n:0 for n in self.__res_lst}
        self.__phase_counter = 0
        self.__phase_run = False
        self.__logger_lst = {'resource':self.resource_setter,
                             'res':self.resource_setter,
                             'event':self.event_setter,
                             'block':self.block_setter,
                             'env':self.log_setter}
        self.log_system('Create Environment <{}>'.format(self.__env_name))
        self.set_logger('res',None)
        self.set_logger('event',None)
        self.set_logger('block',None)

    def get_res(self,res_name) :
        assert res_name in self.__res_lst, 'The resource {} is not existing'.format(res_name)
        return self.__res_lst[res_name].get()

    def set_res_unsafe(self,res_name,data) :
        assert res_name in self.__res_lst, 'The resource {} is not existing'.format(res_name)
        self.__res_lst[res_name].set_unsafe(data)
        return self

    def vars(self,*args) :
        if len(args) == 1 :
            return self.get_res(args[0])
        return [self.get_res(v) for v in args]

    # 優化dynamic event, package, create_event 的流程
    # this for auto chain event and package
    def create_block(self,block_name,event_type_name,*args) :
        return self.package(block_name,self.create_event(event_type_name,block_name,*args))

    def chain_events(self,block_name,*events) :
        eventBlock = self.package(block_name,events[0].reset())
        for event in events[1:] :
            eventBlock.append_event(event.reset(),False)
        return eventBlock.compile()

    # this is the simple interface for dynamic_event
    def trigger(self,block_name,event_type_name,*args) :
        return self.dynamic_event(self.create_block(block_name,event_type_name,*args))

    def get_logger(self,log_type) :
        return self.__logger_lst[log_type]

    def set_logger(self,log_type,displayLevel) :
        self.__logger_lst[log_type].displayLevel(displayLevel)

    def set_display(self,displayLevel) :
        self.log_setter.displayLevel(displayLevel)

    def __reset_link(self) :
        #self.__res_link = {n:False for n in self.__res_lst}
        #self.__res_init = {n:False for n in self.__res_lst}
        self.log_debug('Reset the event link at time slot {}, phase {}'.format(self.__s,self.__phase_counter))
        self.__res_link = {}
        self.__res_init = {}

    def meta(self,event_type_name,event_func,*type_info) :
        assert type_info, "Please enter the reference type of parameter\n  Using `register_event()` to ignore parameter type info"
        tp_info = ' | '.join([str(type(t)) if not type(t) == type(type(1)) else str(t) for t in type_info])
        return self.register_event(event_type_name,event_func,tp_info)

    def metaByRes(self,event_type_name,event_func,*type_info) :
        assert type_info, "Please enter the reference type of parameter\n  Using `register_event()` to ignore parameter type info"
        check = self.vars(*type_info)
        type_info = map(lambda x : f'<{x}>', type_info)
        tp_info = ' | '.join(type_info)
        return self.register_event(event_type_name,event_func,tp_info)

    def eventMeta(self,event_type_name) :
        assert event_type_name in self.__event_type_lst, "Event <{}> is not existing".format(event_type_name)
        label_space = 23
        name_format = '[{}]'.format(event_type_name)
        def format_generator() :
            prefix = ""
            if len(name_format) > (label_space-3) :
                prefix = name_format+"\n"+"".ljust(label_space)
            else :
                prefix = name_format.ljust(label_space)
            return prefix
        print(format_generator(),'<-',self.__event_descri[event_type_name])

    def resMeta(self,res_name) :
        assert res_name in self.__res_lst, "Resource <{}> is not existing".format(res_name)
        label_space = 23
        name_format = '<{}>'.format(res_name)
        def format_generator() :
            prefix = ""
            if len(name_format) > (label_space-3) :
                prefix = name_format+"\n"+"".ljust(label_space)
            else :
                prefix = name_format.ljust(label_space)
            return prefix
        print(format_generator(),'<-',self.__res_lst[res_name])

    def resType(self,res_name) :
        return type(self.vars(res_name))

    def showResType(self,res_name) :
        print(self.resType(res_name))

    def res(self,res_name, var) :
        return self.register_res(res_name,var)

    def register_event(self,event_type_name,event_func,descri=None) :
        assert not event_type_name in self.__event_type_lst, 'Event {} is exist'.format(event_type_name)
        self.__event_type_lst[event_type_name] = event_func
        self.__event_descri[event_type_name] = descri
        self.log_system('Register Event <{}>'.format(event_type_name))
        return event_type_name

    def set_event_descri(self,event_name,text) :
        if event_name in self.__event_descri :
            self.__event_descri[event_name] = text
            return True
        else :
            self.logerr('The {} is not exist'.format(event_name))
            return False

    def register_res(self,res_name, var) :
        assert not res_name in self.__res_lst, 'Resource {} is exist'.format(res_name)
        self.__res_lst[res_name] = Resource(res_name,var)
        self.log_system('Register Resource <{}> | {} : {}'.format(res_name,type(var),var))
        self.__res_lst[res_name].set_logger(self.resource_setter)
        return res_name

    def create_event(self,event_type_name,event_name,*argv) :
        assert event_type_name in self.__event_type_lst, 'Event type {} is not exist'.format(event_type_name)
        r_argv = []
        for r in argv :
            assert r in self.__res_lst, 'Resource {} is not exist'.format(r)
            r_argv.append(self.__res_lst[r])
        event = self.ResEvent(event_name,self.__event_type_lst[event_type_name],*r_argv)
        event.set_logger(self.event_setter)
        return event

    def package(self,process_name,event_chain,latency=None,periodic=lambda *x : True):
        block = self.EventBlock(process_name,event_chain,latency=latency,periodic=periodic)
        block.set_logger(self.block_setter)
        return block

    def sequence(self,*blocks) :
        self.__res_lst[self.__systime](self)
        self.__res_lst[self.__systime].set(self,0)
        self.__res_lst[self.__systime](self,relax=True)
        self.__sequence = []
        for b in blocks :
            assert isinstance(b,self.EventBlock), '{} is not the instance of <EventBlock>'.format(b)
            assert b.is_compile(), 'Event Block {} should be compiled'.format(b.name())
            self.__sequence += [b]
        return len(self.__sequence)

    def show_sequence(self) :
        s = 'Event Sequence---------------'
        print(s)
        for s in self.__sequence :
            print(s)
            print('-'*len(s))

    def list_events(self) :
        for meta in self.__event_type_lst :
            yield meta

    def isEvent(self,event_type) :
        return event_type in self.__event_type_lst

    def list_res(self) :
        for res in self.__res_lst :
            yield res

    def show_res(self) :
        while self.is_run() :
            pass
        print('-'*7,'Resource Definition','-'*7)
        for res in self.__res_lst :
            self.resMeta(res)

    def show_event(self) :
        while self.is_run() :
            pass
        print('-'*7,'Event Type Definition','-'*7)
        for event in self.__event_type_lst :
            self.eventMeta(event)
            #print('[',event,']  <- ',self.__event_descri[event])

    def compile_slot(self,t=0,show=False) :
        self.__compile_seq(t,self.__sequence)
        if show :
            init_e = {}
            for r in self.__res_link:
                b = self.__res_link[r]
                tt = self.__res_cost_time[r]
                print('---------------------------------')
                print(self.__res_lst[r])
                print('Start:',self.__res_init[r],'    ',0)
                print('  End:',b,'    ',tt)
            print('---------------------------------')

    def __compile_seq(self,t,sub_sequence):
        self.log_system('Compile phase {} Event sequence'.format(self.__phase_counter))
        sequence = [b.reset() for b in sub_sequence if b.periodic(t)]
        self.__reset_link()
        for block in sequence :
            assert block.is_compile(), 'Event Block <{}> should be compiled firstly.'.format(block.name())
            if not block.show_res() :
                self.__instant.append(block)
            else :
                for res in block.show_res() :
                    if not res in self.__res_init :
                        self.__res_link[res] = block
                        self.__res_init[res] = block
                        self.__res_cost_time[res] = block.show_time()
                        self.log_debug('Resource <{}> -> Event <{}> at time [{} - {}]'.format(res,block.name(),0,self.__res_cost_time[res]))
                    else :
                        obj = self.__res_link[res]
                        cost_t = self.__res_cost_time[res]
                        assert not block.is_late(cost_t), 'Event Block <{}> over the time limit at slot {} phase {} sub-slot {}'.format(block.name(),t,self.__phase_counter,cost_t)
                        obj.apply_res(block,res)
                        self.__res_link[res] = block
                        self.__res_cost_time[res] = cost_t + block.show_time()
                        self.log_debug('Event <{}> : <{}> -> Event <{}> at time [{} - {}]'.format(obj.name(),res,block.name(),cost_t,self.__res_cost_time[res]))
        self.__exec_counter = len(sequence)
        self.log_system('Event Sequence in Phase: {}'.format(self.__phase_counter))
        return sequence

    def dynamic_event(self,event_chain) :
        if type(event_chain) == self.ResEvent :
            temp = self.package(event_chain.name(),event_chain)
        else :
            temp = event_chain
        self.log_system('Append Event <{}> in next phase'.format(temp.name()))
        self.__sub_sequence.append(temp)
        return temp

    def showPrcTime(self,interrupt=False) :
        self.__show_prc_time = True
        self.__prc_interrupt = interrupt
        return self

    # 要修正會搶先interrupt的bug
    def __run_event(self,e_block:EventBlock):
        self.log_system('Enter the Event <{}>'.format(e_block.name()))
        r = e_block()
        self.log_system('Exit the Event <{}>'.format(e_block.name()))
        if self.__show_prc_time :
            e_block.showExecTime()
            if self.__prc_interrupt :
                input()
        self.__exec_counter -= 1
        if self.__exec_counter == 0 or self.__goEnd:
            self.__run_interrupt()
        else:
            self.log_debug('Remaining Event counter: {}'.format(self.__exec_counter))
            for e in r :
                if e[0].pass_res(self.__res_lst[e[1]]) :
                    self.log_debug('Wake the Event <{}>'.format(e[0]))
                    if self.__thread_flag :
                        threading.Thread(target = self.__run_event, args=(e[0],)).start()
                    else :
                        self.__run_event(e[0])

    def __seq_printer(self,seq) :
        basic_msg = 'Going to Process:'
        for a in seq :
            basic_msg += f'\n<{a.name()}> -> '
        basic_msg += f'\n[Phase Terminated]'
        self.log_system(basic_msg)

    def __run_phase(self,slot) :
        self.__phase_run = True
        sequence = self.__compile_seq(slot,self.__sub_sequence)
        self.__seq_printer(sequence)
        self.__sub_sequence = []
        for b in self.__instant :
            if self.__thread_flag :
                threading.Thread(target = self.__run_event, args=(b,)).start()
            else :
                self.__run_event(b)
        self.__instant = []
        for r in self.__res_init :
            e = self.__res_init[r]
            if e.pass_res(self.__res_lst[r]) :
                if self.__thread_flag :
                    threading.Thread(target = self.__run_event, args=(e,)).start()
                else :
                    self.__run_event(e)

    def run_slot(self,slot) :
        self.log_system('Processing at time slot {} is starting'.format(slot))
        if not self.__sequence :
            self.log_info('Do not exist the process sequence in the Event Model')
            return False
        self.__sub_sequence += self.__sequence
        self.__run_phase(slot)
        while self.__phase_run :
            pass
        return not self.__end_func(slot)

    def __run_interrupt(self):
        if self.__goEnd :
            self.log_system('Force to terminate at Slot {} Phase {}'.format(self.__s,self.__phase_counter))
            self.__phase_run = False
            self.__run_flag = False
            self.__end_func = lambda t : True
            self.__process_time = time.process_time() - self.__process_time
        self.log_system('Slot {} Phase {} is terminated'.format(self.__s,self.__phase_counter))
        if self.__sub_sequence :
            self.__phase_counter += 1
            self.log_system('Slot {} Phase {} is activating'.format(self.__s,self.__phase_counter))
            self.__run_phase(self.__s)
        else :
            self.log_system('Processing at time slot {} is terminated'.format(self.__s))
            if self.__final_process :
                self.log_system(f'Executing the Fianl process <{self.final_process().name()}>')
                self.final_process()()
                self.log_system('Completed the Fianl process')
            self.__s +=1
            self.__res_lst[self.__systime](self)
            self.__res_lst[self.__systime].set(self,self.__s)
            self.__res_lst[self.__systime](self,relax=True)
            self.__phase_counter = 0
            # recursion should be cope
            self.__res_cost_time = {n:0 for n in self.__res_lst}
            if not self.__end_func(self.__s):
                self.__phase_run = False
            else :
                self.log_system('Processing is terminated in time slot {} phase {}'.format(self.__s,self.__phase_counter))
                self.__run_flag = False
                self.__phase_run = False
                self.__process_time = time.process_time() - self.__process_time

    def forceTerminate(self) :
        self.__goEnd = True

    def time(self) :
        return self.__s

    def time_res(self) :
        return self.__systime

    def pause(self) :
        self.log_setter.pause()

    def stepByStep(self,t=1) :
        self.log_setter.stepByStep(t)

    def run(self,start=0,until=1) :
        self.__s = start
        self.__end_func = until
        self.__goEnd = False
        self.log_system('Processing at time slot {} is starting'.format(self.__s))
        if not self.__run_flag :
            if self.__thread_flag :
                self.log_info('Running in Multi-thread mode.')
            else :
                self.log_info('Running in Single-thread mode.')
            self.__process_time = time.process_time()
        self.__run_flag = True
        if type(until) == int :
            self.__end_func = lambda x : x==until
        while self.run_slot(self.__s) :
            pass
        return self.__s

    def is_run(self):
        return self.__run_flag

    def wait_to_finish(self) :
        while self.is_run() :
            pass
        return True

    def use_threading(self,choose=True):
        self.wait_to_finish()
        self.__thread_flag = choose
        return self.__thread_flag

    def logtime(self) :
        if self.__process_time :
            print('Using time: {}'.format(self.__process_time))
        else :
            print('The process time should be estimated by run'.format(self.__process_time))

    def final_process(self,event_block=None,clear=True) :
        if event_block :
            self.__final_process = event_block
        if clear :
            self.__sub_sequence = []
        return self.__final_process

    def set_decoder_to(self,res_name,decode_func) :
        assert res_name in self.__res_lst, 'The Resource <{}> is not existing'.format(res_name)
        self.__res_lst[res_name].set_decoder(decode_func)

    def logout(self,res) :
        assert res in self.__res_lst, f'The resource <{res}> is not existing'
        return self.__res_lst[res].decode()

    def log_resource(self,*res_name) :
        log_lst = {}
        for n in res_name :
            log_lst[n] = self.logout(n)
        return log_lst


if __name__ == '__main__' :
    EventLog.setGLog.displayLevel(0)
    a = lambda x,y : x+y
    c = 1
    b = 2
    class iterEvent(Event) :
        def call(self) :
            if self.var_iter :
                arg = [self.var_iter,*self.argv]
            else :
                arg = [0,*self.argv]
            return arg
    e1 = Event('Simple Add 1',a,b,c)
    e1.detail(time_cost=1)
    e2 = e1(iterEvent('Simple Add 2',a,b))
    print(e1.execute(test=True))
    print(e2.execute())
    e2 = iterEvent('Simple Add 2',a,b)(e1.reset())
    print(e2.execute())
    class resEvent(Event) :
        def call(self) :
            self.argv[0](self)
            arg = [self.argv[0].get(self),*self.argv[1:]]
            #self.log_setter.displayLevel(0)
            self.logger(arg,'debug')
            return arg
        def final(self) :
            self.argv[0](self,True)
            return True
    def foo1(a,b,c) :
        a[b] = c
    r1 = Resource('R1',{})
    efoo = resEvent('Test Foo1',foo1,r1,'A',1)
    efoo2 = resEvent('Test Foo2',foo1,r1,'A',2)
    r1(efoo)
    efoo()
    print(r1.get(efoo))
    r1(efoo,True)
    r1(efoo2)
    print(efoo2.execute())
    print(r1.get(efoo2))
    print(efoo(efoo2))
    r1(efoo2,True)
    print(r1)
    print(efoo2.execute())
    print(r1.get())
    env_t = EventChainFramework('hehe')
    #env_t.get_logger('event').displayLevel(None)
    #env_t.get_logger('block').displayLevel(None)
    env_t.use_threading(False)
    #env_t.use_threading(True)
    x1 = env_t.register_res('x1',1)
    x2 = env_t.register_res('x2',2)
    x3 = env_t.register_res('x3',3)
    x4 = env_t.register_res('x4',4)
    x5 = env_t.register_res('x5',5)
    x6 = env_t.register_res('x6',6)
    x7 = env_t.register_res('x7',7)
    x8 = env_t.register_res('x8',8)
    f1 = lambda x,y : print(x(True)+y(True))
    f2 = lambda x : print('Time Slot: ',x(True))
    etype1 = env_t.register_event('EzPlus',f1)
    sysprint = env_t.register_event('Print',f2)
    print_time = env_t.create_event(sysprint,'Time','SysTime')
    e_x1_x2 = env_t.create_event(etype1,'X1 + X2',x1,x2)
    e_x3_x4 = env_t.create_event(etype1,'X3 + X4',x3,x4)
    e_x5_x6 = env_t.create_event(etype1,'X5 + X6',x5,x6)
    e_x3_x5 = env_t.create_event(etype1,'X3 + X5',x3,x5)
    e_x2_x6 = env_t.create_event(etype1,'X2 + X6',x3,x5)
    e_x1_x3 = env_t.create_event(etype1,'X1 + X3',x1,x3)
    plus_stack = e_x1_x2(e_x3_x4(e_x2_x6))
    timeP = env_t.package('Print Time',print_time)
    ptcl = env_t.package('Plus Protocol',plus_stack)
    ptcl2 = env_t.package('Plus 5+6',e_x5_x6)
    ptcl3 = env_t.package('Plus 3+5',e_x3_x5)
    ptcl4 = env_t.package('Plus 1+3',e_x1_x3,periodic=lambda x : x==2)
    env_t.sequence(ptcl,ptcl2,ptcl3)
    env_t.run()
    while env_t.is_run() :
        pass
    def fuu() :
        env_t.trigger('Test Dynamic x5 x4',etype1,x5,x4)
        env_t.dynamic_event(env_t.create_event(etype1,'Test Dynamic x8 x7',x7,x8))
        pass
    env_t.register_event('fuu',fuu)
    e_fuu = env_t.package('FUU',env_t.create_event('fuu','fuu1'))
    e_fuu2 = env_t.package('FUU',env_t.create_event('fuu','fuu1'))
    env_t.sequence(timeP,ptcl4,e_fuu,e_fuu2,ptcl.reset(),ptcl3.reset(),ptcl2.reset())
    #env_t.sequence(timeP,ptcl4,ptcl.reset(),ptcl3.reset(),ptcl2.reset())
    env_t.run(until=3)
    env_t.show_res()
    env_t.show_event()
    env_t.logtime()
    env_t.meta('TEST META',lambda a, b : "{} {} META".format(a,b),1,2)
    env_t.meta('TEST META 2',lambda a, b : "{} {} META".format(a,b),type(1),2)
    env_t.show_event()
    env_t.showResType(env_t.time_res())
