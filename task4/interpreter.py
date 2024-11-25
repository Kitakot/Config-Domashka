import sys
import xml.etree.ElementTree as ET

# Память УВМ
memory = [0] * 1024  # Ограничение: 1024 ячейки


# Функция для выполнения команды
def execute_command(command):
    a = (command >> 72) & 0x7F
    b = (command >> 48) & 0xFFFFFF
    c = (command >> 24) & 0xFFFFFF
    d = command & 0x1FF

    if a == 55:  # LOAD
        memory[b] = c
    elif a == 119:  # READ
        memory[b] = memory[memory[c]]
    elif a == 80:  # WRITE
        memory[memory[b] + d] = memory[c]
    elif a == 43:  # SQRT
        memory[b] = int(memory[c] ** 0.5)


# Интерпретатор для выполнения программы
def interpreter(input_bin, memory_range, output_file):
    # Загружаем бинарный файл
    with open(input_bin, "rb") as f:
        binary_program = f.read()

    # Выполняем команды из бинарного файла
    for i in range(0, len(binary_program), 11):
        command = int.from_bytes(binary_program[i:i+11], byteorder='big')
        execute_command(command)

    # Сохраняем результат в формате XML
    result_root = ET.Element("result")
    start, end = memory_range
    for addr in range(start, end + 1):
        memory_entry = ET.SubElement(result_root, "memory")
        ET.SubElement(memory_entry, "address").text = str(addr)
        ET.SubElement(memory_entry, "value").text = str(memory[addr])

    tree = ET.ElementTree(result_root)
    with open(output_file, "wb") as result_file:
        tree.write(result_file)


# Запуск программы
if __name__ == "__main__":
    input_binary = sys.argv[1]
    memory_range = list(map(int, sys.argv[2].split("-")))  # Пример: 0-10
    output_result = sys.argv[3]
    interpreter(input_binary, memory_range, output_result)
