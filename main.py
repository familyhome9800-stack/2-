import os
import sys

def parse_value(line):
    """Парсит значение из строки YAML"""
    return line.split(':', 1)[1].strip().strip('"\'') if ':' in line else ""

def main():
    """Основная функция - Этап 1: Минимальный прототип с конфигурацией"""
    print("=== Этап 1: Минимальный прототип с конфигурацией ===")
    print("Чтение параметров из config.yaml...")
    
    try:
        with open("config.yaml", "r", encoding='utf-8') as file:
            print("\nНастраиваемые параметры (ключ-значение):")
            print("-" * 40)
            
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('package:'):
                    value = parse_value(line)
                    if value:
                        print(f"package: {value}")
                    else:
                        print("Ошибка: Пустое значение поля package")
                        return False
                
                elif line.startswith('repository:'):
                    value = parse_value(line)
                    if value:
                        print(f"repository: {value}")
                    else:
                        print("Ошибка: Пустое значение поля repository")
                        return False
                
                elif line.startswith('test_mode:'):
                    value = parse_value(line).lower()
                    if value in ['true', 'false']:
                        print(f"test_mode: {value}")
                    else:
                        print("Ошибка: Некорректное значение test_mode (должно быть true/false)")
                        return False
                
                # Имя сгенерированного файла с изображением графа
                elif line.startswith('output_file:'):
                    value = parse_value(line)
                    if value:
                        print(f"output_file: {value}")
                    else:
                        print("Ошибка: Пустое значение поля output_file")
                        return False
                
                # Режим вывода зависимостей в формате ASCII-дерева
                elif line.startswith('ascii_tree:'):
                    value = parse_value(line).lower()
                    if value in ['true', 'false']:
                        print(f"ascii_tree: {value}")
                    else:
                        print("Ошибка: Некорректное значение ascii_tree (должно быть true/false)")
                        return False
                
                # Подстрока для фильтрации пакетов
                elif line.startswith('filter:'):
                    value = parse_value(line)
                    if value:
                        print(f"filter: {value}")
                    else:
                        print("filter: (не задано)")
            
            print("-" * 40)
            print("Все параметры успешно загружены и проверены!")
            return True
            
    except FileNotFoundError:
        print("Ошибка: Файл config.yaml не найден")
        print("Создайте файл config.yaml со следующими параметрами:")
        print("package: имя_пакета")
        print("repository: URL_репозитория")
        print("test_mode: true/false")
        print("output_file: имя_файла")
        print("ascii_tree: true/false")
        print("filter: подстрока_для_фильтрации")
        return False
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
