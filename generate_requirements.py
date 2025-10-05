import os
import sys
import pkg_resources
from pathlib import Path
import importlib.util
import builtins

PROJECT_DIR = Path(__file__).parent

# Получаем список стандартных модулей Python
STANDARD_MODULES = set(sys.builtin_module_names)
# Добавим модули из стандартной библиотеки, которые часто встречаются
EXTRA_STANDARD = {
    'os', 'sys', 'math', 'json', 're', 'time', 'threading', 'subprocess',
    'collections', 'itertools', 'functools', 'logging', 'enum', 'pathlib',
    'random', 'asyncio', 'typing', 'abc', 'inspect', 'copy', 'contextlib',
    'dataclasses', 'io', 'traceback', 'shlex', 'pickle', 'tempfile', 'hashlib',
    'operator', 'sqlite3', 'struct', 'socket', 'ssl', 'email', 'http', 'argparse',
    'glob', 'gzip', 'shutil', 'tarfile', 'zipfile', 'platform', 'getpass'
}
STANDARD_MODULES.update(EXTRA_STANDARD)

# Функция для сбора всех импортов из проекта
def get_project_imports(project_dir):
    imports = set()
    for py_file in project_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("import "):
                        imports.add(line.split()[1].split(".")[0])
                    elif line.startswith("from "):
                        imports.add(line.split()[1].split(".")[0])
        except Exception as e:
            print(f"Не удалось прочитать {py_file}: {e}")
    return imports

# Получаем версии установленных пакетов
def get_installed_packages():
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def main():
    project_imports = get_project_imports(PROJECT_DIR)
    installed_packages = get_installed_packages()
    
    requirements = []
    for pkg in sorted(project_imports):
        pkg_lower = pkg.lower()
        if pkg_lower in installed_packages and pkg not in STANDARD_MODULES:
            requirements.append(f"{pkg}=={installed_packages[pkg_lower]}")
    
    if requirements:
        with open(PROJECT_DIR / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(requirements))
        print(f"requirements.txt успешно создан с {len(requirements)} пакетами!")
    else:
        print("Не найдено внешних пакетов для requirements.txt")

if __name__ == "__main__":
    main()
    