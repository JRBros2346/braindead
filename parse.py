from typing import List, Dict
from bfir import BFIR, Add, Move, Output, Input, Debug, Loop

RED = "\033[31m"
RESET = "\033[m"


class InvalidSyntax(Exception):
    def __init__(self, errors: Dict[int, tuple[str, List[int]]]):
        self.errors = errors

    def __str__(self) -> str:
        padding = max(map(lambda n: len(str(n)), self.errors.keys()))
        out_lines = []
        for line_num in sorted(self.errors.keys()):
            line, cols = self.errors[line_num]
            colored = ""
            for i, ch in enumerate(line, start=1):
                if i in cols:
                    if i - 1 in cols:
                        colored += f"{ch}"
                    else:
                        colored += f"{RED}{ch}"
                else:
                    if i - 1 in cols:
                        colored += f"{RESET}{ch}"
                    else:
                        colored += f"{ch}"
            colored += RESET
            out_lines.append(f" {line_num:>{padding}} | {colored}")
        return "\n".join(out_lines)


def parse(src: str) -> List[BFIR]:
    source_lines = src.splitlines() if src else [""]
    bracket_stack: List[tuple[int, int]] = []
    errors: Dict[int, tuple[str, List[int]]] = {}
    line_num = 1
    col_num = 1
    ir: List[List[BFIR]] = [[]]

    for char in src:
        if char == "\n":
            line_num += 1
            col_num = 1
            continue

        current_body = ir[-1]

        match char:
            case "+" | "-":
                delta = 1 if char == "+" else -1
                if current_body and isinstance(current_body[-1], Add):
                    current_body[-1].delta += delta
                    if current_body[-1].delta == 0:
                        current_body.pop()
                else:
                    current_body.append(Add(delta))
            case ">" | "<":
                offset = 1 if char == ">" else -1
                if current_body and isinstance(current_body[-1], Move):
                    current_body[-1].offset += offset
                    if current_body[-1].offset == 0:
                        current_body.pop()
                else:
                    current_body.append(Move(offset))
            case ".":
                current_body.append(Output())
            case ",":
                current_body.append(Input())
            case "#":
                current_body.append(Debug())
            case "[":
                bracket_stack.append((line_num, col_num))
                new_loop = Loop(body=[])
                current_body.append(new_loop)
                ir.append(new_loop.body)
            case "]":
                if not bracket_stack:
                    if line_num not in errors:
                        errors[line_num] = (source_lines[line_num - 1], [])
                    errors[line_num][1].append(col_num)
                else:
                    bracket_stack.pop()
                    ir.pop()
            case _:
                continue

        col_num += 1

    for err_line, err_col in bracket_stack:
        if err_line not in errors:
            errors[err_line] = (source_lines[err_line - 1], [])
        errors[err_line][1].append(err_col)

    if errors:
        raise InvalidSyntax(errors)

    return ir[0]


try:
    parse("]\n]]" + "\n" * 924924 + "++>++++++[->++++++++++<]>.[][][[]")
except Exception as e:
    print(e)
