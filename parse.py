from typing import List
from bfir import BFIR, Add, Move, Output, Input, Debug, Loop


class InvalidSyntax(Exception):
    def __init__(self, errors: List["InvalidSyntax"] = []):
        if not errors:
            super().__init__()
            return
        self.errors = errors
        super().__init__(self.gen_report())

    def gen_report(self) -> str:
        error_count = len(self.errors)
        plural = "s" if error_count > 1 else ""
        header = f"{error_count} Error{plural}:\n"
        reports = "\n\n\n".join(str(e) for e in self.errors)
        return header + reports


class UnmatchedClosingBracket(InvalidSyntax):
    def __init__(self, line_num: int, col_num: int, line_content: str):
        self.line_num = line_num
        self.col_num = col_num
        self.line_content = line_content.replace("\t", "    ")

    def __str__(self) -> str:
        pointer = " " * (self.col_num - 1) + "^--- Here"
        padding = " " * len(str(self.line_num))
        return (
            f"Unmatched closing bracket ']' at line {self.line_num}, column {self.col_num}:\n"
            f" {self.line_num} | {self.line_content}\n"
            f" {padding} | {pointer}"
        )


class UnclosedOpeningBracket(InvalidSyntax):
    def __init__(self, line_num: int, col_num: int, line_content: str):
        self.line_num = line_num
        self.col_num = col_num
        self.line_content = line_content.replace("\t", "    ")

    def __str__(self) -> str:
        pointer = " " * (self.col_num - 1) + "^--- Here"
        padding = " " * len(str(self.line_num))
        return (
            f"This opening bracket '[' at line {self.line_num}, column {self.col_num} was never closed:\n"
            f" {self.line_num} | {self.line_content}\n"
            f" {padding} | {pointer}"
        )


def validate(src: str):
    source_lines = src.splitlines() if src else [""]
    bracket_stack: List[tuple[int, int]] = []
    errors: List[InvalidSyntax] = []
    line_num = 1
    col_num = 1
    for char in src:
        if char == "[":
            bracket_stack.append((line_num, col_num))
        elif char == "]":
            if not bracket_stack:
                line_content = source_lines[line_num - 1] if source_lines else ""
                errors.append(UnmatchedClosingBracket(line_num, col_num, line_content))
            else:
                bracket_stack.pop()
        if char == "\n":
            line_num += 1
            col_num = 1
        else:
            col_num += 1
    for err_line, err_col in bracket_stack:
        line_content = source_lines[err_line - 1] if source_lines else ""
        errors.append(UnclosedOpeningBracket(err_line, err_col, line_content))
    if errors:
        raise InvalidSyntax(errors)


def parse(src: str) -> List[BFIR]:
    validate(src)
    stack: List[List[BFIR]] = [[]]

    for char in src:
        current_body = stack[-1]

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
                new_loop = Loop(body=[])
                current_body.append(new_loop)
                stack.append(new_loop.body)
            case "]":
                if len(stack) == 1:
                    raise InvalidSyntax()
                stack.pop()
            case _:
                continue

    if len(stack) != 1:
        raise InvalidSyntax()

    return stack[0]


print(parse("]" + "\n" * 10000 + "--][["))
