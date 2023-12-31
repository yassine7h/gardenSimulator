import xml.etree.ElementTree as ET
import random
from Insecte import Insecte
from Potager import Potager
from Parcelle import Parcelle
from Plante import Plante
from Dispositif_Traitement import Dispositif_Traitement, Programme
from xml.dom import minidom

class Simulation:
    def __init__(self):
        self.potager = None

    def charger_configuration(self, file):
        tree = ET.parse(file)
        root = tree.getroot()

        potager = Potager(
            root.get("Nom"),
            int(root.get("Nb_iterations")),
            int(root.get("Size_x")),
            int(root.get("Size_y")),
        )

        for parcelle in root.findall(".//Parcelle"):
            parcelle_obj = Parcelle(potager, int(parcelle.get("Pos_x")), int(parcelle.get("Pos_y")))


            for plante in parcelle.findall("Plante") + parcelle.findall("Plante_Drageonnante"):
                plante_obj = Plante(parcelle_obj,
                                    plante.get("Espece"),
                                    int(plante.get("Maturite_pied")),
                                    int(plante.get("Maturite_fruit")),
                                    int(plante.get("Nb_recolte")),
                                    float(plante.get("Surface")),
                                    float(plante.get("Humidite_min")),
                                    float(plante.get("Humidite_max")),
                                    plante.tag == "Plante_Drageonnante"
                                    )
                parcelle_obj.plantes.append(plante_obj)

            for insecte in parcelle.findall("Insecte"):
                insecte_obj = Insecte(parcelle_obj,
                                      insecte.get("Espece"),
                                      insecte.get("Sexe"),
                                      int(insecte.get("Vie_max")),
                                      int(insecte.get("Duree_vie_max")),
                                      float(insecte.get("Proba_mobilite")),
                                      float(insecte.get("Resistance_insecticide")),
                                      int(insecte.get("Temps_entre_repro")),
                                      int(insecte.get("Max_portee"))
                                      )
                parcelle_obj.insectes.append(insecte_obj)

            dispositif = parcelle.find("Dispositif")
            if dispositif is not None:
                dispositif_obj = Dispositif_Traitement(parcelle_obj, int(dispositif.get("Rayon")))
                for programme in dispositif.findall("Programme"):
                    programme_obj = Programme(
                        programme.get("Produit"),
                        int(programme.get("Debut")),
                        int(programme.get("Duree")),
                        int(programme.get("Periode")),
                    )
                    dispositif_obj.programs.append(programme_obj)
                parcelle_obj.dispositif_traitement = dispositif_obj

            potager.parcelles.append(parcelle_obj)

        self.potager = potager

    def simulate(self,logging):

        pas = 0
        while pas <= self.potager.nb_iterations:
            # deplacement des insectes
            if pas > 0:
                treated_insects = set()
                for parcelle in self.potager.parcelles:
                    for insecte in parcelle.insectes:
                        if insecte in treated_insects:
                            continue
                        if random.random() <= insecte.proba_mobilite_actuelle:
                            neighbors = insecte.parcelle.get_neighbors()
                            to_parcelle = neighbors[random.randint(0, len(neighbors) - 1)]
                            treated_insects.add(insecte)
                            insecte.deplacement.append(
                                f"({pas})({insecte.parcelle.position_x}, {insecte.parcelle.position_y}) -> ({to_parcelle.position_x}, {to_parcelle.position_y})")
                            insecte.parcelle.insectes.remove(insecte)
                            insecte.parcelle = to_parcelle
                            to_parcelle.insectes.append(insecte)

            # recoltation des plantes
            for parcelle in self.potager.parcelles:
                for plante in parcelle.plantes:
                    plante.calc_dev()
                    plante.update_duree_insecticide()
                    plante.recolter()

            # nutrition des insectes
            for parcelle in self.potager.parcelles:
                for insecte in parcelle.insectes:
                    if (insecte.age >= insecte.duree_vie_max
                            or insecte.sante <= 0
                            or (parcelle.insecticides and random.random() > insecte.resistance_insecticide)
                    ):
                        insecte.parcelle.insectes.remove(insecte)

                    insecte.age += 1

                    if float(insecte.sante) < 0.2 * float(insecte.sante_max):  insecte.proba_mobilite_actuelle /= 2.0

                    if insecte.stack_manger == 3:
                        insecte.sante = min(insecte.sante + 1, insecte.sante_max)
                        insecte.stack_manger = 0
                    if insecte.stack_manger == -3:
                        insecte.proba_mobilite_actuelle = min(insecte.proba_mobilite_actuelle * 2.0, 1.0)
                        insecte.stack_manger = 0

                    if len(insecte.parcelle.plantes) > 0:
                        insecte.proba_mobilite_actuelle = insecte.proba_mobilite
                        if insecte.stack_manger <= 0:
                            insecte.stack_manger = 1
                        else:
                            insecte.stack_manger += 1
                    else:
                        insecte.sante -= 1
                        if insecte.stack_manger >= 0:
                            insecte.stack_manger = -1
                        else:
                            insecte.stack_manger -= 1

            # reproduction
            for parcelle in self.potager.parcelles:
                for insecte1 in parcelle.insectes:
                    for insecte2 in parcelle.insectes:
                        if (insecte1 != insecte2
                                and insecte1.espece == insecte2.espece
                                and insecte1.sexe != insecte2.sexe
                                and not insecte1.married
                                and not insecte2.married
                        ):
                            if (insecte1.temps_avant_prochaine_reproduction == 0
                                    and insecte2.temps_avant_prochaine_reproduction == 0):
                                insecte1.married = True
                                insecte2.married = True
                                insecte1.reproduction(insecte2)
                                insecte1.temps_avant_prochaine_reproduction = insecte1.temps_entre_reproduction
                                insecte2.temps_avant_prochaine_reproduction = insecte2.temps_entre_reproduction

                    insecte1.temps_avant_prochaine_reproduction = max(0,
                                                                      insecte1.temps_avant_prochaine_reproduction - 1)
                for insecte in parcelle.insectes:
                    insecte.married = False

            # Dispositifs
            for parcelle in self.potager.parcelles:
                dis = parcelle.dispositif_traitement
                if dis is not None:
                    dis.nb_fois_active += 1
                    for program in dis.programs:
                        for affected_parcelle in dis.get_affected_parcelles():
                            if program.produit == "Eau":
                                if program.compteur <= 0:
                                    affected_parcelle.humidite = min(
                                        affected_parcelle.humidite + 0.5 * affected_parcelle.humidite, 1)
                                    program.compteur = program.periode
                                else:
                                    affected_parcelle.humidite = max(
                                        affected_parcelle.humidite - 0.2 * affected_parcelle.humidite, 0)
                                    program.compteur -= 1

                            if program.produit == "Engrais":
                                if program.compteur <= 0:
                                    affected_parcelle.engrais = True
                                    affected_parcelle.compteur["engrais"] = 5
                                    program.compteur = program.periode
                                else:
                                    affected_parcelle.engrais_update()
                                    program.compteur -= 1

                            if program.produit == "Insecticide":
                                if program.compteur <= 0:
                                    affected_parcelle.insecticides = True
                                    affected_parcelle.compteur["insecticides"] = 5
                                    program.compteur = program.periode
                                else:
                                    affected_parcelle.insecticides_update()
                                    program.compteur -= 1


            if (logging):
                print(
                    f"*****************************[ {str(pas)} / {str(self.potager.nb_iterations)} ]****************************************")
                self.print_res_to_console(self.potager)

            pas += 1

    def generate_resulte(self, filename=None):
        potager=self.potager
        root = ET.Element("Pootager", {"Nom": potager.nom, "Nb_iterations": str(potager.nb_iterations),
                                      "Size_x": str(potager.size_x), "Size_y": str(potager.size_y)})

        for parcelle in potager.parcelles:
            parcelle_elem = ET.SubElement(root, "Parcelle",
                                          {
                                                    "Pos_x": str(parcelle.position_x),
                                                    "Pos_y": str(parcelle.position_y),
                                                    "Humidite": str(parcelle.humidite),
                                                    "Engrais": str(parcelle.engrais),
                                                    "Insecticides": str(parcelle.insecticides),
                                                    "Nb_insectes": str(len(parcelle.insectes)),
                                                    "Nb_plantes": str(len(parcelle.plantes))
                                                }
                                          )

            for plante in parcelle.plantes:
                plante_elem = ET.SubElement(parcelle_elem, "Plante_Drageonnante" if plante.dragonnante else "Plante", {"Espece": plante.espece,
                                                                          "Maturite_pied": str(plante.maturite_pied),
                                                                          "Maturite_fruit": str(plante.maturite_fruit),
                                                                          "Nb_recolte": str(plante.nb_recolte),
                                                                          "Surface": str(plante.surface),
                                                                          "Humidite_min": str(plante.humidite_min),
                                                                          "Humidite_max": str(plante.humidite_max),
                                                                          "Developpement": str(plante.dev),
                                                                          "Total_recoltes": str(len(plante.recoltes)),
                                                                          "Duree_insecticides": str(plante.duree_insecticide)
                                                                          })
                for recolte in plante.recoltes:
                    ET.SubElement(plante_elem,"Recolte",{
                        "Developpement":str(recolte.developpement),
                        "Duree_insecticides":str(recolte.duree_insecticide)
                    })

            if parcelle.dispositif_traitement is not None:
                dispositif_elem = ET.SubElement(parcelle_elem, "Dispositif", {
                    "Rayon": str(parcelle.dispositif_traitement.rayon),
                    "Nb_fois_active": str(parcelle.dispositif_traitement.nb_fois_active)
                })
                for prog in parcelle.dispositif_traitement.programs:
                    ET.SubElement(dispositif_elem, "Programme",{"Produit" : prog.produit })

            for insecte in parcelle.insectes:
                ET.SubElement(parcelle_elem, "Insecte", {"Espece": insecte.espece,
                                                                        "Sexe": insecte.sexe,
                                                                        "Sante": str(insecte.sante)+"/"+ str(insecte.sante_max),
                                                                        "Age" : str(insecte.age),
                                                                        "Duree_vie_max": str(insecte.duree_vie_max),
                                                                        "Proba_mobilite": str( insecte.proba_mobilite_actuelle),
                                                                        "Proba_mobilite_genetique": str(insecte.proba_mobilite),
                                                                        "Nb_deplacement" : str(len(insecte.deplacement)),
                                                                        "Resistance_insecticide": str(
                                                                            insecte.resistance_insecticide),
                                                                        "Max_portee": str(insecte.max_portee),
                                                                        "Frequence_reproduction": str( insecte.temps_entre_reproduction)})



        xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="    ")[23:]

        if(filename is not None):
            with open(filename, "w") as xml_file:
                xml_file.write(xml_str)
        else:
            return self.xml_to_json(xml_str)

    def print_res_to_console(self,po=None):
        for parcelle in po.parcelles if po is not None else self.potager.parcelles:
            print(parcelle)
            for plante in parcelle.plantes:
                print(f"    {plante}")
            for insecte in parcelle.insectes:
                print(f"    {insecte}")
            if parcelle.dispositif_traitement is not None:
                print(f"    {parcelle.dispositif_traitement}")

    def xml_to_json(self,xml):
            root = ET.fromstring(xml)
            potager_info = {
                "Nom": root.get("Nom"),
                "Nb_iterations": int(root.get("Nb_iterations")),
                "Size_x": int(root.get("Size_x")),
                "Size_y": int(root.get("Size_y")),
                "Parcelles": []
            }

            for parcelle in root.findall("Parcelle"):
                parcelle_info = {
                    "Pos_x": int(parcelle.get("Pos_x")),
                    "Pos_y": int(parcelle.get("Pos_y")),
                    "Humidite": float(parcelle.get("Humidite")),
                    "Engrais": parcelle.get("Engrais")=="True",
                    "Insecticides": parcelle.get("Insecticides")=="True",
                    "Nb_insectes": int(parcelle.get("Nb_insectes")),
                    "Nb_plantes": int(parcelle.get("Nb_plantes")),
                    "Plante": [],
                    "Insectes": [],
                    "Dispositif": None
                }

                for insecte in parcelle.findall("Insecte"):
                    insecte_info = {
                        "Espece": str(insecte.get("Espece")),
                        "Sexe": str(insecte.get("Sexe")),
                        "Sante": str(insecte.get("Sante")),
                        "Age": int(insecte.get("Age")),
                        "Duree_vie_max": int(insecte.get("Duree_vie_max")),
                        "Proba_mobilite": float(insecte.get("Proba_mobilite")),
                        "Proba_mobilite_genetique": float(insecte.get("Proba_mobilite_genetique")),
                        "Nb_deplacement": int(insecte.get("Nb_deplacement")),
                        "Resistance_insecticide": float(insecte.get("Resistance_insecticide")),
                        "Max_portee": int(insecte.get("Max_portee")),
                        "Frequence_reproduction": int(insecte.get("Frequence_reproduction")),
                    }
                    parcelle_info["Insectes"].append(insecte_info)

                if parcelle.find("Dispositif") is not None:
                    dispositif_info = {
                        "Rayon": int(parcelle.find("Dispositif").get("Rayon")),
                        "Nb_fois_active": int(parcelle.find("Dispositif").get("Nb_fois_active")),
                        "Programmes": []
                    }
                    for prog in parcelle.find("Dispositif").findall("Programme"):
                        dispositif_info["Programmes"].append(prog.get("Produit"))
                    parcelle_info["Dispositif"] = dispositif_info

                for plante in parcelle.findall("Plante")+parcelle.findall("Plante_Drageonnante"):
                    plante_info = {
                        "Espece": plante.get("Espece"),
                        "Maturite_pied": int(plante.get("Maturite_pied")),
                        "Maturite_fruit": int(plante.get("Maturite_fruit")),
                        "Nb_recolte": int(plante.get("Nb_recolte")),
                        "Surface": float(plante.get("Surface")),
                        "Humidite_min": float(plante.get("Humidite_min")),
                        "Humidite_max": float(plante.get("Humidite_max")),
                        "Developpement": int(plante.get("Developpement")),
                        "Duree_insecticides": int(plante.get("Duree_insecticides")),
                        "Total_recoltes": int(plante.get("Total_recoltes")),
                        "Recoltes": []
                    }
                    for recolte in plante.findall("Recolte"):
                        recolte_info = {
                            "Developpement": int(recolte.get("Developpement")),
                            "Duree_insecticides": int(recolte.get("Duree_insecticides")),
                        }
                        plante_info["Recoltes"].append(recolte_info)

                    parcelle_info["Plante"].append(plante_info)

                potager_info["Parcelles"].append(parcelle_info)

            return potager_info