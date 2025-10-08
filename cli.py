import argparse
import sys
from pathlib import Path

from parse import parse, InvalidSyntax
from optimize import optimize
from gen import generate


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Can't read file {path}: {e}", file=sys.stderr)
        sys.exit(1)


def write_file(path: Path, data: str) -> None:
    try:
        path.write_text(data, encoding="utf-8")
    except Exception as e:
        print(f"Can't write file {path}: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_parse(args):
    src = read_file(Path(args.input))
    try:
        ir = parse(src)
    except InvalidSyntax as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    for instr in ir:
        print(instr)


def cmd_optimize(args):
    src = read_file(Path(args.input))
    try:
        ir = parse(src)
    except InvalidSyntax as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    opt_ir = optimize(ir)
    for instr in opt_ir:
        print(instr)


def cmd_compile(args):
    src = read_file(Path(args.input))
    try:
        ir = parse(src)
    except InvalidSyntax as e:
        print(e, sys.stderr)
        sys.exit(1)
    ir = optimize(ir)
    c_code = generate(ir)
    if args.output:
        write_file(Path(args.output), c_code)
    else:
        print(c_code)


def cmd_run(args):
    src = read_file(Path(args.input))
    try:
        ir = parse(src)
    except InvalidSyntax as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    ir = optimize(ir)
    code = generate(ir)
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        c_path = Path(tmp) / "out.c"
        exe_path = Path(tmp) / "out"
        c_path.write_text(code, encoding="utf-8")
        cc = ["cc", "-O2", str(c_path), "-o", str(exe_path)]
        try:
            subprocess.run(cc, check=True)
        except subprocess.CalledProcessError:
            print("Compilation failed", file=sys.stderr)
            sys.exit(1)
        try:
            subprocess.run([str(exe_path)])
        except KeyboardInterrupt:
            pass


def main():
    pass


if __name__ == "__main__":
    main()
