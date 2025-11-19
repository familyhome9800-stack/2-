import urllib.request
import xml.etree.ElementTree as ET

def get_value(line):
    parts = line.split("=")
    if len(parts) < 2:
        return ""
    return parts[1].strip()

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
with open("config.ini", "r", encoding="utf-8") as file:
    file.readline()
    name_packege = get_value(file.readline())
    url = get_value(file.readline())
    mode = get_value(file.readline())
    version_packege = get_value(file.readline())
    filter_value = get_value(file.readline())

    print("Имя пакета:", name_packege)
    print("URL:", url)
    print("Режим:", mode)
    print("Версия:", version_packege)
    print("Фильтр:", filter_value)

print("\n=== Этап 2: Сбор данных о зависимостях ===")

nuspec_content = get_nuspec(name_packege, version_packege, url)
if nuspec_content:
    dependencies = extract_dependencies(nuspec_content)
    if dependencies:
        print(f"\nПрямые зависимости пакета {name_packege} ({version_packege}):")
        for dep_id, dep_ver in dependencies:
            print(f" - {dep_id} ({dep_ver})")
    else:
        print(f"Пакет {name_packege} не имеет прямых зависимостей.")
