# Password Manager
# Author: Kunal Dharme (with enhancements)

from cryptography.fernet import Fernet
import os
import getpass
import pyfiglet
from termcolor import colored
from colorama import Fore, init
import time, sys, re
import json
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition

init(autoreset=True)

PASSWORD_FILE = "passwords.enc"
KEY_FILE = "secret.key"
MASTER_PASSWORD_FILE = "master_password.enc"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as file:
        file.write(key)
    print(Fore.GREEN + "Encryption key generated and saved.")

def load_key():
    if not os.path.exists(KEY_FILE):
        print(Fore.LIGHTRED_EX + "[!] Key file not found. Generating a new one...")
        generate_key()
    with open(KEY_FILE, "rb") as file:
        return file.read()

def encrypt_password(password, fernet):
    return fernet.encrypt(password.encode())

def decrypt_password(encrypted_password, fernet):
    return fernet.decrypt(encrypted_password).decode()

def save_passwords(data):
    with open(PASSWORD_FILE, "wb") as file:
        file.write(data)

def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        return {}
    with open(PASSWORD_FILE, "rb") as file:
        return file.read()

def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Include at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Include at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Include at least one number."
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Include at least one special character."
    return True, "Strong password."

def setup_master_password(fernet):
    print(Fore.CYAN + "Setting up a master password for the first time.\n")
    while True:
        print(Fore.RED + "Password must be 8+ chars with uppercase, lowercase, number & special symbol (!@#$...)")
        master_password = getpass.getpass(Fore.GREEN + "Enter a new master password: ")
        confirm_password = getpass.getpass(Fore.GREEN + "Confirm master password: ")
        if master_password != confirm_password:
            print(Fore.RED + "Passwords do not match. Try again.")
            continue
        strong, message = is_strong_password(master_password)
        if not strong:
            print(Fore.RED + f"Weak password: {message}")
            continue
        encrypted_master = encrypt_password(master_password, fernet)
        with open(MASTER_PASSWORD_FILE, "wb") as file:
            file.write(encrypted_master)
        print(Fore.GREEN + "[✓] Master password set successfully!\n")
        break

def verify_master_password(fernet):
    if not os.path.exists(MASTER_PASSWORD_FILE):
        setup_master_password(fernet)

    with open(MASTER_PASSWORD_FILE, "rb") as file:
        encrypted_master = file.read()
    stored_master_password = decrypt_password(encrypted_master, fernet)

    max_attempts = 3
    cooldown_time = 10
    max_cooldowns = 3  # Exit after 3 cooldown rounds
    cooldown_count = 0
    attempts = max_attempts

    while cooldown_count < max_cooldowns:
        while attempts > 0:
            entered_password = getpass.getpass(Fore.YELLOW + "Enter the master password: ")
            if entered_password == stored_master_password:
                print(Fore.GREEN + "[✓] Access granted! Welcome to the Password Manager.\n")
                print(colored(pyfiglet.figlet_format("P A S S W O R D   M A N A G E R", font="mini"), "cyan"))
                return True
            else:
                attempts -= 1
                print(Fore.RED + f"[X] Incorrect password. Attempts remaining: {attempts}")

        # Cooldown triggered
        cooldown_count += 1
        print(Fore.LIGHTRED_EX + f"[!] Too many failed attempts. Cooldown for {cooldown_time} seconds.")
        for remaining in range(cooldown_time, 0, -1):
            sys.stdout.write(Fore.LIGHTRED_EX + f"\r[!] Cooldown: {remaining} seconds remaining... ")
            sys.stdout.flush()
            time.sleep(1)
        print()

        cooldown_time *= 2  # Double the cooldown duration
        attempts = max_attempts  # Reset attempts

    # Exceeded max cooldowns
    print(Fore.LIGHTRED_EX + "[!] Maximum retries and cooldowns reached. Exiting program.")
    return False

def type_effect(text, delay=0.04):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def display_menu():
    print(Fore.LIGHTWHITE_EX + "\n >_ Enter Your Choice")
    print(Fore.BLUE + "1. Add a new Account, ID, and password")
    print(Fore.BLUE + "2. Retrieve a password")
    print(Fore.BLUE + "3. Delete an entry")
    print(Fore.BLUE + "4. View all stored Accounts and IDs")
    print(Fore.LIGHTBLUE_EX + "5. Edit an existing password")  
    print(Fore.RED + "6. Exit")  

def get_masked_input(prompt_text):
    show_password = [False]
    bindings = KeyBindings()

    @bindings.add('c-t')
    def _(event):
        show_password[0] = not show_password[0]

    return prompt(prompt_text,
                  is_password=Condition(lambda: not show_password[0]),
                  key_bindings=bindings)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    type_effect("\n - Welcome to the Password Manager. This script provides a secure way to store and retrieve passwords using encryption.\n", delay=0.05)

    key = load_key()
    fernet = Fernet(key)

    if not verify_master_password(fernet):
        return

    encrypted_data = load_passwords()
    passwords = {}
    if encrypted_data:
        try:
            passwords = json.loads(decrypt_password(encrypted_data, fernet))
        except:
            passwords = {}

    while True:
        display_menu()
        choice = input(Fore.YELLOW + "Enter your choice: ")

        if choice == '1':
            account = input(Fore.GREEN + "Enter Account Name: ")
            user_id = input(Fore.GREEN + "Enter ID: ")
            print(Fore.YELLOW + "(Press Ctrl+t to toggle password visibility)")
            print(Fore.GREEN + "Enter Password:")
            password = get_masked_input("> ")
            if account not in passwords:
                passwords[account] = {}
            passwords[account][user_id] = encrypt_password(password, fernet)
            print(Fore.GREEN + "Password added successfully!")

        elif choice == '2':
            print(Fore.CYAN + "\nSelect an Account by Serial Number:")
            accounts = list(passwords.keys())
            for i, account in enumerate(accounts, 1):
                print(Fore.MAGENTA + f"{i}. {account}")
            try:
                selection = int(input(Fore.YELLOW + "Enter Serial Number: "))
                if 1 <= selection <= len(accounts):
                    selected_account = accounts[selection - 1]
                    confirm = input(Fore.YELLOW + f"\nReveal passwords for {selected_account}? (yes/no): ").strip().lower()
                    if confirm in ["yes", "y"]:
                        for user_id, enc_password in passwords[selected_account].items():
                            try:
                                decrypted_password = decrypt_password(enc_password, fernet)
                                print(Fore.GREEN + f"ID: {user_id} | Password: {decrypted_password}")
                            except:
                                print(Fore.RED + f"ID: {user_id} | Error decrypting password!")
                    else:
                        print(Fore.RED + "Cancelled. Passwords not displayed.")
                else:
                    print(Fore.RED + "Invalid selection.")
            except ValueError:
                print(Fore.RED + "Invalid input.")

        elif choice == '3':
            account = input(Fore.RED + "Enter Account Name to delete an entry: ")
            if account in passwords:
                user_id = input(Fore.RED + "Enter ID to delete: ")
                if user_id in passwords[account]:
                    del passwords[account][user_id]
                    if not passwords[account]:
                        del passwords[account]
                    print(Fore.GREEN + "Entry deleted successfully!")
                else:
                    print(Fore.RED + "ID not found.")
            else:
                print(Fore.RED + "Account not found.")

        elif choice == '4':
            print(Fore.CYAN + "\nStored Accounts and IDs:")
            for account, ids in passwords.items():
                print(Fore.MAGENTA + f"Account: {account}")
                for user_id in ids.keys():
                    print(Fore.YELLOW + f"  - ID: {user_id}")

        elif choice == '5':
            account = input(Fore.CYAN + "Enter Account Name to edit: ")
            if account in passwords:
                user_id = input(Fore.CYAN + "Enter ID to update password: ")
                if user_id in passwords[account]:
                    print(Fore.YELLOW + "(Press Ctrl+t to toggle password visibility)")
                    print(Fore.GREEN + "Enter New Password:")
                    new_password = get_masked_input("> ")
                    passwords[account][user_id] = encrypt_password(new_password, fernet)
                    print(Fore.GREEN + "[✓] Password updated successfully.")
                else:
                    print(Fore.RED + "ID not found.")
            else:
                print(Fore.RED + "Account not found.")

        elif choice == '6':
            serializable_passwords = {
                account: {uid: (enc_pw if isinstance(enc_pw, str) else enc_pw.decode())
                        for uid, enc_pw in ids.items()}
                for account, ids in passwords.items()
            }
            json_data = json.dumps(serializable_passwords)
            encrypted_data = encrypt_password(json_data, fernet)
            save_passwords(encrypted_data)

            print(Fore.GREEN + "Data saved. Goodbye!")
            break


        else:
            print(Fore.RED + "Invalid choice. Try again.")

if __name__ == "__main__":
    main()
