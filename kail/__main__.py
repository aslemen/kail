import click

from . import parse
from . import output

@click.command()
@click.option(
    "--input_format", "-i",
    type = click.Choice(["penn", "kail"]),
    default = "penn"
)
@click.option(
    "--output_format", "-o",
    type = click.Choice(["penn", "kail"]),
    default = "penn"
)
@click.option(
    "--comments/--no_comments",
    default = True
)
@click.option(
    "--compact/--pretty",
    default = False
)
@click.option(
    "--input_file", "-r",
    type = click.File(mode = 'r'),
    default = "-"
)
@click.option(
    "--output_file", "-w",
    type = click.File(mode = 'w'),
    default = "-"
)
def routine(
        input_format,
        output_format,
        input_file, 
        output_file, 
        comments, 
        compact
        ):
    # read trees
    trees = None
    
    if input_format == "penn":
        trees = parse.parse_kai_penn(input_file)
    elif input_format == "kail":
        trees = parse.parse_kail(input_file)

    # write trees
    if output_format == "penn":
        if compact:
            output_file.write(
                "\n\n".join(
                    output.print_kai_penn_squeezed(
                        tree
                        ) for tree in trees
                )
            )
        else:
            output_file.write(
                "\n\n".join(
                    output.print_kai_penn_indented(
                        tree, 
                        show_comments = comments
                        ) for tree in trees
                )
            )
    elif output_format == "kail":
        output_file.write("\n".join(
            output.print_kail(tree) for tree in trees)
            )
    # ===END===