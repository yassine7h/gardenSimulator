import random

class Insecte:
    def __init__(self, parcelle, espece, sexe, sante_max, duree_vie_max, proba_mobilite, resistance_insecticide,
                 temps_entre_reproduction, max_portee):
        self.parcelle = parcelle
        self.espece = espece
        self.sexe = sexe
        self.sante_max = sante_max
        self.sante = sante_max
        self.duree_vie_max = duree_vie_max
        self.proba_mobilite = proba_mobilite
        self.proba_mobilite_actuelle=proba_mobilite
        self.resistance_insecticide = resistance_insecticide
        self.temps_entre_reproduction = temps_entre_reproduction
        self.max_portee = max_portee

        self.stack_manger = 0
        self.age=0

        self.deplacement = []

        self.treated = False

        self.temps_avant_prochaine_reproduction=temps_entre_reproduction
        self.married= False


    def random_int(self,min_val, max_val):
        return random.randint(min(min_val, max_val), max(min_val, max_val))
    def random_float(self, min_val, max_val):
        return random.uniform(min(min_val, max_val), max(min_val, max_val))

    def reproduction(self, parent):

        parent_m = self if self.sexe == "M" else parent
        parent_f = parent if parent_m != parent else self

        for index in range(random.randint(0, parent_f.max_portee)):
            insecte_c=Insecte(parent_f.parcelle,
                                parent_f.espece,
                                random.choice(["M", "F"]),
                                self.random_int(parent_m.sante_max, parent_f.sante_max),
                                self.random_int(parent_m.duree_vie_max, parent_f.duree_vie_max),
                                self.random_float(parent_m.proba_mobilite, parent_f.proba_mobilite),
                                self.random_float(parent_m.resistance_insecticide, parent_f.resistance_insecticide),
                                self.random_int(parent_m.temps_entre_reproduction, parent_f.temps_entre_reproduction),
                                self.random_int(parent_m.max_portee, parent_f.max_portee),
                            )
            insecte_c.sante//=2
            insecte_c.temps_avant_prochaine_reproduction*=2
            parent_f.parcelle.insectes.append(insecte_c)

    def __str__(self):
        return f"Insecte: {self.espece}, {self.sexe}, {self.sante}/{self.sante_max}, " \
               f"age={self.age} max_age={self.duree_vie_max}, mobilite={self.proba_mobilite_actuelle} mobilite_org={self.proba_mobilite}, " \
               f"resis_insecticide={self.resistance_insecticide}, reproduciton={self.temps_entre_reproduction}, max_porte={self.max_portee}, dep=[{', '.join(map(str, self.deplacement))}]"
