import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import filedialog
from Simulation import Simulation

class GUI:
    def __init__(self,root: tk.Tk):
        self.root = root
        self.root.config(padx=10,pady=10)
        self.root.title("Simulation")
        self.sim = Simulation()
        self.root.minsize(1200,800)

        self.buttons_layout= ttk.Frame(self.root)
        self.buttons_layout.place(x=0, y=0, relwidth=1, relheight=0.2)
        self.buttons_layout.rowconfigure(tuple(range(1)), weight=1)
        self.buttons_layout.columnconfigure(tuple(range(3)), weight=1)

        self.matrix_layout = ttk.Frame(self.root)
        self.matrix_layout.place(x=0, rely=0.2, relwidth=1, relheight=0.8)

        ttk.Button(self.buttons_layout, text="Charger Configuration", command=self.load_configuration).grid(row=0,column=0 )
        ttk.Button(self.buttons_layout, text="Lancer Simulation", command=self.run_simulation).grid(row=0,column=1 )
        ttk.Button(self.buttons_layout, text="Sauvegarder Simulation", command=self.save_simulation).grid(row=0,column=2 )


    def load_configuration(self):
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier de configuration",
                                               filetypes=[("Fichiers XML", "*.xml")])
        if file_path:
            self.sim.charger_configuration(file_path)
            for c in self.matrix_layout.winfo_children(): c.destroy()

    def run_simulation(self):
        self.sim.simulate(logging=False)
        potager_obj = self.sim.generate_resulte()
        self.matrix_layout.rowconfigure(tuple(range(potager_obj['Size_y'])), weight=1)
        self.matrix_layout.columnconfigure(tuple(range(potager_obj['Size_x'])), weight=1)
        for parcelle in potager_obj["Parcelles"]:
            but = tk.Button(self.matrix_layout)
            but.config(bg='green')
            text=""
            if parcelle["Nb_plantes"]>0:
                text+="\nPlantes"

            if parcelle["Nb_insectes"]>0:
                text+=("\nInsectes")

            if parcelle["Engrais"]:
                text+=("\nEngrais")

            if parcelle["Insecticides"]:
                text+=("\nInsecticides")

            if parcelle["Dispositif"] is not None:
                text+=("\nDispositif")

            but.config(text=text)
            but.config(fg="white")

            but.grid(row=parcelle["Pos_y"], column=parcelle["Pos_x"], sticky="nswe")
            but.config(command=lambda p=parcelle:self.detail_window(p))

    def detail_window(self,parcelle):
        win = tk.Toplevel(self.root)
        win.minsize(500, 500)
        win.title(f"Parcelle ({parcelle['Pos_x']}, {parcelle['Pos_y']})")

        detail_frame = ttk.Frame(win)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        text_widget = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, width=45, height=10)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        text_widget.insert(tk.END, f"Humidite: {parcelle['Humidite']}\n")
        text_widget.insert(tk.END, f"Engrais: {'Oui' if parcelle['Engrais'] else 'Non'}\n")
        text_widget.insert(tk.END, f"Insecticides: {'Oui' if parcelle['Insecticides'] else 'Non'}\n")
        text_widget.insert(tk.END, f"Nombre des insectes: {parcelle['Nb_insectes']}\n")
        text_widget.insert(tk.END, f"Nombre des plantes: {parcelle['Nb_plantes']}\n")
        if parcelle['Dispositif'] is None:
            text_widget.insert(tk.END, f"Dispositif de traitement: {'Non'}\n")
        else:
            disp="\n   Rayon: "+str(parcelle['Dispositif']['Rayon'])+"\n   Nombre de fois activé: "+str(parcelle['Dispositif']['Nb_fois_active'])+"\n   Programmes: \n   "+str(parcelle['Dispositif']['Programmes'])
            text_widget.insert(tk.END, f"Dispositif de traitement: {disp}\n")

        plantes_widget = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, width=45, height=10)
        plantes_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        insectes_widget = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, width=45, height=10)
        insectes_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        plantes_widget.insert(tk.END, f"Plantes:\n")
        for plante in parcelle["Plante"]:
             for key in plante:
                 if key == "Recoltes":
                     if plante["Total_recoltes"]>0:
                         plantes_widget.insert(tk.END, f"\nRecoltes:")
                         for recolte in plante["Recoltes"]:
                             plantes_widget.insert(tk.END, f"\n[Developpement: {recolte['Developpement']}, Duree_insecticides: {recolte['Duree_insecticides']}]")
                 else:
                    plantes_widget.insert(tk.END, f"\n{key}: {plante[key]}")
             plantes_widget.insert(tk.END, f"\n------------------------")

        insectes_widget.insert(tk.END, f"Insectes:\n")
        for insecte in parcelle["Insectes"]:
            for key in insecte:
                insectes_widget.insert(tk.END, f"\n{key}: {insecte[key]}")
            insectes_widget.insert(tk.END, f"\n------------------------")

    def save_simulation(self):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("Fichiers XML", "*.xml")],
                title="Enregistrer Simulation"
            )
            if file_path:
                self.sim.generate_resulte(file_path)




if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
