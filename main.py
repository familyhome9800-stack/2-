def parse_value(line):
    return line.split(':', 1)[1].strip().strip('"\'') if ':' in line else ""

def read_file(filename):
    """Чтение файла без использования библиотек"""
    try:
        file = open(filename, 'r', encoding='utf-8')
        content = file.read()
        file.close()
        return content
    except:
        return None

def parse_config(filename):
    """Парсинг конфигурационного файла"""
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
    
    # Установка значений по умолчанию
    if 'mode' not in config:
        config['mode'] = 'remote'
    if 'filter' not in config:
        config['filter'] = ''
    
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
                deps = [dep.strip() for dep in deps_str.split(',')]
                dependencies[current_package] = deps
    
    return dependencies

def get_direct_dependencies(package_name, repository_url, mode):
    """Получить прямые зависимости пакета"""
    if mode == 'test':
        # Режим тестирования - используем файл тестового репозитория
        deps_data = parse_test_repository(repository_url)
        if deps_data and package_name in deps_data:
            return deps_data[package_name]
        return []
    
    # Для реального режима эмулируем данные (без библиотек для HTTP запросов)
    # В реальном проекте здесь был бы HTTP запрос к NuGet API
    print(f"Эмуляция получения зависимостей для {package_name}")
    
    # Эмулируем некоторые известные зависимости для демонстрации
    sample_dependencies = {
        "Newtonsoft.Json": ["System.Runtime", "System.Xml"],
        "EntityFramework": ["System.ComponentModel.DataAnnotations", "System.Data"],
        "System.Runtime": [],
        "System.Xml": ["System.Runtime"],
        "System.ComponentModel.DataAnnotations": ["System.Runtime"],
        "System.Data": ["System.Runtime", "System.Xml"]
    }
    
    return sample_dependencies.get(package_name, [])

def build_dependency_graph(start_package, repository_url, mode, filter_str, visited=None, graph=None):
    """Построение графа зависимостей с помощью DFS с рекурсией"""
    if visited is None:
        visited = {}
    if graph is None:
        graph = {}
    
    if start_package in visited:
        return graph
    
    visited[start_package] = True
    
    # Пропускаем пакеты, содержащие подстроку фильтра
    if filter_str and filter_str in start_package:
        graph[start_package] = []
        return graph
    
    # Получаем прямые зависимости
    direct_deps = get_direct_dependencies(start_package, repository_url, mode)
    graph[start_package] = []
    
    for dep in direct_deps:
        # Пропускаем зависимости, содержащие подстроку фильтра
        if filter_str and filter_str in dep:
            continue
        
        graph[start_package].append(dep)
        
        # Рекурсивно строим граф для зависимости
        if dep not in visited:
            build_dependency_graph(dep, repository_url, mode, filter_str, visited, graph)
    
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
    print(f"Выходной файл: {config.get('output_file', 'Не задан')}")
    print(f"ASCII дерево: {config.get('ascii_tree', False)}")
    print(f"Фильтр: {config.get('filter', 'Не задан')}")
    
    print("\n=== Этап 2: Сбор данных ===")
    
    package_name = config.get('package')
    repository_url = config.get('repository')
    mode = config.get('mode', 'remote')
    
    if not package_name:
        print("Ошибка: Не задано имя пакета")
        return
    
    # Получаем прямые зависимости
    direct_deps = get_direct_dependencies(package_name, repository_url, mode)
    print(f"Прямые зависимости пакета {package_name}:")
    for dep in direct_deps:
        print(f"  - {dep}")
    
    print("\n=== Этап 3: Основные операции ===")
    
    # Строим полный граф зависимостей
    filter_str = config.get('filter', '')
    dependency_graph = build_dependency_graph(package_name, repository_url, mode, filter_str)
    
    print("Полный граф зависимостей:")
    for package, deps in dependency_graph.items():
        print(f"  {package} -> {deps}")
    
    # Обнаруживаем циклические зависимости
    cycles = detect_cycles(dependency_graph)
    if cycles:
        print(f"Обнаружены циклические зависимости: {cycles}")
    else:
        print("Циклические зависимости не обнаружены")
    
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
