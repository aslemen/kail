import re
import itertools

from nltk.tree import ParentedTree as pt

from . import structures as strs

import typing

def print_kai_penn_indented(tree: pt, indent: int = 0) -> str:
    """
        Generate the well-indented representation of this tree, given the overall indent

        Parameters
        ----------
        indent: int, default 0
            the overall indent.

        Returns
        -------
        indented_tree: str
            the indented tree representation
    """
    label_object: str = tree.label()
    self_label_raw: str = None

    if isinstance(label_object, strs.Label_Complex_with_Pos):
        self_label_raw = label_object.print_kai_penn()
    else:
        self_label_raw = str(label_object)

    if len(tree) == 0:
        # if this is a terminal node
        return " " * indent + self_label_raw
    else:
        # if this is a non-terminal node

        # get the representation of the subtrees
        ## note: calculation of the indent for the second and latter subtrees
        ## ................. (labellabellabel..........label (..... 
        ## ^===[indent]=====^_^====[len(self.label)]=======^_^----------
        str_subtrees: typing.List[str] = [
                                print_kai_penn_indented(
                                    st,
                                    indent = indent \
                                              + 1 \
                                              + len(self_label_raw) \
                                              + 1
                                    )
                                for st in tree
                                ]

        # cut out the spaces at the beginning of the first subtree
        str_subtrees[0] = str_subtrees[0].lstrip()

        # generate
        return "{indent}({label} {subtrees})".format(
                    indent = " " * indent,
                    label = self_label_raw,
                    subtrees = "\n".join(str_subtrees)
                    )

def print_kai_penn_squeezed(tree: pt) -> str:
    """
        Generate the one-line representation of this tree, given the overall indent.

        Parameters
        ----------
        indent: int, default 0
            the overall indent.

        Returns
        -------
        indented_tree: str
            the one-line tree representation
    """

    return re.sub(
        r"\s+",
        repl = " ",
        string = print_kai_penn_indented(tree)
        )

def print_kail(tree: pt, indent_amount: int = 2, indent: int = 0) -> str:
    """
        Generate the representation of this tree
        in the Kail style.

        Parameters
        ----------
        indent: int, default 0
            the overall indent.

        Returns
        -------
        indented_tree: str
            the one-line tree representation
    """
    label_object: str = tree.label()
    self_label_raw: str = None

    if isinstance(label_object, strs.Label_Complex_with_Pos):
        self_label_raw = label_object.print_kail()
    else:
        self_label_raw = str(label_object)

    return (" " * indent) + "\n".join(
                    itertools.chain(
                        (self_label_raw, ),
                        map(
                            lambda subtree: print_kail(
                                subtree,
                                indent_amount = indent_amount,
                                indent = indent + indent_amount
                                ),
                            tree
                        )
                    )
    )