from dataclasses import dataclass
from typing import List


@dataclass
class BFIR:
    pass


@dataclass
class Add(BFIR):
    delta: int

    def __repr__(self) -> str:
        return f"Add({self.delta})"


@dataclass
class Move(BFIR):
    offset: int

    def __repr__(self) -> str:
        return f"Move({self.offset})"


@dataclass
class Output(BFIR):
    def __repr__(self) -> str:
        return "Output"


@dataclass
class Input(BFIR):
    def __repr__(self) -> str:
        return "Input"


@dataclass
class Debug(BFIR):
    def __repr__(self) -> str:
        return "Debug"


@dataclass
class Loop(BFIR):
    body: List[BFIR]

    def __repr__(self) -> str:
        return f"Loop({self.body})"
