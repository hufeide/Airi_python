
import time
class Tracer:
    def __init__(self):
        self.traces=[]
    def record(self,node,state):
        self.traces.append({"node":node,"time":time.time(),"state":{k:str(v) for k,v in state.items()}})
