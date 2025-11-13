def parse_value(line):
    return line.split(':', 1)[1].strip().strip('"\'') if ':' in line else ""

def main():
    s = input("Введите имя файла yaml: ")
    
    print("=== Этап 1: Конфигурация ===")
    
    try:
        with open(s, encoding='utf-8') as file:
            print(f"Параметры файла {s}:")
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('package:'):
                    value = parse_value(line)
                    print(value if value else "Ошибка: Пустое значение поля package")
                    
                elif line.startswith('repository:'):
                    value = parse_value(line)
                    print(value if value else "Ошибка: Пустое значение поля repository")
                    
                elif line.startswith('mode:'):
                    value = parse_value(line)
                    print(value if value in ['remote', 'local', 'test'] else "Ошибка: Некорректный режим работы")
                    
                elif line.startswith('output_file:'):
                    value = parse_value(line)
                    print(value if value else "Ошибка: Пустое значение поля output_file")
                    
                elif line.startswith('ascii_tree:'):
                    value = parse_value(line).lower()
                    print(value if value in ['true', 'false'] else "Ошибка: Некорректное значение ascii_tree")
                    
                elif line.startswith('max_depth:'):
                    value = parse_value(line)
                    print(value if value.isdigit() and int(value) > 0 else "Ошибка: Некорректное значение max_depth")
                    
                elif line.startswith('filter:'):
                    value = parse_value(line)
                    print(value if value else "фильтр не задан")
        
        print("=== Этап 1 завершен ===")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл {s} не найден")
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}")

if __name__ == "__main__":
    main()
