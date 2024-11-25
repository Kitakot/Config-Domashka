import os
import subprocess
import argparse
from pathlib import Path


def get_git_commit_graph(repo_path):
    """
    Получает граф зависимостей коммитов в репозитории.
    Возвращает текстовое представление для PlantUML.
    """
    os.chdir(repo_path)
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H %P"],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    lines = result.stdout.strip().split("\n")
    edges = []

    for line in lines:
        parts = line.split()
        commit = parts[0]
        parents = parts[1:]
        for parent in parents:
            edges.append((commit, parent))

    # Создание графа в формате PlantUML
    plantuml_content = "@startuml\n"
    for edge in edges:
        plantuml_content += f'  "{edge[0]}" --> "{edge[1]}"\n'
    plantuml_content += "@enduml\n"

    return plantuml_content


def save_plantuml_file(content, file_path):
    """
    Сохраняет содержимое PlantUML в файл.
    """
    with open(file_path, "w") as file:
        file.write(content)


def generate_graph_image(plantuml_path, plantuml_file, output_file):
    """
    Генерирует изображение графа с помощью PlantUML.
    """
    # Используем java -jar для выполнения JAR-файла
    subprocess.run(
        ["java", "-jar", plantuml_path, plantuml_file],
        check=True
    )
    # Перемещение сгенерированного файла в нужное место
    generated_file = Path(plantuml_file).with_suffix(".png")
    if generated_file.exists():
        generated_file.rename(output_file)
    else:
        raise FileNotFoundError(f"Файл {generated_file} не был создан.")


def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей Git.")
    parser.add_argument(
        "--plantuml_path",
        required=True,
        help="Путь к программе PlantUML (например, jar-файл)."
    )
    parser.add_argument(
        "--repo_path",
        required=True,
        help="Путь к анализируемому Git-репозиторию."
    )
    parser.add_argument(
        "--output_file",
        required=True,
        help="Путь к файлу, куда будет сохранено изображение графа."
    )

    args = parser.parse_args()

    # Проверка путей
    if not os.path.exists(args.repo_path):
        print("Ошибка: Указанный репозиторий не существует.")
        return

    if not os.path.isfile(args.plantuml_path):
        print("Ошибка: Указанный файл PlantUML не найден.")
        return

    # Генерация графа зависимостей
    print("Сбор данных о зависимостях...")
    plantuml_content = get_git_commit_graph(args.repo_path)

    # Сохранение файла PlantUML
    plantuml_file = "dependency_graph.puml"
    save_plantuml_file(plantuml_content, plantuml_file)

    # Генерация изображения
    print("Генерация изображения графа...")
    generate_graph_image(args.plantuml_path, plantuml_file, args.output_file)

    print(f"Граф успешно сохранён в {args.output_file}")


if __name__ == "__main__":
    main()
