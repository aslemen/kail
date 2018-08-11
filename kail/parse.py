import re
import io
import pathlib

from nltk.tree import ParentedTree as pt
import nltk.corpus as corp

import typing as typ

from . import structures as strs
lbcx = strs.Label_Complex_with_Pos
orc = strs.Object_with_Row_Column

def convert_kai_penn_tree_file(path: str) -> typ.List[pt]:
    sents_raw = corp.BracketParseCorpusReader(
            root = "",
            fileids = path
                ).parsed_sents()

    for sent in sents_raw:
        sent_pt: pt = pt.convert(sent)

        def traverse_parse(tree):
            res = None

            if isinstance(tree, pt):

                for i in range(len(tree)):
                    tree[i] = traverse_parse(tree[i])

                tree.set_label(lbcx.parse_from_kai_penn(tree.label()))
                res = tree
            else:
                res = pt(
                    node = lbcx(
                            label = orc(str(tree), -1, 0),
                            ICHed = orc(0, -1, -1),
                            sort_info = orc("", -1, -1)
                            ),
                    children = []
                )
            return res

        sent_pt = traverse_parse(sent_pt)

        yield sent_pt

def parse_kail(stream: io.TextIOBase) -> typ.List[pt]:
    indent: typ.List[int] = [-1]

    res_tree: pt = pt(None, children = [])
    node_pointer: pt = res_tree

    re_indent: "_sre.SRE_Match" = re.compile(r"[ \t]*")

    for row, line_raw in enumerate(stream):
        # ======
        # Strip out redundant whitespaces on the right side
        # ======
        line: str = line_raw.rstrip()

        # ======
        # Strip out comments
        # ======

        # ======
        # Firstly, check whether the line is empty
        # ======
        if line == "": continue

        # ======
        # The line being non-empty, find the indent
        # ======

        # Extract the indent
        current_indent_raw: "_sre.SRE_PATTERN" = re_indent.match(line)

        # Count the indent
        current_indent: int = 0

        for char in current_indent_raw.group(0):
            if char == r"\t":
                current_indent += 2
            else:
                current_indent += 1

        # ======
        # find the items for label complex
        # ======
        current_label_complex: lbcx = strs.Label_Complex_with_Pos.parse_from_kail(line, row)

        # ======
        # Create a chile node
        # ======
        current_node = pt(current_label_complex, children = [])

        # ======
        # Position the label in a tree
        # ======

        # Detect embedding / de-embedding
        previous_indent: int = indent[-1]

        if current_indent > previous_indent:
            node_pointer.append(current_node)

            # record the current indent
            indent.append(current_indent)

        elif current_indent == previous_indent:
            # keep on that tree depth
            # make a sibling
            current_node = pt(current_label_complex, children = [])
            node_pointer.parent().append(current_node)

        else:
            # go back to the parent

            # find the anchor
            while True:
                # discard the previous indent
                indent.pop()
                # make the pointer point to the ancestor
                node_pointer = node_pointer.parent()

                # get the indent of the ancestor
                parent_indent = indent[-1]

                if current_indent > parent_indent:
                    raise SyntaxError(
                        "An unanchorable indent is found " \
                        "at Line {row_add}, Column {col_add}".format(
                            row_add = row + 1,
                            col_add = current_label_complex.label.column + 1
                            )
                    )
                elif current_indent == parent_indent:
                    # anchor the current node NEXT TO the ancestor
                    # make a sibling
                    current_node = pt(current_label_complex, children = [])
                    node_pointer.parent().append(current_node)

                    # stop searching
                    break
                else: pass # search further
            
            # ===END WHILE===

        # Set the pointer to the newly created node
        node_pointer = current_node

        # ===END FOR===
    
    return res_tree

    # ===END===