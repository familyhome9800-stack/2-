import urllib.request
import xml.etree.ElementTree as ET

def parse_yaml_value(line):
    """Парсинг значения из YAML строки"""
    if ':' not in line:
        return ""
    
    parts = line.split(':', 1)
    value = parts[1].strip()
    
    # Убираем кавычки если они есть
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
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
    lines = file.readlines()
    
    # Парсим YAML файл
    config = {}
    for line in lines:
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

    # Извлекаем значения с проверкой на наличие
    name_package = config.get('package', '')
    url = config.get('repository', '')
    mode = config.get('mode', 'remote')
    version_package = config.get('version', '')
    filter_value = config.get('filter', '')
    output_file = config.get('output_file', '')
    ascii_tree = config.get('ascii_tree', False)
    max_depth = config.get('max_depth', '')

    print("Имя пакета:", name_package)
    print("URL репозитория:", url)
    print("Режим:", mode)
    print("Версия:", version_package)
    print("Фильтр:", filter_value)
    print("Выходной файл:", output_file)
    print("ASCII дерево:", ascii_tree)
    print("Макс. глубина:", max_depth)

print("\n=== Этап 2: Сбор данных о зависимостях ===")

if name_package and version_package and url:
    nuspec_content = get_nuspec(name_package, version_package, url)
    if nuspec_content:
        dependencies = extract_dependencies(nuspec_content)
        if dependencies:
            print(f"\nПрямые зависимости пакета {name_package} ({version_package}):")
            for dep_id, dep_ver in dependencies:
                print(f" - {dep_id} ({dep_ver})")
        else:
            print(f"Пакет {name_package} не имеет прямых зависимостей.")
    else:
        print(f"Не удалось загрузить данные для пакета {name_package}")
else:
    print("Ошибка: Не все обязательные параметры заданы (package, version, repository)")
