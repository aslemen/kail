import click
import pathlib
import sys

from . import parse
from . import output

@click.group()
def routine(): pass

@routine.command(name = "simplize")
@click.argument("path",
        type = click.Path(
            exists = True,
            resolve_path = True
            ))
def kai_penn_to_kail(path):
    print(str(pathlib.Path(path).resolve()))
    trees = parse.convert_kai_penn_tree_file(
        [str(pathlib.Path(path).resolve())]
        )

    print("\n".join(output.print_kail(tree) for tree in trees))

@routine.command(name = "recover")
def kail_to_kai_penn():
    trees = parse.parse_kail(sys.stdin)
    print("\n\n".join(output.print_kai_penn_indented(tree) for tree in trees))


routine()