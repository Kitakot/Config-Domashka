import sys
import xml.etree.ElementTree as ET


# Функция преобразования команды в бинарный формат
def assemble_command(operation, b, c, d=0):
    opcodes = {"LOAD": 55, "READ": 119, "WRITE": 80, "SQRT": 43}
    a = opcodes[operation]
    # Формируем 11-байтную команду
    command = (a & 0x7F) << 72 | (b & 0xFFFFFF) << 48 | (c & 0xFFFFFF) << 24 | (d & 0x1FF)
    return command.to_bytes(11, byteorder='big')


# Основная функция ассемблера
def assembler(input_file, output_bin, log_file):
    commands = []
    log_root = ET.Element("log")

    # Читаем текстовую программу
    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            operation = parts[0]
            b = int(parts[1])
            c = int(parts[2])
            d = int(parts[3]) if len(parts) > 3 else 0

            # Преобразуем команду в бинарный формат
            binary_command = assemble_command(operation, b, c, d)
            commands.append(binary_command)

            # Логгируем инструкцию
            instruction = ET.SubElement(log_root, "instruction")
            ET.SubElement(instruction, "operation").text = operation
            ET.SubElement(instruction, "A").text = str({"LOAD": 55, "READ": 119, "WRITE": 80, "SQRT": 43}[operation])
            ET.SubElement(instruction, "B").text = str(b)
            ET.SubElement(instruction, "C").text = str(c)
            if d:
                ET.SubElement(instruction, "D").text = str(d)
            ET.SubElement(instruction, "encoded").text = ' '.join(f'0x{byte:02X}' for byte in binary_command)

    # Сохраняем бинарный файл
    with open(output_bin, "wb") as bin_file:
        for command in commands:
            bin_file.write(command)

    # Сохраняем лог в формате XML
    tree = ET.ElementTree(log_root)
    with open(log_file, "wb") as log_file:
        tree.write(log_file)


# Запуск программы
if __name__ == "__main__":
    input_program = sys.argv[1]
    output_binary = sys.argv[2]
    log_output = sys.argv[3]
    assembler(input_program, output_binary, log_output)
