import subprocess
import sys

def run_script(script_name):
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print("✅ Activity completed.")
    except subprocess.CalledProcessError:
        print(f"❌ Error running {script_name}.")

def install_requirements():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements.")

def main():
    while True:
        print("\nWhat do you want to do?")
        print("1. Run King Jouet script")
        print("2. Scrape EAN Values")
        print("3. Run Amazon script")
        print("4. Install requirements")
        print("5. Quit")

        choice = input("Enter your choice (1, 2, 3, 4 or 5): ")

        if choice == "1":
            run_script("king_jouet.py")
        elif choice == "2":
            run_script("ean_scraper.py")
        elif choice == "3":
            run_script("amazon_scraper.py")
        elif choice == "4":
            install_requirements()
        elif choice == "5":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, 4 or 5.")

if __name__ == "__main__":
    main()
