import argparse
import json
import re
import sys


NAME_PATTERN = re.compile(r'^[A-Z]+$')
CONST_EXPR_PATTERN = re.compile(r'\|([+\-*/]|min|pow) [A-Z0-9 ]+\|')

def parse_args():
    parser = argparse.ArgumentParser(description="JSON to config language translator.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file path.")
    parser.add_argument("-o", "--output", required=True, help="Output file path.")
    return parser.parse_args()

def evaluate_expression(expr):
    try:
        if expr.startswith('|+'):
            _, *args = expr[1:-1].split()
            return sum(map(int, args))
        elif expr.startswith('|-'):
            _, *args = expr[1:-1].split()
            return int(args[0]) - sum(map(int, args[1:]))
        elif expr.startswith('|*'):
            _, *args = expr[1:-1].split()
            result = 1
            for arg in args:
                result *= int(arg)
            return result
        elif expr.startswith('|/'):
            _, *args = expr[1:-1].split()
            result = int(args[0])
            for arg in args[1:]:
                result //= int(arg)  # Используем целочисленное деление
            return result
        elif expr.startswith('|min'):
            _, *args = expr[1:-1].split()
            return min(map(int, args))
        elif expr.startswith('|pow'):
            _, base, exp = expr[1:-1].split()
            return pow(int(base), int(exp))
        else:
            raise ValueError(f"Unsupported expression: {expr}")
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expr}': {e}")

def json_to_config(data, indent=0):
    output = []
    if isinstance(data, dict):
        output.append("{")
        for key, value in data.items():
            if not NAME_PATTERN.match(key):
                raise ValueError(f"Invalid name '{key}' in dictionary.")
            formatted_value = json_to_config(value, indent + 2)
            output.append(f'{" " * (indent + 2)}{key} : {formatted_value},')
        output[-1] = output[-1][:-1]
        output.append(" " * indent + "}")
    elif isinstance(data, int):
        output.append(str(data))
    elif isinstance(data, str):
        if CONST_EXPR_PATTERN.match(data):
            output.append(str(evaluate_expression(data)))
        else:
            raise ValueError(f"Invalid constant expression '{data}'.")
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")
    return "\n".join(output)

def main():
    args = parse_args()
    try:
        with open(args.input, "r") as f:
            input_data = json.load(f)
        config_output = json_to_config(input_data)
        with open(args.output, "w") as f:
            f.write(config_output)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error decoding JSON: {e}\n")
    except ValueError as e:
        sys.stderr.write(f"Error processing input: {e}\n")
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
