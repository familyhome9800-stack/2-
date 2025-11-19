# Парсер YAML
def parse_yaml(content):
    lines = content.split('\n')
    result = {}
    current_key = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.endswith(':'):
            current_key = line[:-1].strip()
            result[current_key] = []
        elif line.startswith('-'):
            if current_key is not None:
                item = line[1:].strip()
                result[current_key].append(item)
    
    return result

# Построение графа зависимостей
def build_dependency_graph(data, exclude_pattern=None):
    graph = {}
    
    for package, deps in data.items():
        if exclude_pattern and exclude_pattern in package:
            continue
        filtered_deps = []
        for dep in deps:
            if not exclude_pattern or exclude_pattern not in dep:
                filtered_deps.append(dep)
        graph[package] = filtered_deps
    
    return graph

# DFS с обнаружением циклов
def dfs_with_cycles_detection(graph, start_node, visited=None, recursion_stack=None, path=None, cycles=None):
    if visited is None:
        visited = set()
    if recursion_stack is None:
        recursion_stack = set()
    if path is None:
        path = []
    if cycles is None:
        cycles = []
    
    visited.add(start_node)
    recursion_stack.add(start_node)
    path.append(start_node)
    
    if start_node in graph:
        for neighbor in graph[start_node]:
            if neighbor not in graph:
                continue
            if neighbor not in visited:
                dfs_with_cycles_detection(graph, neighbor, visited, recursion_stack, path, cycles)
            elif neighbor in recursion_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:]
                cycles.append(cycle.copy())
    
    path.pop()
    recursion_stack.remove(start_node)
    return cycles

# Получение всех транзитивных зависимостей
def get_all_dependencies(graph, package, exclude_pattern=None):
    if package not in graph:
        return set()
    
    visited = set()
    
    def dfs(node):
        if node in visited or node not in graph:
            return
        visited.add(node)
        for dep in graph[node]:
            if exclude_pattern and exclude_pattern in dep:
                continue
            if dep in graph:
                dfs(dep)
    
    for dep in graph[package]:
        if exclude_pattern and exclude_pattern in dep:
            continue
        dfs(dep)
    
    return visited

# Валидация имен пакетов (только большие латинские буквы)
def validate_package_names(data):
    for package, deps in data.items():
        if not package.isupper() or not package.isalpha():
            return False, f"Неверное имя пакета: {package}"
        for dep in deps:
            if not dep.isupper() or not dep.isalpha():
                return False, f"Неверное имя зависимости: {dep}"
    return True, "OK"

# Основная функция
def main():
    print("=== Анализатор зависимостей пакетов ===")
    print("Режимы работы:")
    print("1 - Тестовый режим (встроенные тесты)")
    print("2 - Файловый режим (пользовательский файл)")
    
    mode = input("Выберите режим: ").strip()
    
    if mode == "1":
        run_test_cases()
    elif mode == "2":
        run_file_mode()
    else:
        print("Неверный режим")

# Режим работы с файлом
def run_file_mode():
    file_path = input("Введите путь к файлу описания графа: ").strip()
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        data = parse_yaml(content)
        
        # Валидация имен пакетов
        valid, message = validate_package_names(data)
        if not valid:
            print(f"Ошибка валидации: {message}")
            return
        
        print("\nЗагруженные данные:")
        for pkg, deps in data.items():
            print(f"{pkg}: {deps}")
        
        exclude_pattern = input("\nВведите подстроку для исключения (или Enter чтобы пропустить): ").strip()
        if exclude_pattern == "":
            exclude_pattern = None
        
        graph = build_dependency_graph(data, exclude_pattern)
        
        print("\nГраф зависимостей:")
        for node, deps in graph.items():
            print(f"{node} -> {deps}")
        
        # Проверка циклов
        all_cycles = []
        visited = set()
        for node in graph:
            if node not in visited:
                cycles = dfs_with_cycles_detection(graph, node, set(), set(), [], [])
                all_cycles.extend(cycles)
                visited.add(node)
        
        if all_cycles:
            print("\nОбнаружены циклические зависимости:")
            for cycle in all_cycles:
                print(f"Цикл: {' -> '.join(cycle)} -> {cycle[0]}")
        else:
            print("\nЦиклические зависимости не обнаружены")
        
        # Транзитивные зависимости
        print("\nТранзитивные зависимости:")
        for package in sorted(graph.keys()):
            all_deps = get_all_dependencies(graph, package, exclude_pattern)
            if all_deps:
                print(f"{package}: {sorted(list(all_deps))}")
            else:
                print(f"{package}: нет зависимостей")
        
    except Exception as e:
        print(f"Ошибка: {e}")

# Тестовые случаи
def run_test_cases():
    print("\n" + "="*50)
    print("ТЕСТ 1: Простой граф без циклов")
    print("="*50)
    test1 = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D'],
        'D': []
    }
    run_test(test1, "TEST1")
    
    print("\n" + "="*50)
    print("ТЕСТ 2: Граф с циклическими зависимостями")
    print("="*50)
    test2 = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A']
    }
    run_test(test2, "TEST2")
    
    print("\n" + "="*50)
    print("ТЕСТ 3: Сложный граф с исключениями")
    print("="*50)
    test3 = {
        'A': ['B', 'C'],
        'B': ['D', 'EXCLUDE_ME'],
        'C': ['E'],
        'D': ['F'],
        'E': ['B'],
        'F': [],
        'EXCLUDE_ME': ['A']
    }
    run_test(test3, "TEST3", "EXCLUDE")

# Запуск теста
def run_test(data, test_name, exclude_pattern=None):
    print(f"\nДанные {test_name}:")
    for pkg, deps in data.items():
        print(f"{pkg}: {deps}")
    
    graph = build_dependency_graph(data, exclude_pattern)
    
    print(f"\nГраф {test_name}:")
    for node, deps in graph.items():
        print(f"{node} -> {deps}")
    
    # Проверка циклов
    all_cycles = []
    visited = set()
    for node in graph:
        if node not in visited:
            cycles = dfs_with_cycles_detection(graph, node, set(), set(), [], [])
            all_cycles.extend(cycles)
            visited.add(node)
    
    if all_cycles:
        print(f"\nОбнаружены циклические зависимости в {test_name}:")
        for cycle in all_cycles:
            print(f"Цикл: {' -> '.join(cycle)} -> {cycle[0]}")
    else:
        print(f"\nЦиклические зависимости в {test_name} не обнаружены")
    
    # Транзитивные зависимости
    print(f"\nТранзитивные зависимости {test_name}:")
    for package in sorted(graph.keys()):
        all_deps = get_all_dependencies(graph, package, exclude_pattern)
        if all_deps:
            print(f"{package}: {sorted(list(all_deps))}")
        else:
            print(f"{package}: нет зависимостей")

# Создание тестовых файлов
def create_test_files():
    # Простой граф без циклов
    test1_content = """
A:
  - B
  - C
B:
  - D
C:
  - D
D:
"""
    
    # Граф с циклом
    test2_content = """
A:
  - B
B:
  - C
C:
  - A
"""
    
    # Сложный граф с исключениями
    test3_content = """
A:
  - B
  - C
B:
  - D
  - EXCLUDE_ME
C:
  - E
D:
  - F
E:
  - B
F:
EXCLUDE_ME:
  - A
"""
    
    with open('test1_simple.yaml', 'w') as f:
        f.write(test1_content)
    with open('test2_cycle.yaml', 'w') as f:
        f.write(test2_content)
    with open('test3_complex.yaml', 'w') as f:
        f.write(test3_content)
    
    print("Созданы тестовые файлы:")
    print("- test1_simple.yaml (простой граф без циклов)")
    print("- test2_cycle.yaml (граф с циклическими зависимостями)")
    print("- test3_complex.yaml (сложный граф с пакетами для исключения)")

# Демонстрация
if __name__ == "__main__":
    create_test_files()
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ АНАЛИЗА ЗАВИСИМОСТЕЙ")
    print("="*60)
    main()
