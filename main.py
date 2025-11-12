import requests
import sys

def parse_value(line):
    """Парсит значение из строки YAML"""
    return line.split(':', 1)[1].strip().strip('"\'') if ':' in line else ""

def load_config():
    """Загрузка конфигурации из YAML файла"""
    config = {}
    
    print("=== Этап 1: Конфигурация ===")
    print("Параметры файла config.yaml:")
    
    try:
        with open("config.yaml", "r", encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('package_name:'):
                    value = parse_value(line)
                    if value:
                        config['package_name'] = value
                        print(f"package_name: {value}")
                    else:
                        print("Ошибка: Пустое значение поля package_name")
                        return None
                        
                elif line.startswith('repository_url:'):
                    value = parse_value(line)
                    if value:
                        config['repository_url'] = value
                        print(f"repository_url: {value}")
                    else:
                        print("Ошибка: Пустое значение поля repository_url")
                        return None
                        
                elif line.startswith('test_repository_mode:'):
                    value = parse_value(line).lower()
                    if value in ['true', 'false']:
                        config['test_repository_mode'] = value == 'true'
                        print(f"test_repository_mode: {value}")
                    else:
                        print("Ошибка: Некорректное значение test_repository_mode")
                        return None
                        
                elif line.startswith('output_image_filename:'):
                    value = parse_value(line)
                    if value:
                        config['output_image_filename'] = value
                        print(f"output_image_filename: {value}")
                    else:
                        print("Ошибка: Пустое значение поля output_image_filename")
                        return None
                        
                elif line.startswith('ascii_tree_mode:'):
                    value = parse_value(line).lower()
                    if value in ['true', 'false']:
                        config['ascii_tree_mode'] = value == 'true'
                        print(f"ascii_tree_mode: {value}")
                    else:
                        print("Ошибка: Некорректное значение ascii_tree_mode")
                        return None
                        
                elif line.startswith('filter_substring:'):
                    value = parse_value(line)
                    if value:
                        config['filter_substring'] = value
                        print(f"filter_substring: {value}")
                    else:
                        config['filter_substring'] = ""
                        print("filter_substring: фильтр не задан")
        
        print("=== Конфигурация загружена успешно ===\n")
        return config
        
    except FileNotFoundError:
        print("Ошибка: Файл config.yaml не найден")
        return None
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}")
        return None

def get_nuget_dependencies(package_name, repository_url):
    """Получение зависимостей из NuGet репозитория"""
    print("=== Этап 2: Сбор данных ===")
    print(f"Анализ пакета: {package_name}")
    print(f"Репозиторий: {repository_url}")
    
    try:
        # Получаем базовый URL API
        response = requests.get(repository_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        resources = data.get('resources', [])
        
        search_url = None
        for resource in resources:
            if resource.get('@type') == 'SearchQueryService':
                search_url = resource['@id']
                break
        
        if not search_url:
            print("Ошибка: Не найден SearchQueryService в репозитории")
            return []
        
        # Ищем пакет
        search_response = requests.get(f"{search_url}?q=packageid:{package_name}", timeout=10)
        search_response.raise_for_status()
        
        search_data = search_response.json()
        
        if not search_data.get('data'):
            print(f"Ошибка: Пакет '{package_name}' не найден")
            return []
        
        package_info = search_data['data'][0]
        versions = package_info.get('versions', [])
        
        if not versions:
            print(f"Ошибка: Не найдены версии для пакета '{package_name}'")
            return []
        
        # Берем последнюю версию
        latest_version = versions[-1]
        version_url = latest_version['@id']
        
        # Получаем информацию о версии
        version_response = requests.get(version_url, timeout=10)
        version_response.raise_for_status()
        
        version_data = version_response.json()
        
        # Извлекаем зависимости
        dependencies = []
        catalog_entry = version_data.get('catalogEntry', {})
        dependency_groups = catalog_entry.get('dependencyGroups', [])
        
        for group in dependency_groups:
            group_dependencies = group.get('dependencies', [])
            for dep in group_dependencies:
                dep_id = dep.get('id')
                if dep_id and dep_id not in dependencies:
                    dependencies.append(dep_id)
        
        return dependencies
        
    except requests.RequestException as e:
        print(f"Ошибка сети: {e}")
        return []
    except Exception as e:
        print(f"Ошибка при получении зависимостей: {e}")
        return []

def main():
    """Основная функция"""
    
    # Этап 1: Загрузка конфигурации
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Этап 2: Получение зависимостей
    dependencies = get_nuget_dependencies(
        config['package_name'], 
        config['repository_url']
    )
    
    # Вывод результатов
    print("\nПрямые зависимости пакета:")
    if dependencies:
        for i, dep in enumerate(dependencies, 1):
            print(f"{i}. {dep}")
        print(f"\nВсего найдено зависимостей: {len(dependencies)}")
    else:
        print("Зависимости не найдены или произошла ошибка")

if __name__ == "__main__":
    main()
