# Парсер YAML
def parse_yaml(content):
    lines = content.split('\n')
    result = {}
    current_key = None
    current_list = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.endswith(':'):
            current_key = line[:-1].strip()
            result[current_key] = []
            current_list = result[current_key]
        elif line.startswith('-'):
            if current_list is not None:
                item = line[1:].strip()
                current_list.append(item)
    
    return result

# Построение графа зависимостей с помощью DFS
def build_dependency_graph(data, exclude_pattern=None):
    graph = {}
    
    for package, deps in data.items():
        if exclude_pattern and exclude_pattern in package:
            continue
        graph[package] = [dep for dep in deps if not exclude_pattern or exclude_pattern not in dep]
    
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

# Получение всех зависимостей (транзитивное замыкание)
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
            dfs(dep)
    
    dfs(package)
    visited.discard(package)
    return visited

# Основная функция
def main():
    print("=== Анализатор зависимостей пакетов ===")
    print("Режимы работы:")
    print("1 - Тестовый режим (файл)")
    print("2 - Продакшен режим (URL)")
    
    mode = input("Выберите режим: ").strip()
    
    if mode == "1":
        file_path = input("Введите путь к файлу: ").strip()
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            data = parse_yaml(content)
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
            for package in graph:
                all_deps = get_all_dependencies(graph, package, exclude_pattern)
                if all_deps:
                    print(f"{package}: {sorted(list(all_deps))}")
            
        except Exception as e:
            print(f"Ошибка: {e}")
    
    elif mode == "2":
        print("Режим URL будет реализован позже")
    else:
        print("Неверный режим")

# Тестовые данные
def create_test_file():
    test_data = """
A:
  - B
  - C

B:
  - C
  - D

C:
  - E

D:
  - A
  - F

E:
  - B

F:
  - G

G:
  - H

H:
"""
    
    with open('test_repo.yaml', 'w') as f:
        f.write(test_data)
    print("Создан тестовый файл: test_repo.yaml")

# Демонстрация
if __name__ == "__main__":
    create_test_file()
    print("Демонстрация работы системы:")
    print("=" * 50)
    main()
