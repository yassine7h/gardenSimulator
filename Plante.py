class Recolte:
    def __init__(self, plante , developpement,duree_insecticide):
        self.plante = plante
        self.developpement = developpement
        self.duree_insecticide = duree_insecticide

class Plante:
    def __init__(self, parcelle , espece, maturite_pied, maturite_fruit, nb_recolte, surface, humidite_min,
                 humidite_max, dragonnante):
        self.parcelle = parcelle
        self.espece = espece
        self.maturite_pied = maturite_pied
        self.maturite_fruit = maturite_fruit
        self.nb_recolte = nb_recolte #nombre de recoltes max
        self.surface = surface
        self.humidite_min = humidite_min
        self.humidite_max = humidite_max
        self.dragonnante = dragonnante
        self.dev = 1
        self.recoltes = []
        self.nb_pas_avant_recolter = maturite_pied + maturite_fruit
        self.duree_insecticide_recolte = 0
        self.duree_insecticide = 0
        self.age=0

    def calc_dev(self):
        self.dev= max(0, (1 + self.parcelle.engrais) * (1 + int(self.humidite_min < self.parcelle.humidite < self.humidite_max)+ int(len(self.parcelle.insectes) > 0)))

    def update_duree_insecticide(self):
        self.age+=1
        if(self.parcelle.insecticides): self.duree_insecticide+=1
        if(self.age>=self.maturite_pied
        and self.parcelle.insecticides
        ): self.duree_insecticide_recolte+=1

    def recolter(self):
        if not self.dragonnante:
            if self.nb_pas_avant_recolter == 0:
                self.nb_pas_avant_recolter = self.maturite_fruit - 1
                if(len(self.recoltes)<self.nb_recolte):
                    self.recoltes.append(
                        Recolte(
                            self,
                            self.dev,
                            self.duree_insecticide_recolte
                        )
                    )
                    self.duree_insecticide_recolte=0
            else:
                self.nb_pas_avant_recolter = max(0,self.nb_pas_avant_recolter-1)


    def __str__(self):
        return f"Plante(Espece: {self.espece}, dev={self.dev}, Nb_recolte_actuel: {len(self.recoltes)} ,Maturite_pied: {self.maturite_pied}, Maturite_fruit: {self.maturite_fruit}, Nb_recolte: {self.nb_recolte}, Surface: {self.surface}, Humidite_min: {self.humidite_min}, Humidite_max: {self.humidite_max})"

