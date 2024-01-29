import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# Employee Classes
class IEmploye(ABC):
    @abstractmethod
    def Age(self):
        pass

    @abstractmethod
    def Anciennete(self):
        pass

    @abstractmethod
    def DateRetraite(self, ageRetraite):
        pass

class IR:
    # Tranches dyal IR o taux dyalhom
    _tranches = [0, 28001, 40001, 50001, 60001, 150001]
    _tauxIR = [0, 0.12, 0.24, 0.34, 0.38, 0.40]

    @staticmethod
    def getIR(salaire):
        for i in range(1, 6):
            if salaire < IR._tranches[i]:
                return IR._tauxIR[i - 1]
        return IR._tauxIR[5]

class Employe(IEmploye):
    cpt = 0
    # Constructor dyal Employe
    def __init__(self, nom="", dateNaissance=datetime(2000, 1, 1), dateEmbauche=None, salaireBase=0):
        self._nom = nom
        self._dateNaissance = dateNaissance
        self._salaireBase = salaireBase
        Employe.cpt += 1
        self._mtle = Employe.cpt
        self._dateEmbauche = datetime.now() if dateEmbauche is None else dateEmbauche
        self.verifier_age_embauche()

    # Verifier l age dyal l employee waqt l embauche
    def verifier_age_embauche(self):
        age_embauche = (self._dateEmbauche - self._dateNaissance).days / 365
        if age_embauche < 16:
            raise ValueError("L'âge lors du recrutement doit être supérieur à 16 ans")

    @abstractmethod
    def SalaireAPayer(self):
        pass

    # Calculer l age
    def Age(self):
        return int((datetime.now() - self._dateNaissance).days / 365)

    # Calculer l anciennete
    def Anciennete(self):
        return int((datetime.now() - self._dateEmbauche).days / 365)

    # Date dyal la retraite
    def DateRetraite(self, ageRetraite):
        return self._dateNaissance + timedelta(days=ageRetraite * 365)

    def __str__(self):
        return f"{self._mtle}-{self._nom}-{self._dateNaissance.strftime('%d/%m/%Y')}-{self._dateEmbauche.strftime('%d/%m/%Y')}-{self._salaireBase}"

    def __eq__(self, other):
        if not isinstance(other, Employe):
            return False
        return self._mtle == other._mtle

class Agent(Employe):
    # Constructor dyal Agent
    def __init__(self, nom="", dateNaissance=datetime(2000, 1, 1), dateEmbauche=None, salaireBase=0, primeResponsabilite=0):
        super().__init__(nom, dateNaissance, dateEmbauche, salaireBase)
        self._primeResponsabilite = primeResponsabilite

    # Calculer le salaire à payer pour un agent
    def SalaireAPayer(self):
        return (self._salaireBase + self._primeResponsabilite) * (1 - IR.getIR(self._salaireBase * 12))

class Formateur(Employe):
    _remunerationHSup = 70.00

    # Constructor dyal Formateur
    def __init__(self, nom="", dateNaissance=datetime(2000, 1, 1), dateEmbauche=None, salaireBase=0, heureSup=0):
        super().__init__(nom, dateNaissance, dateEmbauche, salaireBase)
        self._heureSup = heureSup

    # Calculer le salaire à payer pour un formateur
    def SalaireAPayer(self):
        heuresSup = self._heureSup
        if heuresSup >= 30:
            heuresSup = 30
        return (self._salaireBase + heuresSup * Formateur._remunerationHSup) * (1 - IR.getIR(self._salaireBase * 12))

    def __str__(self):
        return super().__str__() + "-" + str(self._heureSup)

# JSON Serialization and Deserialization
def employe_encoder(obj):
    if isinstance(obj, Employe):
        # Convertir l'objet Employe en dictionnaire
        obj_dict = {
            '_nom': obj._nom,
            '_dateNaissance': obj._dateNaissance.isoformat(),
            '_salaireBase': obj._salaireBase,
            '_mtle': obj._mtle,
            '_dateEmbauche': obj._dateEmbauche.isoformat(),
        }
        if isinstance(obj, Agent):
            obj_dict['_primeResponsabilite'] = obj._primeResponsabilite
        elif isinstance(obj, Formateur):
            obj_dict['_heureSup'] = obj._heureSup
        return obj_dict
    return obj

def employe_decoder(dct):
    if '_nom' in dct:
        dct['_dateNaissance'] = datetime.fromisoformat(dct['_dateNaissance'])
        dct['_dateEmbauche'] = datetime.fromisoformat(dct['_dateEmbauche'])
        
        if '_primeResponsabilite' in dct:
            return Agent(nom=dct['_nom'], dateNaissance=dct['_dateNaissance'], dateEmbauche=dct['_dateEmbauche'], 
                         salaireBase=dct['_salaireBase'], primeResponsabilite=dct['_primeResponsabilite'])
        elif '_heureSup' in dct:
            return Formateur(nom=dct['_nom'], dateNaissance=dct['_dateNaissance'], dateEmbauche=dct['_dateEmbauche'], 
                             salaireBase=dct['_salaireBase'], heureSup=dct['_heureSup'])
        else:
            return Employe(nom=dct['_nom'], dateNaissance=dct['_dateNaissance'], dateEmbauche=dct['_dateEmbauche'], 
                           salaireBase=dct['_salaireBase'])
    return dct

def charger_comptes(fichier):
    # Chargi l comptes men fichier
    try:
        with open(fichier, 'r') as file:
            return json.load(file, object_hook=employe_decoder)
    except FileNotFoundError:
        return []

def sauvegarder_comptes(comptes, fichier):
    # Sauvegarde l comptes f fichier
    with open(fichier, 'w') as file:
        json.dump(comptes, file, default=employe_encoder)

#Application Class
class PayrollApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll System")
        self.root.geometry("800x600")

        self.comptes = charger_comptes('comptes.json')
        self.create_widgets()

    def create_widgets(self):
        # nsawbo l interface dyal l application
        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        # Add Employee Button
        tk.Button(button_frame, text="Add Employee", command=self.add_employee).grid(row=0, column=0, padx=10)

        # Remove Employee Button
        tk.Button(button_frame, text="Remove Employee", command=self.remove_employee).grid(row=0, column=1, padx=10)

        # Refresh Button to Update Table
        tk.Button(button_frame, text="Refresh Table", command=self.refresh_table).grid(row=0, column=2, padx=10)

        # Save and Exit Button
        tk.Button(button_frame, text="Save and Exit", command=self.save_and_exit).grid(row=0, column=3, padx=10)

        # Table to Display Employees
        self.tree = ttk.Treeview(self.root, columns=('Name', 'Birth Date', 'Hiring Date', 'Base Salary', 'Type', 'Extra'))
        self.tree.heading('#0', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Birth Date', text='Birth Date')
        self.tree.heading('Hiring Date', text='Hiring Date')
        self.tree.heading('Base Salary', text='Base Salary')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Extra', text='Extra')
        self.tree.pack()


    def add_employee(self):
        # nziido employee jdid
        nom = simpledialog.askstring("Input", "Enter employee's name", parent=self.root)
        dateNaissance = simpledialog.askstring("Input", "Enter birth date (YYYY-MM-DD)", parent=self.root)
        dateEmbauche = simpledialog.askstring("Input", "Enter hiring date (YYYY-MM-DD)", parent=self.root)
        salaireBase = simpledialog.askfloat("Input", "Enter base salary", parent=self.root)

        type_employe = simpledialog.askstring("Input", "Enter employee type (Agent/Formateur)", parent=self.root)
        if type_employe is None:
            messagebox.showerror("Error", "No employee type entered")
            return

        if type_employe.lower() == 'agent':
            primeResponsabilite = simpledialog.askfloat("Input", "Enter responsibility premium", parent=self.root)
            new_employee = Agent(nom, datetime.fromisoformat(dateNaissance), datetime.fromisoformat(dateEmbauche), salaireBase, primeResponsabilite)
        elif type_employe.lower() == 'formateur':
            heureSup = simpledialog.askfloat("Input", "Enter number of extra hours", parent=self.root)
            new_employee = Formateur(nom, datetime.fromisoformat(dateNaissance), datetime.fromisoformat(dateEmbauche), salaireBase, heureSup)
        else:
            messagebox.showerror("Error", "Invalid employee type")
            return
          
            self.comptes.append(new_employee)
            messagebox.showinfo("Success", "Employee added successfully")

    def display_employees(self):
        #Naffichiw hbabna
        display_text = "\n".join(str(compte) for compte in self.comptes)
        messagebox.showinfo("Employees", display_text)

    def remove_employee(self):
        #Nmes7o chi Hbibna
        selected_item = self.tree.selection()
        if selected_item:
            employee_id = self.tree.item(selected_item)['text']
            self.comptes = [emp for emp in self.comptes if emp._mtle != employee_id]
            self.refresh_table()
            messagebox.showinfo("Success", "Employee removed successfully")
        else:
            messagebox.showwarning("Warning", "No employee selected")

    def refresh_table(self):
        # Refresh l tableau dyal hbabna
        for i in self.tree.get_children():
            self.tree.delete(i)

        for compte in self.comptes:
            if isinstance(compte, Agent):
                employee_type = 'Agent'
                extra = compte._primeResponsabilite
            elif isinstance(compte, Formateur):
                employee_type = 'Formateur'
                extra = compte._heureSup
            else:
                employee_type = 'Employe'
                extra = 'N/A'

            self.tree.insert('', 'end', text=compte._mtle, values=(compte._nom, compte._dateNaissance.strftime('%Y-%m-%d'),
                                compte._dateEmbauche.strftime('%Y-%m-%d'), compte._salaireBase, employee_type, extra))


    def save_and_exit(self):
        # Sauvegarde les données o khruj men l application
        sauvegarder_comptes(self.comptes, 'comptes.json')
        self.root.quit()

def main():
    root = tk.Tk()
    app = PayrollApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
