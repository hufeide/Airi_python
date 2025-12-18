
import time,random
class MemoryStore:
    def __init__(self):
        self.short=[]
        self.long=[]
        self.dreams=[]

    def add(self,text):
        self.short.append((time.time(),text))

    def consolidate(self):
        now=time.time()
        for t,x in list(self.short):
            if now-t>5:
                self.long.append(x)
                self.short.remove((t,x))

    def dream(self):
        if len(self.long)>=2:
            summary="Dream:"+random.choice(self.long)+" & "+random.choice(self.long)
            self.dreams.append(summary)
            return summary
        return None
