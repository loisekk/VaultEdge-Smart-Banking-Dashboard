from pathlib import Path
import json
import random
import string


class Bank:
    DATABASE = "data.json"
    data = []

    # Load existing data on startup
    try:
        if Path(DATABASE).exists():
            with open(DATABASE, 'r') as f:
                data = json.load(f)
        else:
            print("No existing database found. Starting fresh.")
    except Exception as e:
        print(f"Error loading database: {e}")

    @classmethod
    def save(cls):
        """Save all data to the JSON file."""
        with open(cls.DATABASE, 'w') as f:
            json.dump(cls.data, f, indent=4)

    @staticmethod
    def generate_account_no():
        """Generate a random 8-character account number (4 digits + 4 letters)."""
        digits = random.choices(string.digits, k=4)
        alpha = random.choices(string.ascii_uppercase, k=4)
        combined = digits + alpha
        random.shuffle(combined)
        return "".join(combined)

    @staticmethod
    def find_user(accountno, pin):
        """Find a user by account number and PIN. Returns user dict or None."""
        for user in Bank.data:
            if user["accountno"] == accountno and user["pin"] == int(pin):
                return user
        return None

    def create_account(self):
        """Create a new bank account."""
        print("\n--- Create New Account ---")
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return

        try:
            age = int(input("Enter your age: "))
            email = input("Enter your email address: ").strip()
            phone = input("Enter your 10-digit phone number: ").strip()
            pin = input("Enter a 4-digit PIN: ").strip()
        except ValueError:
            print("Invalid input. Please enter valid details.")
            return

        # Validate inputs
        if age < 18:
            print("You must be at least 18 years old to open an account.")
            return
        if len(phone) != 10 or not phone.isdigit():
            print("Phone number must be exactly 10 digits.")
            return
        if len(pin) != 4 or not pin.isdigit():
            print("PIN must be exactly 4 digits.")
            return

        account_no = Bank.generate_account_no()

        user_info = {
            "name": name,
            "age": age,
            "email": email,
            "phone": phone,
            "pin": int(pin),
            "accountno": account_no,
            "balance": 0
        }

        Bank.data.append(user_info)
        Bank.save()
        print(f"\nAccount created successfully!")
        print(f"Your Account Number: {account_no}  (save this safely)")

    def deposit(self):
        """Deposit money into an account."""
        print("\n--- Deposit Money ---")
        accountno = input("Enter your account number: ").strip()
        pin = input("Enter your 4-digit PIN: ").strip()

        user = Bank.find_user(accountno, pin)
        if not user:
            print("Invalid account number or PIN.")
            return

        try:
            amount = int(input("Enter amount to deposit (max ₹10,000 per transaction): "))
        except ValueError:
            print("Invalid amount.")
            return

        if amount <= 0:
            print("Amount must be greater than 0.")
        elif amount > 10000:
            print("Cannot deposit more than ₹10,000 in a single transaction.")
        else:
            user["balance"] += amount
            Bank.save()
            print(f"₹{amount} deposited successfully. New balance: ₹{user['balance']}")

    def withdraw(self):
        """Withdraw money from an account."""
        print("\n--- Withdraw Money ---")
        accountno = input("Enter your account number: ").strip()
        pin = input("Enter your 4-digit PIN: ").strip()

        user = Bank.find_user(accountno, pin)
        if not user:
            print("Invalid account number or PIN.")
            return

        try:
            amount = int(input("Enter amount to withdraw (max ₹10,000 per transaction): "))
        except ValueError:
            print("Invalid amount.")
            return

        if amount <= 0:
            print("Amount must be greater than 0.")
        elif amount > 10000:
            print("Cannot withdraw more than ₹10,000 in a single transaction.")
        elif user["balance"] < amount:
            print("Insufficient funds.")
        else:
            user["balance"] -= amount
            Bank.save()
            print(f"₹{amount} withdrawn successfully. Remaining balance: ₹{user['balance']}")

    def view_details(self):
        """View account details."""
        print("\n--- Account Details ---")
        accountno = input("Enter your account number: ").strip()
        pin = input("Enter your 4-digit PIN: ").strip()

        user = Bank.find_user(accountno, pin)
        if not user:
            print("Invalid account number or PIN.")
            return

        print("\n--- Your Account Information ---")
        print(f"  Name          : {user['name']}")
        print(f"  Age           : {user['age']}")
        print(f"  Email         : {user['email']}")
        print(f"  Phone         : {user['phone']}")
        print(f"  Account No.   : {user['accountno']}")
        print(f"  Balance       : ₹{user['balance']}")

    def update_details(self):
        """Update account details (except account number and balance)."""
        print("\n--- Update Account Details ---")
        accountno = input("Enter your account number: ").strip()
        pin = input("Enter your current 4-digit PIN: ").strip()

        user = Bank.find_user(accountno, pin)
        if not user:
            print("Invalid account number or PIN.")
            return

        print("Press Enter to keep the current value unchanged.")

        new_name = input(f"New name [{user['name']}]: ").strip()
        new_email = input(f"New email [{user['email']}]: ").strip()
        new_phone = input(f"New phone [{user['phone']}]: ").strip()
        new_pin = input("New 4-digit PIN (leave blank to keep current): ").strip()

        if new_name:
            user["name"] = new_name
        if new_email:
            user["email"] = new_email
        if new_phone:
            if len(new_phone) == 10 and new_phone.isdigit():
                user["phone"] = new_phone
            else:
                print("Invalid phone number. Phone not updated.")
        if new_pin:
            if len(new_pin) == 4 and new_pin.isdigit():
                user["pin"] = int(new_pin)
            else:
                print("Invalid PIN. PIN not updated.")

        Bank.save()
        print("Account updated successfully.")

    def delete_account(self):
        """Delete an account permanently."""
        print("\n--- Delete Account ---")
        accountno = input("Enter your account number: ").strip()
        pin = input("Enter your 4-digit PIN: ").strip()

        user = Bank.find_user(accountno, pin)
        if not user:
            print("Invalid account number or PIN.")
            return

        confirm = input(f"Are you sure you want to delete account {accountno}? (yes/no): ").strip().lower()
        if confirm == "yes":
            Bank.data.remove(user)
            Bank.save()
            print("Account deleted successfully.")
        else:
            print("Operation cancelled.")


# ─────────────────────────────────────────
#  Main Menu
# ─────────────────────────────────────────

def main():
    obj = Bank()

    menu = """
╔══════════════════════════════╗
║        BANKING SYSTEM        ║
╠══════════════════════════════╣
║  1. Create Account           ║
║  2. Deposit Money            ║
║  3. Withdraw Money           ║
║  4. View Account Details     ║
║  5. Update Account Details   ║
║  6. Delete Account           ║
║  0. Exit                     ║
╚══════════════════════════════╝
"""

    actions = {
        1: obj.create_account,
        2: obj.deposit,
        3: obj.withdraw,
        4: obj.view_details,
        5: obj.update_details,
        6: obj.delete_account,
    }

    while True:
        print(menu)
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == 0:
            print("Thank you for using our Banking System. Goodbye!")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("Invalid choice. Please select from the menu.")


if __name__ == "__main__":
    main()
