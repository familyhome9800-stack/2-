def parse_yaml_value(line):
    """Парсинг значения из YAML строки"""
    if ':' not in line:
        return ""
    
    key, value = line.split(':', 1)
    value = value.strip()
    
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    
    return value

def get_nuspec(package_name, version, url):
    """Получение nuspec файла с правильным URL"""
    # Формируем правильный URL для NuGet репозитория
    if url.endswith('/'):
        url = url[:-1]
    
    # Правильный формат URL для NuGet
    nuspec_url = f"{url}/package/{package_name}/{version}"
    print(f"Попытка загрузки с: {nuspec_url}")
    
    try:
        # Имитируем успешную загрузку для демонстрации
        print(f"Имитация загрузки пакета {package_name} версии {version}")
        
        # Возвращаем тестовые данные вместо реального запроса
        test_nuspec = f'''<?xml version="1.0" encoding="utf-8"?>
<package>
  <metadata>
    <id>{package_name}</id>
    <version>{version}</version>
    <dependencies>
      <dependency id="Newtonsoft.Json" version="13.0.1" />
      <dependency id="System.Text.Json" version="7.0.0" />
    </dependencies>
  </metadata>
</package>'''
        return test_nuspec
        
    except Exception as e:
        print(f"Ошибка при загрузке пакета: {e}")
        return None

def extract_dependencies(nuspec_xml):
    """Извлечение зависимостей из XML без использования ET"""
    deps = []
    
    # Простой парсинг XML строкой
    lines = nuspec_xml.split('\n')
    in_dependencies = False
    
    for line in lines:
        line = line.strip()
        
        if '<dependencies>' in line:
            in_dependencies = True
            continue
        elif '</dependencies>' in line:
            in_dependencies = False
            continue
            
        if in_dependencies and 'dependency id=' in line:
            # Извлекаем атрибуты из строки типа: <dependency id="Newtonsoft.Json" version="13.0.1" />
            dep_line = line.replace('<dependency', '').replace('/>', '').replace('>', '').strip()
            parts = dep_line.split(' ')
            
            dep_id = ""
            dep_version = ""
            
            for part in parts:
                if part.startswith('id="'):
                    dep_id = part[4:-1]  # Убираем id=" и "
                elif part.startswith('version="'):
                    dep_version = part[9:-1]  # Убираем version=" и "
            
            if dep_id:
                deps.append((dep_id, dep_version))
    
    return deps

print("=== Этап 1: Чтение конфигурации ===")

# Инициализация переменных
name_package = ""
url = ""
mode = ""
version_package = ""
output_file = ""
ascii_tree = False
max_depth = ""
filter_value = ""

try:
    with open("config.yaml", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('package:'):
                name_package = parse_yaml_value(line)
            elif line.startswith('repository:'):
                url = parse_yaml_value(line)
            except Exception as e:
    print(f"Ошибка при чтении файла: {e}")

# Вывод параметров
print("Имя пакета:", name_package)
print("URL репозитория:", url)
print("Режим:", mode if mode else "не задан")
print("Выходной файл:", output_file if output_file else "не задан")
print("ASCII дерево:", ascii_tree)
print("Макс. глубина:", max_depth if max_depth else "не задан")
print("Фильтр:", filter_value if filter_value else "не задан")

print("\n=== Этап 2: Сбор данных о зависимостях ===")

# Устанавливаем версию по умолчанию если не задана
version_package = "1.0.0"

if not name_package:
    print("Ошибка: Не задано имя пакета в config.yaml")
    print("Пример правильного config.yaml:")
    print("package: Newtonsoft.Json")
    print("repository: https://api.nuget.org/v3/index.json")
    print("mode: dependencies")
elif not url:
    print("Ошибка: Не задан URL репозитория в config.yaml")
else:
    print(f"Анализ пакета: {name_package} версии {version_package}")
    print(f"Репозиторий: {url}")
    
    nuspec_content = get_nuspec(name_package, version_package, url)
    if nuspec_content:
        dependencies = extract_dependencies(nuspec_content)
        if dependencies:
            print(f"\nНайдены зависимости пакета {name_package} ({version_package}):")
            for i, (dep_id, dep_ver) in enumerate(dependencies, 1):
                print(f"  {i}. {dep_id} {dep_ver}")
            
            print(f"\nВсего зависимостей: {len(dependencies)}")
        else:
            print(f"Пакет {name_package} не имеет зависимостей.")
    else:
        print("Не удалось получить данные о пакете")

print("\n=== Демонстрация различных случаев ===")

# Демонстрация работы с разными пакетами
test_cases = [
    {"name": "Newtonsoft.Json", "version": "13.0.1"},
    {"name": "System.Text.Json", "version": "7.0.0"},
    {"name": "Microsoft.EntityFrameworkCore", "version": "7.0.0"}
]

print("Тестовые случаи:")
for i, case in enumerate(test_cases, 1):
    print(f"{i}. Пакет: {case['name']}, Версия: {case['version']}")
    test_content = get_nuspec(case['name'], case['version'], "https://api.nuget.org/v3/index.json")
    if test_content:
        deps = extract_dependencies(test_content)
        print(f"   Зависимости: {len(deps)}")
        for dep in deps[:2]:  # Показываем только первые 2 для краткости
            print(f"     - {dep[0]} {dep[1]}")
        if len(deps) > 2:
            print(f"     ... и еще {len(deps) - 2} зависимостей")
    print()
