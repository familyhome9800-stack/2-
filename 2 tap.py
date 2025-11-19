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
    config = {}
    for line in file:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('package:'):
            config['package'] = parse_yaml_value(line)
        elif line.startswith('repository:'):
            config['repository'] = parse_yaml_value(line)
        elif line.startswith('mode:'):
            config['mode'] = parse_yaml_value(line)
        elif line.startswith('version:'):
            config['version'] = parse_yaml_value(line)
        elif line.startswith('output_file:'):
            config['output_file'] = parse_yaml_value(line)
        elif line.startswith('ascii_tree:'):
            value = parse_yaml_value(line).lower()
            config['ascii_tree'] = value == 'true'
        elif line.startswith('filter:'):
            config['filter'] = parse_yaml_value(line)
        elif line.startswith('max_depth:'):
            config['max_depth'] = parse_yaml_value(line)

# Вывод параметров
print("Имя пакета:", config.get('package', 'Не задано'))
print("URL:", config.get('repository', 'Не задано'))
print("Режим:", config.get('mode', 'Не задано'))
print("Версия:", config.get('version', 'Не задано'))
print("Выходной файл:", config.get('output_file', 'Не задано'))
print("ASCII дерево:", config.get('ascii_tree', False))
print("Фильтр:", config.get('filter', 'Не задано'))
print("Макс. глубина:", config.get('max_depth', 'Не задано'))

print("\n=== Этап 2: Сбор данных о зависимостях ===")

package_name = config.get('package')
version = config.get('version')
url = config.get('repository')

if not package_name or not version or not url:
    print("Ошибка: Не заданы обязательные параметры (package, version, repository)")
else:
    nuspec_content = get_nuspec(package_name, version, url)
    if nuspec_content:
        dependencies = extract_dependencies(nuspec_content)
        if dependencies:
            print(f"\nПрямые зависимости пакета {package_name} ({version}):")
            for dep_id, dep_ver in dependencies:
                print(f" - {dep_id} ({dep_ver})")
        else:
            print(f"Пакет {package_name} не имеет прямых зависимостей.")
