import click

import kail.structures as strs

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
        trees = strs.TreeWithParent.parse_kai_penn(input_file)
    elif input_format == "kail":
        trees = strs.TreeWithParent.parse_kail(input_file)

    # write trees
    if output_format == "penn":
        if compact:
            # One-line mode

            # Raise out comments
            for tree in list(iter(trees)):
                tree.raise_comments_out()
            # copy needed?

            # Print
            output_file.write(
                "\n".join(
                    filter(
                        None,
                        (
                            tree.print_kai_penn_squeezed(
                                show_comments = comments
                                ) for tree in trees
                        )
                    )
                )
            )
        else:
            # Pretty mode

            # Raise out comments on rightmost-corners
            for tree in list(iter(trees)):
                tree.raise_comments_on_right_corner_one_level_above()
            # copy needed?

            # Print
            output_file.write(
                "\n\n".join(
                    filter(None,
                        (
                            tree.print_kai_penn_indented(
                                show_comments = comments
                                ) for tree in trees
                        )
                    )
                )
            )
    elif output_format == "kail":
        # Pretty mode only
        output_file.write("\n".join(
            tree.print_kail() for tree in trees
            )
        )
    # ===END===

routine()