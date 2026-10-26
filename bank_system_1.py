class BankAccount:
    def __init__(self, account_number, owner_name, balance=0.0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def __str__(self):
        return f"Account #{self.account_number} | Owner: {self.owner_name} | Balance: {self.balance:.2f}€"


class Bank:
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.accounts = {}

    def open_account(self, account_number, owner_name, initial_balance):
        new_account = BankAccount(account_number, owner_name, initial_balance)
        self.accounts[account_number] = new_account

    def get_account(self, account_number):
        return self.accounts.get(account_number)

    # 1. ΑΠΟΘΗΚΕΥΣΗ ΣΕ ΑΡΧΕΙΟ (Save)
    def save_to_file(self, filename="bank_data.txt"):
        with open(filename, "w") as file:
            for account in self.accounts.values():
                file.write(f"{account}\n")
        print("Όλα τα δεδομένα αποθηκεύτηκαν στο αρχείο!")

    # 2. ΦΟΡΤΩΣΗ ΑΠΟ ΑΡΧΕΙΟ (Load) - ΝΕΑ ΜΕΘΟΔΟΣ!
    def load_from_file(self, filename="bank_data.txt"):
        try:
            with open(filename, "r") as file:
                for line in file:
                    # Αφαιρούμε τα κενά/αλλαγές γραμμής
                    line = line.strip()
                    if not line:
                        continue

                    # Σπάμε τη γραμμή στο σύμβολο '|'
                    parts = line.split(" | ")
                    
                    # Παίρνουμε τον αριθμό λογαριασμού (π.χ. 'Account #101' -> '101')
                    acc_num = parts[0].split("#")[1]
                    
                    # Παίρνουμε το όνομα (π.χ. 'Owner: Anna' -> 'Anna')
                    owner = parts[1].split(": ")[1]
                    
                    # Παίρνουμε το υπόλοιπο (π.χ. 'Balance: 600.00€' -> '600.00')
                    raw_balance = parts[2].split(": ")[1].replace("€", "")
                    balance = float(raw_balance)

                    # Ξαναφτιάχνουμε το αντικείμενο BankAccount
                    loaded_acc = BankAccount(acc_num, owner, balance)
                    self.accounts[acc_num] = loaded_acc

            print("Τα δεδομένα φορτώθηκαν επιτυχώς από το αρχείο!")
        except FileNotFoundError:
            print("Δεν βρέθηκε προηγούμενο αρχείο δεδομένων. Ξεκινάμε με άδεια τράπεζα.")


# --- ΔΙΑΔΡΑΣΤΙΚΟ ΜΕΝΟΥ ΧΡΗΣΤΗ ---

my_bank = Bank("Python National Bank")
# Φορτώνουμε αυτόματα τα υπάρχοντα δεδομένα κατά την εκκίνηση
my_bank.load_from_file()

while True:
    print("\n==============================")
    print("  PYTHON NATIONAL BANK MENU  ")
    print("==============================")
    print("1. Άνοιγμα Νέου Λογαριασμού")
    print("2. Προβολή Όλων των Λογαριασμών")
    print("3. Κατάθεση Χρημάτων")
    print("4. Αποθήκευση & Έξοδος")
    
    choice = input("\nΕπιλέξτε μια ενέργεια (1-4): ")

    if choice == "1":
        acc_num = input("Δώστε αριθμό λογαριασμού (π.χ. 103): ")
        name = input("Δώστε όνομα κατόχου: ")
        amount = float(input("Δώστε αρχική κατάθεση (€): "))
        my_bank.open_account(acc_num, name, amount)

    elif choice == "2":
        print("\n--- ΛΙΣΤΑ ΛΟΓΑΡΙΑΣΜΩΝ ---")
        if not my_bank.accounts:
            print("Δεν υπάρχουν εγγεγραμμένοι λογαριασμοί.")
        else:
            for acc in my_bank.accounts.values():
                print(acc)

    elif choice == "3":
        acc_num = input("Δώστε τον αριθμό λογαριασμού: ")
        acc = my_bank.get_account(acc_num)
        if acc:
            amount = float(input("Ποσό κατάθεσης (€): "))
            acc.deposit(amount)
        else:
            print("Ο λογαριασμός δεν βρέθηκε!")

    elif choice == "4":
        # Αποθηκεύουμε τις αλλαγές πριν κλείσει το πρόγραμμα
        my_bank.save_to_file()
        print("Ευχαριστούμε που χρησιμοποιήσατε την τράπεζά μας. Αντίο!")
        break  # Σταματάει το while loop και τερματίζει το πρόγραμμα

    else:
        print("Μη έγκυρη επιλογή! Παρακαλώ πληκτρολογήστε 1, 2, 3 ή 4.")