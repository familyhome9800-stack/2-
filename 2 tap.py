import urllib.request
import xml.etree.ElementTree as ET

def parse_yaml_value(line):
    """Парсинг значения из YAML строки"""
    if ':' not in line:
        return ""
    
    # Разделяем по первому двоеточию
    key, value = line.split(':', 1)
    value = value.strip()
    
    # Убираем кавычки если есть
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    
    return value

def get_nuspec(package_name, version, url):
    base_url = f"{url}{package_name.lower()}/{version}/{package_name.lower()}.nuspec"
    print(f"Загрузка данных с {base_url} ...")
    try:
        with urllib.request.urlopen(base_url) as response:
            data = response.read().decode("utf-8")
        return data
    except Exception as e:
        print(f"Ошибка при загрузке пакета: {e}")
        return None

def extract_dependencies(nuspec_xml):
    try:
        root = ET.fromstring(nuspec_xml)
    except Exception as e:
        print(f"Ошибка при чтении XML: {e}")
        return []

    deps = []
    for dependency in root.findall(".//{*}dependency"):
        dep_id = dependency.attrib.get("id", "—")
        dep_version = dependency.attrib.get("version", "—")
        deps.append((dep_id, dep_version))
    return deps

print("Параметры файла:")
with open("config.yaml", "r", encoding="utf-8") as file:
    # Инициализируем переменные значениями по умолчанию
    name_packege = ""
    url = ""
    mode = ""
    version_packege = ""
    output_file = ""
    ascii_tree = False
    max_depth = ""
    filter_value = ""
    
    for line in file:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Парсим только конкретные поля из заданного формата
        if line.startswith('package:'):
            name_packege = parse_yaml_value(line)
        elif line.startswith('repository:'):
            url = parse_yaml_value(line)
        elif line.startswith('mode:'):
            mode = parse_yaml_value(line)
        elif line.startswith('output_file:'):
            output_file = parse_yaml_value(line)
        elif line.startswith('ascii_tree:'):
            ascii_tree_value = parse_yaml_value(line).lower()
            ascii_tree = ascii_tree_value == 'true'
        elif line.startswith('max_depth:'):
            max_depth = parse_yaml_value(line)
        elif line.startswith('filter:'):
            filter_value = parse_yaml_value(line)

# Вывод параметров в том же формате что и в оригинальном коде
print("Имя пакета:", name_packege)
print("URL:", url)
print("Режим:", mode)
print("Выходной файл:", output_file)
print("ASCII дерево:", ascii_tree)
print("Макс. глубина:", max_depth)
print("Фильтр:", filter_value)

print("\n=== Этап 2: Сбор данных о зависимостях ===")

# Для этапа 2 нам нужны только package, version и repository
# Но в заданном формате нет version, поэтому используем фиксированную версию
version_packege = "1.0.0"  # версия по умолчанию

if not name_packege or not url:
    print("Ошибка: Не заданы обязательные параметры (package, repository)")
else:
    nuspec_content = get_nuspec(name_packege, version_packege, url)
    if nuspec_content:
        dependencies = extract_dependencies(nuspec_content)
        if dependencies:
            print(f"\nПрямые зависимости пакета {name_packege} ({version_packege}):")
            for dep_id, dep_ver in dependencies:
                print(f" - {dep_id} ({dep_ver})")
        else:
            print(f"Пакет {name_packege} не имеет прямых зависимостей.")
