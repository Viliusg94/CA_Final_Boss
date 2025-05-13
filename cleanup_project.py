"""
Projektų valymo įrankis.
Šis skriptas padeda sutvarkyti projekto struktūrą ir pašalinti nereikalingus failus.
"""
import os
import shutil
from pathlib import Path
import sys

def print_section(title):
    """Atspausdina sekcijos pavadinimą su formatavimu"""
    print("\n" + "="*50)
    print(f"    {title}")
    print("="*50)

def confirm_action(message):
    """Patvirtina vartotojo veiksmą"""
    confirm = input(f"{message} (t/n): ").lower()
    return confirm == 't' or confirm == 'taip' or confirm == 'y' or confirm == 'yes'

def main():
    # Projekto šakninis katalogas
    root_dir = Path(__file__).parent
    
    print_section("Bitcoin Forecasting projekto valymas")
    print(f"Projekto katalogas: {root_dir}")
    
    if not confirm_action("Ar norite tęsti projekto valymą?"):
        print("Valymas atšauktas.")
        return
    
    # 1. Pašaliname dublikuotus failus
    print_section("Dublikuotų failų šalinimas")
      # Failai, kuriuos reikia pašalinti (reliatyvūs keliai nuo projekto šakninio katalogo)
    files_to_remove = [
        "v1/database/initialize_db.py",  # dublikatas v1/initialize_db.py
        "v1/database/test_database_imports.py",  # dublikatas v1/test_database_imports.py
        "v1/database/reset_db.py",  # dublikatas v1/reset_db.py
        "v1/database/set_password.py",  # dublikatas v1/set_password.py
        "sql.py",  # perkeltas funkcionalumas į database modulį
    ]
    
    for file_path in files_to_remove:
        full_path = root_dir / file_path
        if full_path.exists():
            if confirm_action(f"Ar norite pašalinti {file_path}?"):
                try:
                    os.remove(full_path)
                    print(f"✓ Pašalintas: {file_path}")
                except Exception as e:
                    print(f"✗ Klaida šalinant {file_path}: {e}")
            else:
                print(f"➖ Praleista: {file_path}")
      # 2. Išvalome __pycache__ katalogus
    print_section("__pycache__ katalogų šalinimas")
    
    pycache_dirs = []
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_dirs.append(os.path.join(root, dir_name))
    
    if pycache_dirs:
        if confirm_action(f"Ar norite pašalinti {len(pycache_dirs)} __pycache__ katalogus?"):
            for pycache_dir in pycache_dirs:
                try:
                    shutil.rmtree(pycache_dir)
                    print(f"✓ Pašalintas: {pycache_dir}")
                except Exception as e:
                    print(f"✗ Klaida šalinant {pycache_dir}: {e}")
    else:
        print("Nerasta __pycache__ katalogų.")
        
    # 2.5 Patikriname didelius failus, kurie neturėtų būti sekiojami
    print_section("Didelių failų tikrinimas")
    
    large_files = []
    size_threshold = 5 * 1024 * 1024  # 5 MB
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.csv', '.pkl', '.h5', '.model')):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > size_threshold:
                        large_files.append((file_path, size / (1024 * 1024)))
                except Exception:
                    pass
    
    if large_files:
        print(f"Rasti {len(large_files)} dideli failai, kurie greičiausiai neturėtų būti sekiojami:")
        for file_path, size in large_files:
            rel_path = os.path.relpath(file_path, root_dir)
            print(f"  - {rel_path} ({size:.2f} MB)")
        
        print("\nPatikrinkite, ar šie failai yra įtraukti į .gitignore. Jei ne, rekomenduojama juos įtraukti.")
    else:
        print("Nerasta didelių failų, kurie galėtų sukelti problemų.") 
      # 3. Atnaujinkime Git repozitoriją
    print_section("Git repozitorijos atnaujinimas")
    
    if confirm_action("Ar norite atnaujinti Git repozitoriją (git add .)?"):
        try:
            # Pridedame svarbius failus
            os.system("git add cleanup_project.py")
            os.system("git add .gitignore")
            os.system("git add v1/*.py")
            os.system("git add v1/database/*.py")
            os.system("git add v1/data/*.py")
            os.system("git add v1/models/*.py")
            os.system("git add v1/utils/*.py")
            os.system("git add v1/*.md v1/*.txt")
            os.system("git add v1/.env.example")
            print("✓ Git repozitorija atnaujinta.")
        except Exception as e:
            print(f"✗ Klaida atnaujinant Git repozitoriją: {e}")
    
    # Pabaigos pranešimas
    print_section("Projekto valymas baigtas")
    print("Projektas sėkmingai sutvarkytas!")
    print("Dabar galite pereiti į kitus etapus:")
    print("1. Duomenų transformacijos (Checkpoint 2)")
    print("2. Modelių kūrimas (Checkpoint 3)")
    print("3. Vartotojo sąsajos tobulinimas (Checkpoint 4)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nValymas nutrauktas vartotojo.")
        sys.exit(1)
    except Exception as e:
        print(f"\nĮvyko klaida: {e}")
        sys.exit(1)
