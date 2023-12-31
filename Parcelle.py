class Parcelle:
    def __init__(self, potager, position_x, position_y):
        self.potager = potager
        self.position_x = position_x
        self.position_y = position_y
        self.plantes = []
        self.insectes = []
        self.dispositif_traitement = None
        self.humidite = 0.5
        self.engrais = False
        self.insecticides = False
        self.compteur = {
            "engrais": 0,
            "insecticides": 0
        }
        self.nb_insectes=0
    def engrais_update(self):
        self.compteur["engrais"]= max(0,self.compteur["engrais"]-1)
        if(self.compteur["engrais"]>0):
            self.engrais = True
        else:
            self.engrais = False

    def insecticides_update(self):
        self.compteur["insecticides"]= max(0,self.compteur["insecticides"]-1)
        if(self.compteur["insecticides"]>0):
            self.insecticides = True
        else:
            self.insecticides = False

    def get_neighbors(self):
        coordinates = []
        if self.position_y > 0:
            coordinates.append([self.position_x, self.position_y - 1])
        if self.position_y < self.potager.size_y:
            coordinates.append([self.position_x, self.position_y + 1])
        if self.position_x > 0:
            coordinates.append([self.position_x - 1, self.position_y])
        if self.position_x < self.potager.size_x:
            coordinates.append([self.position_x + 1, self.position_y])
        neighbors = []
        for coordinate in coordinates:
            for parcelle in self.potager.parcelles:
                if parcelle.position_x == coordinate[0] and parcelle.position_y == coordinate[1]:
                    neighbors.append(parcelle)
        return neighbors

    def __str__(self):
        return f"Position: ({self.position_x}, {self.position_y}), {len(self.plantes) > 0}"
