import click
from pathlib import Path
import subprocess
import tempfile
from parser import parse
from optimizer import optimize
from codegen import generate


@click.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--show", is_flag=True, help="Show the intermediate steps in console")
@click.option("--ir", is_flag=True, help="Outputs the  intermediate IR file")
@click.option("--c", is_flag=True, help="Outputs the C code file")
@click.option("--s", is_flag=True, help="Outputs the Assembly file")
@click.option("--no", is_flag=True, help="No Optimizations")
@click.option("--exe", is_flag=True, help="Generates the executable")
def cli(source, show, ir, c, s, no, exe):
    source_path = Path(source)
    ext = source_path.suffix.lower()
    save_dir = source_path.parent

    if not (ir or c or s or exe):
        exe = True

    if ext == ".b":
        bf_code = source_path.read_text()
        ir_data = parse(bf_code)
        if not no:
            ir_data = optimize(ir_data)
        if show:
            click.echo("=== IR ===")
            click.echo(ir_data)
    elif ext == ".bfir":
        ir_data = eval(source_path.read_text())
        if not no:
            ir_data = optimize(ir_data)
        if show:
            click.echo("=== IR ===")
            click.echo(ir_data)
    else:
        raise click.ClickException("Input file must be .b or .bfir")

    if ir:
        ir_path = save_dir / (source_path.stem + ".bfir")
        ir_path.write_text(str(ir_data))

    if not (c or s or exe):
        return

    c_code = generate(ir_data)
    c_path = save_dir / (source_path.stem + ".c") if c else None
    if c_path:
        c_path.write_text(c_code)
    else:
        tmp_c = tempfile.NamedTemporaryFile(delete=False, suffix=".c")
        tmp_c.write(c_code.encode())
        tmp_c.close()
        c_path = Path(tmp_c.name)
    if show:
        click.echo("=== C Code ===")
        click.echo(c_code)

    if not (s or exe):
        return

    asm_path = (
        save_dir / (source_path.stem + ".s")
        if s
        else Path(tempfile.NamedTemporaryFile(delete=False, suffix=".s").name)
    )
    subprocess.run(["clang", "-S", str(c_path), "-o", str(asm_path)], check=True)

    if show:
        asm_code = asm_path.read_text()
        click.echo("=== Assembly ===")
        click.echo(asm_code)

    if exe:
        exe_path = save_dir / (source_path.stem + ".exe")
        subprocess.run(["clang", str(c_path), "-o", str(exe_path)], check=True)

    if c_path and not c:
        c_path.unlink()
    if asm_path and not s:
        asm_path.unlink()


if __name__ == "__main__":
    cli()
