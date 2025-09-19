from dataclasses import dataclass
import random

@dataclass
class Manger:
    bouche: bool=False
    
    def ouvrir_la_bouche(self):
        self.bouche = random.choice([True, False])
        return self.bouche


m = Manger()
print("Test :", m.ouvrir_la_bouche())