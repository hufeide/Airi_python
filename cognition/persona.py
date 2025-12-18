
class PersonaState:
    def __init__(self):
        self.emotional=0.0
        self.rational=0.0
        self.trust=0.2
        self.relationship=0.2

    def update(self,text):
        if any(w in text for w in ["谢谢","信你"]):
            self.trust=min(1.0,self.trust+0.1)
        if any(w in text for w in ["压力","焦虑"]):
            self.emotional+=0.3
        if any(w in text for w in ["分析","方案"]):
            self.rational+=0.3
