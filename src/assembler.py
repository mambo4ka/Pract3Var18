import argparse
import json
from pathlib import Path

SPEC = {
    'LOAD_CONST': {'opcode': 0, 'size': 6, 'fields': [('A', 0, 3),
        ('B', 3, 17), ('C', 20, 22)]},
    'READ_MEM': {'opcode': 1, 'size': 5, 'fields': [('A', 0, 3),
        ('B', 3, 17), ('C', 20, 17)]},
    'WRITE_MEM': {'opcode': 6, 'size': 5, 'fields': [('A', 0, 3),
        ('B', 3, 17), ('C', 20, 17)]},
    'SHR': {'opcode': 5, 'size': 7, 'fields': [('A', 0, 3),
        ('B', 3, 17), ('C', 20, 17), ('D', 37, 17)]},
}
ALIASES = {'LOAD_CONST': 'LOAD_CONST', 'LOAD': 'LOAD_CONST',
    'READ_MEM': 'READ_MEM', 'READ': 'READ_MEM',
    'WRITE_MEM': 'WRITE_MEM', 'WRITE': 'WRITE_MEM',
    'SHR': 'SHR', 'LOGICAL_RIGHT_SHIFT': 'SHR'}


def parse_source(path):
    program = []
    lines = Path(path).read_text(
        encoding='utf-8'
    ).splitlines()
    for line_no, raw_line in enumerate(lines, 1):
        line = raw_line.split('#', 1)[0]
        line = line.split(';', 1)[0].strip()
        if not line:
            continue
        parts = line.replace(',', ' ').split()
        mnemonic = parts[0].upper()
        if mnemonic not in ALIASES:
            raise ValueError(
                f'Line {line_no}: unknown command {mnemonic}'
            )
        mnemonic = ALIASES[mnemonic]
        expected = [
            field[0] for field in SPEC[mnemonic]['fields']
        ][1:]
        operands = parts[1:]
        values = {}
        if operands and all('=' in item for item in operands):
            for item in operands:
                name, value = item.split('=', 1)
                values[name.upper()] = parse_int(
                    value, line_no
                )
            if set(values) != set(expected):
                raise ValueError(
                    f'Line {line_no}: expected fields {expected}'
                )
        else:
            if len(operands) != len(expected):
                raise ValueError(
                    f'Line {line_no}: {mnemonic} expects '
                    f'{len(expected)} operands'
                )
            values = {
                name: parse_int(value, line_no)
                for name, value in zip(expected, operands)
            }
        command = {
            'name': mnemonic,
            'line': line_no,
            'A': SPEC[mnemonic]['opcode'],
        }
        command.update(values)
        program.append(command)
    return program

def parse_int(value, line_no):
    try:
        return int(value, 0)
    except ValueError as error:
        message = f'Line {line_no}: invalid integer {value!r}'
        raise ValueError(message) from error



def to_ir(program):
    result = []
    for item in program:
        name = item['name'].upper()
        if name not in SPEC:
            raise ValueError(f"Unknown command: {name}")
        spec = SPEC[name]
        record = {'command': name, 'size': spec['size'], 'fields': {}}
        for field, offset, width in spec['fields']:
            value = item.get(field, spec['opcode'] if field == 'A' else None)
            if value is None:
                raise ValueError(f'{name}: missing field {field}')
            if not 0 <= value < (1 << width):
                raise ValueError(f'{name}: {field} must fit in {width} bits')
            record['fields'][field] = {'value': value, 'offset': offset,
                'width': width}
        result.append(record)
    return result


def encode(ir):
    output = bytearray()
    for command in ir:
        packed = 0
        for field in command['fields'].values():
            packed |= field['value'] << field['offset']
        output.extend(packed.to_bytes(command['size'], 'little'))
    return bytes(output)


def print_test(ir):
    for index, command in enumerate(ir, 1):
        print(f"Тест {index}: {command['command']} ({command['size']} байт)")
        for name, data in command['fields'].items():
            print(f"  {name}: значение={data['value']}, "
                  f"смещение={data['offset']}, ширина={data['width']}")


def main():
    description = 'Assembler for VM, variant 18'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', help='Assembly source file')
    parser.add_argument('output', help='Output binary file')
    parser.add_argument('--test', action='store_true',
        help='Print field/value IR instead of writing binary')
    args = parser.parse_args()
    ir = to_ir(parse_source(args.input))
    if args.test:
        print_test(ir)
    else:
        Path(args.output).write_bytes(encode(ir))
        print(f'Binary written to {args.output} ({len(encode(ir))} bytes)')


if __name__ == '__main__':
    main()
