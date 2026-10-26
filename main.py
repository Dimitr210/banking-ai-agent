import os
import sys
import io

# 🔧 ΕΠΙΒΟΛΗ UTF-8 ENCODING ΣΤΟ TERMINAL
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# =====================================================================
# 🔑 GEMINI API KEY CONFIGURATION (ΝΕΟ SDK google-genai)
# =====================================================================
GEMINI_API_KEY = "AQ.Ab8RN6K0igY-8yJJbEPxOeZcJXdfr4k6g_6vGqd9m-VXyIn7jg"  # <--- Βάλε το νέο σου API Key!

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("✅ Ο νέος Gemini Client (google-genai) αρχικοποιήθηκε επιτυχώς!")
except Exception as e:
    print(f"❌ Σφάλμα Αρχικοποίησης Client: {e}")
    client = None

app = FastAPI(title="Python National Bank API with Agentic Tools")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 🏛️ PYTHON BANK CLASSES
# =====================================================================
class BankAccount:
    def __init__(self, account_number, owner_name, balance=0.0, history=None):
        self.account_number = str(account_number)
        self.owner_name = owner_name
        self.balance = float(balance)
        self.history = history if history is not None else []

    def add_transaction(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"[{timestamp}] {message}")

    def deposit(self, amount: float):
        if amount > 0:
            self.balance += amount
            self.add_transaction(f"Κατάθεση: +{amount:.2f}€")
            return True
        return False

    def withdraw(self, amount: float):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.add_transaction(f"Ανάληψη: -{amount:.2f}€")
            return True
        return False

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "owner_name": self.owner_name,
            "balance": self.balance,
            "history": self.history
        }

class Bank:
    def __init__(self):
        self.accounts = {}
        self.load_from_file()

    def load_from_file(self, filename="bank_data.json"):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                for acc_num, acc_info in data.items():
                    self.accounts[str(acc_num)] = BankAccount(
                        acc_info["account_number"],
                        acc_info["owner_name"],
                        acc_info["balance"],
                        acc_info.get("history", [])
                    )
        except FileNotFoundError:
            self.accounts["101"] = BankAccount("101", "Γιάννης Παπαδόπουλος", 1250.00)
            self.accounts["102"] = BankAccount("102", "Μαρία Δημητρίου", 796.00)
            self.save_to_file()

    def save_to_file(self, filename="bank_data.json"):
        data = {acc_num: acc.to_dict() for acc_num, acc in self.accounts.items()}
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def transfer(self, from_acc_num: str, to_acc_num: str, amount: float):
        from_acc = self.accounts.get(str(from_acc_num))
        to_acc = self.accounts.get(str(to_acc_num))

        if not from_acc or not to_acc:
            return {"status": "error", "message": "Ένας από τους λογαριασμούς δεν βρέθηκε."}

        if from_acc.withdraw(amount):
            to_acc.deposit(amount)
            from_acc.add_transaction(f"Μεταφορά προς #{to_acc_num}: -{amount:.2f}€")
            to_acc.add_transaction(f"Μεταφορά από #{from_acc_num}: +{amount:.2f}€")
            self.save_to_file()
            return {"status": "success", "message": f"Μεταφέρθηκαν {amount:.2f}€ από #{from_acc_num} σε #{to_acc_num}."}
        
        return {"status": "error", "message": "Ανεπαρκές υπόλοιπο για τη μεταφορά."}

bank = Bank()
sessions_memory = {}
analytics_logs = []
SESSIONS_FILE = "sessions_db.json"

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [WARN] Σφάλμα ανάγνωσης sessions_db.json: {e}")
    return {}

def save_sessions():
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions_memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ [WARN] Σφάλμα αποθήκευσης sessions_db.json: {e}")

# Φόρτωση μνήμης κατά την εκκίνηση
sessions_memory = load_sessions()
# =====================================================================
# 🛠️ GEMINI TOOLS DEFINITION
# =====================================================================

def tool_deposit(account_number: str, amount: float) -> str:
    """Κατάθεση χρημάτων σε έναν λογαριασμό."""
    acc = bank.accounts.get(str(account_number))
    if not acc:
        return f"Σφάλμα: Ο λογαριασμός #{account_number} δεν υπάρχει."
    if acc.deposit(float(amount)):
        bank.save_to_file()
        return f"Επιτυχία: Κατάθεση {amount:.2f}€ στον λογαριασμό #{account_number}. Νέο υπόλοιπο: {acc.balance:.2f}€."
    return "Σφάλμα: Μη έγκυρο ποσό."

def tool_withdraw(account_number: str, amount: float) -> str:
    """Ανάληψη χρημάτων από έναν λογαριασμό."""
    acc = bank.accounts.get(str(account_number))
    if not acc:
        return f"Σφάλμα: Ο λογαριασμός #{account_number} δεν υπάρχει."
    if acc.withdraw(float(amount)):
        bank.save_to_file()
        return f"Επιτυχία: Ανάληψη {amount:.2f}€ από τον λογαριασμό #{account_number}. Νέο υπόλοιπο: {acc.balance:.2f}€."
    return "Σφάλμα: Ανεπαρκές υπόλοιπο."

def tool_transfer(from_account: str, to_account: str, amount: float) -> str:
    """Μεταφορά χρημάτων μεταξύ δύο λογαριασμών."""
    res = bank.transfer(str(from_account), str(to_account), float(amount))
    return res["message"]

# =====================================================================
# 🌐 REST API ENDPOINTS
# =====================================================================

class TransactionRequest(BaseModel):
    account_number: str
    amount: float

class AIQueryRequest(BaseModel):
    question: str
    session_id: str = "default_session"

@app.get("/accounts")
def get_accounts():
    return [acc.to_dict() for acc in bank.accounts.values()]

@app.post("/deposit")
def deposit_money(req: TransactionRequest):
    acc = bank.accounts.get(str(req.account_number))
    if not acc:
        raise HTTPException(status_code=404, detail="Ο λογαριασμός δεν βρέθηκε")
    if acc.deposit(req.amount):
        bank.save_to_file()
        return {"message": "Η κατάθεση ολοκληρώθηκε", "account": acc.to_dict()}
    raise HTTPException(status_code=400, detail="Μη έγκυρο ποσό")

@app.post("/withdraw")
def withdraw_money(req: TransactionRequest):
    acc = bank.accounts.get(str(req.account_number))
    if not acc:
        raise HTTPException(status_code=404, detail="Ο λογαριασμός δεν βρέθηκε")
    if acc.withdraw(req.amount):
        bank.save_to_file()
        return {"message": "Η ανάληψη ολοκληρώθηκε", "account": acc.to_dict()}
    raise HTTPException(status_code=400, detail="Ανεπαρκές υπόλοιπο")

import re

@app.post("/ai-ask")
def ai_ask(req: AIQueryRequest):
    bank_data = [acc.to_dict() for acc in bank.accounts.values()]
    q = req.question.strip()
    q_lower = q.lower()
    session_id = req.session_id

    print(f"\n[DEBUG] 📩 Νέα ερώτηση ({session_id}): {q}")

    if session_id not in sessions_memory:
        sessions_memory[session_id] = []

    history = sessions_memory[session_id]

    # 1. FAST-PATH (Άμεση εκτέλεση)
    if "μετάφερε" in q_lower or "μεταφορα" in q_lower or "στείλε" in q_lower or "στειλε" in q_lower:
        numbers = re.findall(r'\d+', q)
        if len(numbers) >= 3:
            amount = float(numbers[0])
            from_acc = numbers[1]
            to_acc = numbers[2]

            print(f"[DEBUG] ⚡ Fast-Path μεταφορά: {amount}€ από #{from_acc} σε #{to_acc}")
            result = tool_transfer(from_acc, to_acc, amount)
            
            history.append({"role": "user", "parts": [{"text": q}]})
            history.append({"role": "model", "parts": [{"text": result}]})
            save_sessions()
            
            return {
                "answer": f"🤖 Gemini Agent (Fast-Path): {result}",
                "session_id": session_id
            }

    # 2. GEMINI API CALL (Με Pruning & Persistence)
    if client:
        user_message = f"Ζωντανά δεδομένα τράπεζας: {json.dumps(bank_data, ensure_ascii=False)}\nΕρώτηση: {q}"
        current_user_part = {"role": "user", "parts": [{"text": user_message}]}
        
        history.append(current_user_part)

        # ✂️ CONTEXT PRUNING: Κρατάμε μόνο τα τελευταία 6 μηνύματα για έλεγχο κόστους/latency
        max_history_length = 6
        trimmed_history = history[-max_history_length:]

        try:
            start_time = time.time()

            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=trimmed_history
            )

            latency = round(time.time() - start_time, 3)
            model_reply = response.text

            history.append({"role": "model", "parts": [{"text": model_reply}]})
            
            # 💾 Αποθήκευση της μνήμης στο αρχείο JSON
            save_sessions()

            usage = response.usage_metadata
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id,
                "latency_sec": latency,
                "prompt_tokens": usage.prompt_token_count if usage else 0,
                "candidate_tokens": usage.candidates_token_count if usage else 0,
                "total_tokens": usage.total_token_count if usage else 0
            }
            analytics_logs.append(log_entry)

            print(f"[ANALYTICS] Latency: {latency}s | Tokens: {log_entry['total_tokens']}")

            return {
                "answer": model_reply,
                "session_id": session_id,
                "metrics": log_entry
            }

        except Exception as e:
            print(f"⚠️ [ERROR] Gemini Call Failed: {e}")
            if history and history[-1] == current_user_part:
                history.pop()

            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return {
                    "answer": "⚠️ Το Gemini API είναι προσωρινά επιβαρυμένο. Παρακαλώ περίμενε λίγα δευτερόλεπτα.",
                    "session_id": session_id
                }

    return {"answer": f"🤖 Local AI: Η τράπεζα διαθέτει {len(bank.accounts)} λογαριασμούς."}