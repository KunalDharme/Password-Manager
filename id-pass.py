#Password Manager
#Author : Kunal Dharme

from cryptography.fernet import Fernet
import os
from colorama import Fore, Style, init
import getpass

# Initialize colorama
init(autoreset=True)

# File to store encrypted passwords
PASSWORD_FILE = "passwords.enc"
KEY_FILE = "secret.key"
MASTER_PASSWORD_FILE = "master_password.enc"

def generate_key():
    """Generate a key for encryption and save it to a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as file:
        file.write(key)
    print(Fore.GREEN + "Encryption key generated and saved.")

def load_key():
    """Load the encryption key from the file."""
    if not os.path.exists(KEY_FILE):
        print(Fore.YELLOW + "Key file not found. Generating a new one...")
        generate_key()
    with open(KEY_FILE, "rb") as file:
        return file.read()

def encrypt_password(password, fernet):
    """Encrypt the given password."""
    return fernet.encrypt(password.encode())

def decrypt_password(encrypted_password, fernet):
    """Decrypt the given password."""
    return fernet.decrypt(encrypted_password).decode()

def save_passwords(data):
    """Save the encrypted data to the file."""
    with open(PASSWORD_FILE, "wb") as file:
        file.write(data)

def load_passwords():
    """Load the encrypted data from the file or return an empty dictionary."""
    if not os.path.exists(PASSWORD_FILE):
        return {}
    with open(PASSWORD_FILE, "rb") as file:
        return file.read()

def setup_master_password(fernet):
    """Set up and save the master password securely."""
    print(Fore.CYAN + "Setting up a master password for the first time.")
    while True:
        master_password = getpass.getpass(Fore.GREEN + "Enter a new master password: ")
        confirm_password = getpass.getpass(Fore.GREEN + "Confirm master password: ")
        if master_password == confirm_password:
            encrypted_master = encrypt_password(master_password, fernet)
            with open(MASTER_PASSWORD_FILE, "wb") as file:
                file.write(encrypted_master)
            print(Fore.GREEN + "Master password set successfully!")
            break
        else:
            print(Fore.RED + "Passwords do not match. Try again.")

def verify_master_password(fernet):
    """Verify the master password before accessing the manager."""
    if not os.path.exists(MASTER_PASSWORD_FILE):
        setup_master_password(fernet)
    with open(MASTER_PASSWORD_FILE, "rb") as file:
        encrypted_master = file.read()
    stored_master_password = decrypt_password(encrypted_master, fernet)

    attempts = 3
    while attempts > 0:
        entered_password = getpass.getpass(Fore.YELLOW + "Enter the master password: ")
        if entered_password == stored_master_password:
            print(Fore.GREEN + "Access granted! Welcome to the Password Manager.")
            return True
        else:
            attempts -= 1
            print(Fore.RED + f"Incorrect password. Attempts remaining: {attempts}")
    print(Fore.RED + "Too many failed attempts. Exiting program.")
    return False

def display_menu():
    """Display the options menu."""
    print(Fore.CYAN + "\n--- Password Manager ---")
    print(Fore.BLUE + "1. Add a new Account, ID, and password")
    print(Fore.BLUE + "2. Retrieve a password")
    print(Fore.BLUE + "3. Delete an entry")
    print(Fore.BLUE + "4. View all stored Accounts and IDs")
    print(Fore.RED + "5. Exit")

def main():
    # Load encryption key and initialize Fernet
    key = load_key()
    fernet = Fernet(key)

    # Verify master password
    if not verify_master_password(fernet):
        return

    # Load stored passwords
    encrypted_data = load_passwords()
    passwords = {}  # account: {id: encrypted_password}
    if encrypted_data:
        passwords = eval(decrypt_password(encrypted_data, fernet))

    while True:
        display_menu()
        choice = input(Fore.YELLOW + "Enter your choice: ")

        if choice == '1':
            # Add a new account, ID, and password
            account = input(Fore.GREEN + "Enter Account Name: ")
            user_id = input(Fore.GREEN + "Enter ID: ")
            password = input(Fore.GREEN + "Enter Password: ")
            if account not in passwords:
                passwords[account] = {}
            passwords[account][user_id] = encrypt_password(password, fernet)
            print(Fore.GREEN + "Password added successfully!")

        elif choice == '2':
            # Retrieve a password
            print(Fore.CYAN + "\nSelect an Account by Serial Number:")
            accounts = list(passwords.keys())
            for i, account in enumerate(accounts, 1):
                print(Fore.MAGENTA + f"{i}. {account}")
            try:
                selection = int(input(Fore.YELLOW + "Enter Serial Number: "))
                if 1 <= selection <= len(accounts):
                    selected_account = accounts[selection - 1]
                    print(Fore.CYAN + f"\nPasswords for {selected_account}:")
                    for user_id, enc_password in passwords[selected_account].items():
                        decrypted_password = decrypt_password(enc_password, fernet)
                        print(Fore.GREEN + f"ID: {user_id} | Password: {decrypted_password}")
                else:
                    print(Fore.RED + "Invalid selection. Try again.")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

        elif choice == '3':
            # Delete an entry
            account = input(Fore.RED + "Enter Account Name to delete an entry: ")
            if account in passwords:
                user_id = input(Fore.RED + "Enter ID to delete: ")
                if user_id in passwords[account]:
                    del passwords[account][user_id]
                    if not passwords[account]:
                        del passwords[account]  # Delete account if no IDs are left
                    print(Fore.GREEN + "Entry deleted successfully!")
                else:
                    print(Fore.RED + "ID not found under this account.")
            else:
                print(Fore.RED + "Account not found.")

        elif choice == '4':
            # View all stored Accounts and IDs
            print(Fore.CYAN + "\nStored Accounts and IDs:")
            for account, ids in passwords.items():
                print(Fore.MAGENTA + f"Account: {account}")
                for user_id in ids.keys():
                    print(Fore.YELLOW + f"  - ID: {user_id}")

        elif choice == '5':
            # Save and exit
            encrypted_data = encrypt_password(str(passwords), fernet)
            save_passwords(encrypted_data)
            print(Fore.GREEN + "Data saved. Goodbye!")
            break

        else:
            print(Fore.RED + "Invalid choice. Try again.")

if __name__ == "__main__":
    main()
