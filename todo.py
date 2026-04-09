import json
import os
from colorama import Fore, Style, init

# Αρχικοποίηση colorama για χρώματα στο terminal
init(autoreset=True)

# Το αρχείο JSON όπου αποθηκεύονται τα tasks
FILENAME = "tasks.json"

# Φορτώνει τα tasks από το αρχείο JSON (αν υπάρχει)
def load_tasks():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []  # Αν δεν υπάρχει αρχείο, επιστρέφει άδεια λίστα

# Αποθηκεύει τα tasks στο αρχείο JSON
def save_tasks(tasks):
    with open(FILENAME, "w") as f:
        json.dump(tasks, f, indent=2)

# Εμφανίζει όλα τα tasks με ✓ ή ✗ ανάλογα με την κατάστασή τους
def show_tasks(tasks):
    if not tasks:
        print(Fore.YELLOW + "Δεν υπάρχουν tasks!")
        return
    print(Fore.CYAN + "\n📋 Λίστα Tasks:")
    for i, task in enumerate(tasks, 1):
        # Πράσινο ✓ αν έγινε, κόκκινο ✗ αν όχι
        status = Fore.GREEN + "✓" if task["done"] else Fore.RED + "✗"
        print(f"  {status} {i}. {Style.RESET_ALL}{task['title']}")
    print()

# Προσθέτει νέο task στη λίστα
def add_task(tasks):
    title = input(Fore.CYAN + "Νέο task: ")
    tasks.append({"title": title, "done": False})  # done=False γιατί είναι νέο
    save_tasks(tasks)
    print(Fore.GREEN + "✓ Προστέθηκε!")

# Σημειώνει ένα task ως ολοκληρωμένο
def complete_task(tasks):
    show_tasks(tasks)
    try:
        num = int(input(Fore.CYAN + "Ποιο task ολοκληρώθηκε; (αριθμός): "))
        tasks[num - 1]["done"] = True  # Αλλάζει το done σε True
        save_tasks(tasks)
        print(Fore.GREEN + "✓ Ολοκληρώθηκε!")
    except (ValueError, IndexError):
        print(Fore.RED + "Λάθος αριθμός!")

# Διαγράφει ένα task από τη λίστα
def delete_task(tasks):
    show_tasks(tasks)
    try:
        num = int(input(Fore.CYAN + "Ποιο task να διαγραφεί; (αριθμός): "))
        removed = tasks.pop(num - 1)  # Αφαιρεί το task από τη λίστα
        save_tasks(tasks)
        print(Fore.RED + f"✗ Διαγράφηκε: {removed['title']}")
    except (ValueError, IndexError):
        print(Fore.RED + "Λάθος αριθμός!")

# Κεντρική συνάρτηση — εμφανίζει το μενού και διαχειρίζεται τις επιλογές
def main():
    tasks = load_tasks()  # Φόρτωσε τα αποθηκευμένα tasks
    while True:
        print(Fore.YELLOW + "─── To-Do App ───")
        print("1. Δες tasks")
        print("2. Πρόσθεσε task")
        print("3. Ολοκλήρωσε task")
        print("4. Διάγραψε task")
        print("5. Έξοδος")
        choice = input(Fore.CYAN + "\nΕπιλογή: ")

        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print(Fore.YELLOW + "Αντίο!")
            break
        else:
            print(Fore.RED + "Μη έγκυρη επιλογή!")

# Εκτελείται μόνο αν τρέξουμε απευθείας αυτό το αρχείο
if __name__ == "__main__":
    main()
