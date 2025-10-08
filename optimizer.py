from typing import List
from bfir import BFIR, Zero, Add, Loop


def optimize(ir: List[BFIR]) -> List[BFIR]:
    def is_zero_loop(loop: Loop) -> bool:
        if len(loop.body) != 1:
            return False
        only = loop.body[0]
        return isinstance(only, Add) and abs(only.delta) == 1

    return ir
