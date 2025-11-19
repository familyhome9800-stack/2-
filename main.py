def parse_value(line):
    return line.split(':', 1)[1].strip().strip('"\'') if ':' in line else ""

def read_file(filename):
    """Чтение файла"""
    try:
        file = open(filename, 'r', encoding='utf-8')
        content = file.read()
        file.close()
        return content
    except:
        return None

def write_file(filename, content):
    """Запись в файл"""
    try:
        file = open(filename, 'w', encoding='utf-8')
        file.write(content)
        file.close()
        return True
    except:
        return False

def parse_config(filename):
    """Парсинг конфигурационного файла YAML"""
    config = {}
    content = read_file(filename)
    if content is None:
        return None
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('package:'):
            config['package'] = parse_value(line)
        elif line.startswith('repository:'):
            config['repository'] = parse_value(line)
        elif line.startswith('mode:'):
            config['mode'] = parse_value(line)
        elif line.startswith('output_file:'):
            config['output_file'] = parse_value(line)
        elif line.startswith('ascii_tree:'):
            config['ascii_tree'] = parse_value(line).lower() == 'true'
        elif line.startswith('filter:'):
            config['filter'] = parse_value(line)
        elif line.startswith('version:'):
            config['version'] = parse_value(line)
    
    if 'mode' not in config:
        config['mode'] = 'remote'
    if 'filter' not in config:
        config['filter'] = ''
    if 'version' not in config:
        config['version'] = '1.0.0'  # версия по умолчанию
    
    return config

def parse_test_repository(filepath):
    """Парсинг тестового репозитория"""
    content = read_file(filepath)
    if content is None:
        return None
    
    dependencies = {}
    lines = content.split('\n')
    current_package = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('Package:'):
            current_package = line.split(':', 1)[1].strip()
            dependencies[current_package] = []
        elif line.startswith('Dependencies:'):
            deps_str = line.split(':', 1)[1].strip()
            if deps_str and current_package:
                deps = [dep.strip() for dep in deps_str.split(',') if dep.strip()]
                dependencies[current_package] = deps
    
    return dependencies

# === ЭТАП 2: Сбор данных (ваш код) ===
def get_nuspec(package_name, version, url):
    """Получение nuspec файла пакета"""
    base_url = f"{url}{package_name.lower()}/{version}/{package_name.lower()}.nuspec"
    print(f"Загрузка данных с {base_url} ...")
    try:
        # Эмуляция загрузки (без реальных HTTP запросов)
        print(f"Эмуляция загрузки nuspec для {package_name} версии {version}")
        
        # Эмулируем содержимое nuspec файла для разных пакетов
        sample_nuspecs = {
            "Newtonsoft.Json": '''<?xml version="1.0"?>
<package>
  <metadata>
    <dependencies>
      <dependency id="System.Runtime" version="4.3.0" />
      <dependency id="System.Xml" version="4.3.0" />
    </dependencies>
  </metadata>
</package>''',
            "EntityFramework": '''<?xml version="1.0"?>
<package>
  <metadata>
    <dependencies>
      <dependency id="System.ComponentModel.DataAnnotations" version="4.3.0" />
      <dependency id="System.Data" version="4.3.0" />
    </dependencies>
  </metadata>
</package>''',
            "System.Runtime": '''<?xml version="1.0"?>
<package>
  <metadata>
    <dependencies>
    </dependencies>
  </metadata>
</package>'''
        }
        
        return sample_nuspecs.get(package_name, '''<?xml version="1.0"?>
<package>
  <metadata>
    <dependencies>
    </dependencies>
  </metadata>
</package>''')
        
    except Exception as e:
        print(f"Ошибка при загрузке пакета: {e}")
        return None

def extract_dependencies(nuspec_xml):
    """Извлечение зависимостей из nuspec XML"""
    try:
        # Простой парсинг XML без библиотек
        dependencies = []
        lines = nuspec_xml.split('\n')
        
        for line in lines:
            line = line.strip()
            if '<dependency id=' in line:
                # Извлекаем id и version из строки типа: <dependency id="System.Runtime" version="4.3.0" />
                parts = line.split('"')
                if len(parts) >= 3:
                    dep_id = parts[1]  # id находится между первыми кавычками
                    dep_version = parts[3] if len(parts) > 3 else "—"  # version между следующими кавычками
                    dependencies.append((dep_id, dep_version))
        
        return dependencies
    except Exception as e:
        print(f"Ошибка при чтении XML: {e}")
        return []

def get_direct_dependencies(package_name, repository_url, mode, version):
    """Получить прямые зависимости пакета"""
    if mode == 'test':
        # Режим тестирования - используем файл тестового репозитория
        deps_data = parse_test_repository(repository_url)
        if deps_data and package_name in deps_data:
            return [dep for dep in deps_data[package_name]]
        return []
    
    # Режим remote - используем ваш код для получения зависимостей
    nuspec_content = get_nuspec(package_name, version, repository_url)
    if nuspec_content:
        dependencies = extract_dependencies(nuspec_content)
        return [dep_id for dep_id, dep_ver in dependencies]
    
    return []

# === ЭТАП 3: Основные операции ===
def build_dependency_graph(start_package, repository_url, mode, filter_str, version, visited=None, graph=None):
    """Построение графа зависимостей с помощью DFS с рекурсией"""
    if visited is None:
        visited = {}
    if graph is None:
        graph = {}
    
    if start_package in visited:
        return graph
    
    visited[start_package] = True
    
    if filter_str and filter_str in start_package:
        graph[start_package] = []
        return graph
    
    direct_deps = get_direct_dependencies(start_package, repository_url, mode, version)
    graph[start_package] = []
    
    for dep in direct_deps:
        if filter_str and filter_str in dep:
            continue
        
        graph[start_package].append(dep)
        
        if dep not in visited:
            build_dependency_graph(dep, repository_url, mode, filter_str, version, visited, graph)
    
    return graph

def detect_cycles(graph):
    """Обнаружение циклических зависимостей"""
    def dfs_cycle_detect(node, visited, recursion_stack, cycles):
        visited[node] = True
        recursion_stack[node] = True
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs_cycle_detect(neighbor, visited, recursion_stack, cycles):
                    cycles.add(node)
                    return True
            elif recursion_stack.get(neighbor, False):
                cycles.add(node)
                cycles.add(neighbor)
                return True
        
        recursion_stack[node] = False
        return False
    
    visited = {}
    recursion_stack = {}
    cycles = set()
    
    for node in graph:
        if node not in visited:
            dfs_cycle_detect(node, visited, recursion_stack, cycles)
    
    return list(cycles)

def save_graph_to_file(graph, filename):
    """Сохранение графа в файл"""
    content = "Граф зависимостей:\n"
    for package, deps in graph.items():
        content += f"{package} -> {deps}\n"
    
    if write_file(filename, content):
        print(f"Граф сохранен в файл: {filename}")
    else:
        print("Ошибка при сохранении графа")

def main():
    filename = input("Введите имя файла yaml: ")
    
    print("=== Этап 1: Конфигурация ===")
    
    config = parse_config(filename)
    if config is None:
        print("Ошибка: Не удалось прочитать конфигурационный файл")
        return
    
    # Вывод параметров конфигурации
    print(f"Пакет: {config.get('package', 'Не задан')}")
    print(f"Репозиторий: {config.get('repository', 'Не задан')}")
    print(f"Режим: {config.get('mode', 'remote')}")
    print(f"Версия: {config.get('version', '1.0.0')}")
    print(f"Выходной файл: {config.get('output_file', 'Не задан')}")
    print(f"ASCII дерево: {config.get('ascii_tree', False)}")
    print(f"Фильтр: {config.get('filter', 'Не задан')}")
    
    print("\n=== Этап 2: Сбор данных ===")
    
    package_name = config.get('package')
    repository_url = config.get('repository')
    mode = config.get('mode', 'remote')
    version = config.get('version', '1.0.0')
    
    if not package_name:
        print("Ошибка: Не задано имя пакета")
        return
    
    # Получаем прямые зависимости с использованием вашего кода
    nuspec_content = get_nuspec(package_name, version, repository_url)
    if nuspec_content:
        dependencies = extract_dependencies(nuspec_content)
        if dependencies:
            print(f"\nПрямые зависимости пакета {package_name} ({version}):")
            for dep_id, dep_ver in dependencies:
                print(f" - {dep_id} ({dep_ver})")
        else:
            print(f"Пакет {package_name} не имеет прямых зависимостей.")
    else:
        print(f"Не удалось получить зависимости для пакета {package_name}")
    
    print("\n=== Этап 3: Основные операции ===")
    
    # Строим полный граф зависимостей
    filter_str = config.get('filter', '')
    dependency_graph = build_dependency_graph(package_name, repository_url, mode, filter_str, version)
    
    print("Полный граф зависимостей:")
    for package, deps in dependency_graph.items():
        print(f"  {package} -> {deps}")
    
    # Обнаруживаем циклические зависимости
    cycles = detect_cycles(dependency_graph)
    if cycles:
        print(f"Обнаружены циклические зависимости: {cycles}")
    else:
        print("Циклические зависимости не обнаружены")
    
    # Сохранение результатов
    output_file = config.get('output_file', 'dependencies.txt')
    save_graph_to_file(dependency_graph, output_file)
    
    # Демонстрация работы с тестовым репозиторием
    if mode == 'test':
        print("\nДемонстрация работы с тестовым репозиторием:")
        test_data = parse_test_repository(repository_url)
        if test_data:
            print("Содержимое тестового репозитория:")
            for pkg, deps in test_data.items():
                print(f"  {pkg}: {deps}")

if __name__ == "__main__":
    main()
