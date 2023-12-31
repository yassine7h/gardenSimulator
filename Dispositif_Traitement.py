class Programme:
    def __init__(self, produit, debut, duree, periode):
        self.produit = produit
        self.debut = debut
        self.duree = duree
        self.periode = periode
        self.compteur = debut
        self.active =False

    def __str__(self):
        return f"produit={self.produit}, debut={self.debut}, duree={self.duree}, periode={self.periode}"


class Dispositif_Traitement:
    def __init__(self,parcelle, rayon):
        self.parcelle = parcelle
        self.rayon = rayon
        self.programs = []
        self.nb_fois_active=0

    def get_affected_parcelles(self):
        parcelles=[]
        if(self.rayon==1):
            parcelles=self.parcelle.get_neighbors()
            parcelles.append(self.parcelle)
        return parcelles



    def __str__(self):
        return f"Rayon={self.rayon}, programmes=[{'| '.join(map(str, self.programs))}]"
