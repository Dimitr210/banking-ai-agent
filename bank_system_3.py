class BankAccount:
    def __init__(self, account_number, owner_name, balance=0.0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"Κατάθεση {amount:.2f}€ επιτυχής.")
            return True
        print("Το ποσό πρέπει να είναι θετικό.")
        return False

    def withdraw(self, amount):
        if amount > self.balance:
            print("Ανεπαρκές υπόλοιπο (Insufficient funds)!")
            return False
        elif amount <= 0:
            print("Το ποσό ανάληψης πρέπει να είναι θετικό.")
            return False
        else:
            self.balance -= amount
            print(f"Ανάληψη {amount:.2f}€ επιτυχής.")
            return True

    def __str__(self):
        return f"Account #{self.account_number} | Owner: {self.owner_name} | Balance: {self.balance:.2f}€"


class Bank:
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.accounts = {}

    def open_account(self, account_number, owner_name, initial_balance):
        new_account = BankAccount(account_number, owner_name, initial_balance)
        self.accounts[account_number] = new_account
        print(f"Ο λογαριασμός #{account_number} δημιουργήθηκε!")

    def get_account(self, account_number):
        return self.accounts.get(account_number)

    def transfer(self, from_acc_num, to_acc_num, amount):
        from_acc = self.get_account(from_acc_num)
        to_acc = self.get_account(to_acc_num)

        if not from_acc or not to_acc:
            print("Ένας ή και οι δύο λογαριασμοί δεν βρέθηκαν.")
            return

        print(f"\n--- Μεταφορά {amount:.2f}€ από {from_acc.owner_name} σε {to_acc.owner_name} ---")
        if from_acc.withdraw(amount):
            to_acc.deposit(amount)
            print("Η μεταφορά ολοκληρώθηκε με επιτυχία!")

    def save_to_file(self, filename="bank_data.txt"):
        with open(filename, "w") as file:
            for account in self.accounts.values():
                file.write(f"{account}\n")
        print("Όλα τα δεδομένα αποθηκεύτηκαν στο αρχείο!")

    def load_from_file(self, filename="bank_data.txt"):
        try:
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(" | ")
                    acc_num = parts[0].split("#")[1]
                    owner = parts[1].split(": ")[1]
                    raw_balance = parts[2].split(": ")[1].replace("€", "")
                    balance = float(raw_balance)

                    loaded_acc = BankAccount(acc_num, owner, balance)
                    self.accounts[acc_num] = loaded_acc

            print("Τα δεδομένα φορτώθηκαν επιτυχώς από το αρχείο!")
        except FileNotFoundError:
            print("Δεν βρέθηκε προηγούμενο αρχείο δεδομένων.")


# --- ΔΙΑΔΡΑΣΤΙΚΟ ΜΕΝΟΥ ΧΡΗΣΤΗ ΜΕ ERROR HANDLING ---

my_bank = Bank("Python National Bank")
my_bank.load_from_file()

while True:
    print("\n==============================")
    print("  PYTHON NATIONAL BANK MENU  ")
    print("==============================")
    print("1. Άνοιγμα Νέου Λογαριασμού")
    print("2. Προβολή Όλων των Λογαριασμών")
    print("3. Κατάθεση Χρημάτων")
    print("4. Ανάληψη Χρημάτων")
    print("5. Μεταφορά Χρημάτων")
    print("6. Αποθήκευση & Έξοδος")

    choice = input("\nΕπιλέξτε μια ενέργεια (1-6): ")

    if choice == "1":
        acc_num = input("Αριθμός λογαριασμού (π.χ. 103): ")
        name = input("Όνομα κατόχου: ")
        
        # Προστασία από λάθος είσοδο στο ποσό
        try:
            amount = float(input("Αρχική κατάθεση (€): "))
            my_bank.open_account(acc_num, name, amount)
        except ValueError:
            print("Σφάλμα: Παρακαλώ εισάγετε έγκυρο αριθμό για το ποσό!")

    elif choice == "2":
        print("\n--- ΛΙΣΤΑ ΛΟΓΑΡΙΑΣΜΩΝ ---")
        if not my_bank.accounts:
            print("Δεν υπάρχουν εγγεγραμμένοι λογαριασμοί.")
        else:
            for acc in my_bank.accounts.values():
                print(acc)

    elif choice == "3":
        acc_num = input("Αριθμός λογαριασμού: ")
        acc = my_bank.get_account(acc_num)
        if acc:
            try:
                amount = float(input("Ποσό κατάθεσης (€): "))
                acc.deposit(amount)
            except ValueError:
                print("Σφάλμα: Παρακαλώ εισάγετε έγκυρο αριθμό!")
        else:
            print("Ο λογαριασμός δεν βρέθηκε!")

    elif choice == "4":
        acc_num = input("Αριθμός λογαριασμού: ")
        acc = my_bank.get_account(acc_num)
        if acc:
            try:
                amount = float(input("Ποσό ανάληψης (€): "))
                acc.withdraw(amount)
            except ValueError:
                print("Σφάλμα: Παρακαλώ εισάγετε έγκυρο αριθμό!")
        else:
            print("Ο λογαριασμός δεν βρέθηκε!")

    elif choice == "5":
        from_num = input("Αριθμός λογαριασμού αποστολέα: ")
        to_num = input("Αριθμός λογαριασμού παραλήπτη: ")
        try:
            amount = float(input("Ποσό μεταφοράς (€): "))
            my_bank.transfer(from_num, to_num, amount)
        except ValueError:
            print("Σφάλμα: Παρακαλώ εισάγετε έγκυρο αριθμό!")

    elif choice == "6":
        my_bank.save_to_file()
        print("Ευχαριστούμε που χρησιμοποιήσατε την τράπεζά μας. Αντίο!")
        break

    else:
        print("Μη έγκυρη επιλογή! Παρακαλώ πληκτρολογήστε από 1 έως 6.")