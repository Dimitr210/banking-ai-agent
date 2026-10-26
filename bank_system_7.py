import json
from datetime import datetime
from google import genai

# =====================================================================
# 🔑 ΡΥΘΜΙΣΗ API KEY GOOGLE GEMINI
# =====================================================================
GEMINI_API_KEY = "AQ.Ab8RN6KISQTiwHX2pCe_dpjgJVLc2mrXmgWdDWoGt2XddUmCSg"

  # <--- Βάλε εδώ το API Key σου!

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    client = None


class BankAccount:
    def __init__(self, account_number, owner_name, balance=0.0, history=None):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = balance
        self.history = history if history is not None else []

    def add_transaction(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = f"[{timestamp}] {message}"
        self.history.append(record)

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.add_transaction(f"Κατάθεση: +{amount:.2f}€")
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
            self.add_transaction(f"Ανάληψη: -{amount:.2f}€")
            print(f"Ανάληψη {amount:.2f}€ επιτυχής.")
            return True

    def show_history(self):
        print(f"\n--- ΙΣΤΟΡΙΚΟ ΣΥΝΑΛΛΑΓΩΝ: {self.owner_name} (#{self.account_number}) ---")
        if not self.history:
            print("Δεν υπάρχουν καταγεγραμμένες συναλλαγές.")
        else:
            for record in self.history:
                print(record)

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "owner_name": self.owner_name,
            "balance": self.balance,
            "history": self.history
        }

    def __str__(self):
        return f"Account #{self.account_number} | Owner: {self.owner_name} | Balance: {self.balance:.2f}€"


class RealBankAIModule:
    """Ο AI Βοηθός που συνδέεται με το Gemini API, με αυτόματο Fallback σε τοπική ανάλυση!"""
    def __init__(self, bank):
        self.bank = bank

    def _local_fallback(self, question):
        """Τοπικός AI Βοηθός αν το API δεν είναι διαθέσιμο."""
        question = question.lower().strip()
        accounts_list = list(self.bank.accounts.values())

        if not accounts_list:
            return "🤖 Local AI: Δεν υπάρχουν ακόμα λογαριασμοί στην τράπεζα για να αναλύσω!"

        if "συνολικ" in question or "όλα" in question or "ταμείο" in question or "total" in question:
            total = sum(acc.balance for acc in accounts_list)
            return f"🤖 Local AI: Το συνολικό υπόλοιπο όλων των λογαριασμών είναι {total:.2f}€."

        elif "πλουσιότερ" in question or "μεγαλύτερ" in question or "max" in question or "top" in question:
            top_acc = max(accounts_list, key=lambda acc: acc.balance)
            return f"🤖 Local AI: Ο πελάτης με το μεγαλύτερο υπόλοιπο είναι ο/η {top_acc.owner_name} με {top_acc.balance:.2f}€!"

        elif "μέσος" in question or "μέσο" in question or "average" in question:
            total = sum(acc.balance for acc in accounts_list)
            avg = total / len(accounts_list)
            return f"🤖 Local AI: Ο μέσος όρος καταθέσεων ανά λογαριασμό είναι {avg:.2f}€."

        elif "πόσοι" in question or "πλήθος" in question or "αριθμός" in question or "count" in question:
            return f"🤖 Local AI: Αυτή τη στιγμή υπάρχουν {len(accounts_list)} ενεργοί λογαριασμοί στην τράπεζα."

        else:
            return ("🤖 Local AI: (Offline Mode) Μπορείτε να με ρωτήσετε για:\n"
                    "  - Το συνολικό υπόλοιπο της τράπεζας\n"
                    "  - Τον πλουσιότερο πελάτη\n"
                    "  - Τον μέσο όρο καταθέσεων\n"
                    "  - Τον συνολικό αριθμό λογαριασμών")

    def ask(self, question):
        if not client:
            return self._local_fallback(question)

        bank_data = [acc.to_dict() for acc in self.bank.accounts.values()]
        
        prompt = f"""
        Είσαι ο έξυπνος AI Βοηθός της τράπεζας 'Python National Bank'.
        Έχεις πρόσβαση στα παρακάτω ζωντανά δεδομένα των λογαριασμών της τράπεζας σε μορφή JSON:
        
        {json.dumps(bank_data, ensure_ascii=False, indent=2)}

        Ο χρήστης σου κάνει την εξής ερώτηση: "{question}"

        Παρακαλώ απάντησε φιλικά, επαγγελματικά και με ακρίβεια στα ελληνικά, χρησιμοποιώντας τα παραπάνω δεδομένα.
        """

        # Δοκιμή με το Gemini API
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return f"\n🤖 Gemini AI: {response.text}"
        except Exception:
            # Αν αποτύχει το API, καλεί αυτόματα τον τοπικό AI βοηθό!
            print("\n[⚠️ Ειδοποίηση System: Το Gemini API δεν ανταποκρίθηκε. Ενεργοποίηση Local AI Module...]")
            return self._local_fallback(question)
class Bank:
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.accounts = {}
        self.ai_assistant = RealBankAIModule(self)

    def open_account(self, account_number, owner_name, initial_balance):
        new_account = BankAccount(account_number, owner_name, initial_balance)
        new_account.add_transaction(f"Άνοιγμα λογαριασμού με αρχικό ποσό: {initial_balance:.2f}€")
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
            from_acc.add_transaction(f"Μεταφορά προς #{to_acc_num} ({to_acc.owner_name}): -{amount:.2f}€")
            to_acc.add_transaction(f"Μεταφορά από #{from_acc_num} ({from_acc.owner_name}): +{amount:.2f}€")
            print("Η μεταφορά ολοκληρώθηκε με επιτυχία!")

    def save_to_file(self, filename="bank_data.json"):
        data_to_save = {
            acc_num: acc.to_dict() for acc_num, acc in self.accounts.items()
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, ensure_ascii=False, indent=4)
        print("Όλα τα δεδομένα αποθηκεύτηκαν επιτυχώς σε μορφή JSON!")

    def load_from_file(self, filename="bank_data.json"):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data_loaded = json.load(file)
                for acc_num, acc_info in data_loaded.items():
                    loaded_acc = BankAccount(
                        acc_info["account_number"],
                        acc_info["owner_name"],
                        acc_info["balance"],
                        acc_info.get("history", [])
                    )
                    self.accounts[acc_num] = loaded_acc
            print("Τα δεδομένα φορτώθηκαν επιτυχώς από το αρχείο JSON!")
        except FileNotFoundError:
            print("Δεν βρέθηκε προηγούμενο αρχείο JSON. Ξεκινάμε με νέα βάση.")


# --- ΔΙΑΔΡΑΣΤΙΚΟ ΜΕΝΟΥ ΧΡΗΣΤΗ ---

my_bank = Bank("Python National Bank")
my_bank.load_from_file()

while True:
    print("\n==============================")
    print("  PYTHON NATIONAL BANK MENU  ")
    print("==============================")
    print("1. Άνοιγμα Νέου Λογαριασμού")
    print("2. Προβολή Όλων των Λογαριασμών")
    print("3. Προβολή Ιστορικού Συναλλαγών")
    print("4. Κατάθεση Χρημάτων")
    print("5. Ανάληψη Χρημάτων")
    print("6. Μεταφορά Χρημάτων")
    print("7. 🤖 Real Gemini AI Assistant")
    print("8. Αποθήκευση & Έξοδος")

    choice = input("\nΕπιλέξτε μια ενέργεια (1-8): ")

    if choice == "1":
        acc_num = input("Αριθμός λογαριασμού (π.χ. 103): ")
        name = input("Όνομα κατόχου: ")
        try:
            amount = float(input("Αρχική κατάθεση (€): "))
            my_bank.open_account(acc_num, name, amount)
        except ValueError:
            print("Σφάλμα: Παρακαλώ εισάγετε έγκυρο αριθμό!")

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
            acc.show_history()
        else:
            print("Ο λογαριασμός δεν βρέθηκε!")

    elif choice == "4":
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

    elif choice == "5":
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

    elif choice == "6":
        from_num = input("Αριθμός λογαριασμού αποστολέα: ")
        to_num = input("Αριθμός λογαριασμού παραλήπτη: ")
        try:
            amount = float(input("Ποσό μεταφοράς (€): "))
            my_bank.transfer(from_num, to_num, amount)
        except ValueError:
            print("Σφάλμα: Παρακαλώ εισάγετε έγκυρο αριθμό!")

    elif choice == "7":
        print("\n--- 🤖 REAL GEMINI AI ASSISTANT ---")
        user_query = input("Ρωτήστε το Gemini AI οτιδήποτε για την τράπεζα: ")
        response = my_bank.ai_assistant.ask(user_query)
        print(response)

    elif choice == "8":
        my_bank.save_to_file()
        print("Ευχαριστούμε που χρησιμοποιήσατε την τράπεζά μας. Αντίο!")
        break

    else:
        print("Μη έγκυρη επιλογή! Παρακαλώ πληκτρολογήστε από 1 έως 8.")