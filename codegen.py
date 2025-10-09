from typing import List
from bfir import BFIR, Add, Move, Output, Input, Debug, Loop, MulAdd, Zero, Copy

BASE_INDENT = "    "


def generate(ir: List[BFIR]) -> str:
    def generate_helper(ir: List[BFIR], indent_level: int = 1) -> str:
        code = []
        indent = BASE_INDENT * indent_level
        for node in ir:
            if isinstance(node, Add):
                code.append(f"{indent}cells[ptr] += {node.delta};")
            elif isinstance(node, Move):
                code.append(f"{indent}ptr += {node.offset};")
            elif isinstance(node, Output):
                code.append(f"{indent}putchar(cells[ptr]);")
            elif isinstance(node, Input):
                code.append(f"{indent}cells[ptr] = getchar();")
            # elif isinstance(node, Debug):
            #     code.append(
            #         f'{indent}printf("\\n[DEBUG] ptr=%d val=%d\\n", ptr, cells[ptr]);'
            #     )
            elif isinstance(node, Zero):
                code.append(f"{indent}cells[ptr] = 0;")
            # elif isinstance(node, MulAdd):
            #     for offset, factor in node.ops:
            #         if factor != 0:
            #             code.append(
            #                 f"{indent}cells[ptr + {offset}] += cells[ptr] * {factor};"
            #             )
            #     code.append(f"{indent}cells[ptr] = 0;")
            # elif isinstance(node, Copy):
            #     for offset in node.offsets:
            #         code.append(f"{indent}cells[ptr + {offset}] += cells[ptr];")
            #     code.append(f"{indent}cells[ptr] = 0;")
            elif isinstance(node, Loop):
                code.append(f"{indent}while (cells[ptr]) {{")
                code.append(generate_helper(node.body, indent_level + 1))
                code.append(f"{indent}}}")
            else:
                raise NotImplementedError(f"Unknown IR node: {node}")
        return "\n".join(code)

    return f"""#include<stdio.h>

int main() {{
    unsigned char cells[30000] = {{}};
    int ptr = 0;

    {generate_helper(ir)}

    return 0;
}}
"""
