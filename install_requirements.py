import os
import subprocess
import sys

def main():
    # Получаем текущую директорию
    current_dir = os.getcwd()
    requirements_file = os.path.join(current_dir, "requirements.txt")
    
    # Проверяем существование requirements.txt
    if not os.path.exists(requirements_file):
        print("Файл requirements.txt не найден в текущей директории")
        sys.exit(1)
    
    # Создаем директорию для библиотек
    venv_dir = os.path.join(current_dir, "venv")
    try:
        os.makedirs(venv_dir, exist_ok=True)
    except Exception as e:
        print(f"Ошибка при создании директории venv: {e}")
        sys.exit(1)
    
    # Создаем виртуальное окружение
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании виртуального окружения: {e}")
        sys.exit(1)
    
    # Определяем путь к pip в виртуальном окружении
    if sys.platform == "darwin":  # macOS
        pip_path = os.path.join(venv_dir, "bin", "pip")
    else:
        # Для других ОС (можно добавить поддержку Windows/Linux если нужно)
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
    
    # Обновляем pip
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обновлении pip: {e}")
        sys.exit(1)
    
    # Устанавливаем библиотеки из requirements.txt
    try:
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
        print(f"Все библиотеки из requirements.txt успешно установлены в {venv_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке библиотек: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
