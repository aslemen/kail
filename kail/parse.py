import re
import io
import itertools
import pathlib

from nltk.tree import ParentedTree as pt
import nltk.corpus as corp

import typing

from . import structures as strs
lbcx = strs.Label_Complex_with_Pos
orc = strs.Object_with_Row_Column
com = strs.Comment_with_Pos

def convert_kai_penn_tree_file(path: str) -> typing.List[pt]:
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

def __strip_linear_comment_from_line(
            line_raw: str, 
            row: int, 
            node_pointer: pt,
            comment_char: str = ";;"
        ) -> str:
        split_result = line_raw.split(comment_char, 1)

        line_cleared = split_result[0]

        if len(split_result) > 1:
            current_comment_raw = split_result[1]
            current_comment = com(
                                orc(
                                    content = current_comment_raw,
                                    row = row,
                                    column = len(line_cleared)
                                    )
                                )
            node_pointer.append(pt(current_comment, children = []))

        return line_cleared

        # ===END===

def parse_kail(stream: io.TextIOBase) -> typing.List[pt]:
    """
        Parse a text stream in the Kail format.

        Parameters
        ----------
        stream: io.TextIOBase

        Returns
        -------
        trees: List[nltk.tree.ParentedTree]
    """
    indent: typing.List[int] = [-1]

    res_tree: pt = pt(None, children = [])
    node_pointer: pt = res_tree

    re_indent: "_sre.SRE_Match" = re.compile(r"[ \t]*")

    for row, line_raw in enumerate(stream):
        # ======
        # Strip out comments
        # ======
        line_without_comment = __strip_linear_comment_from_line(
                                                line_raw = line_raw.rstrip(),
                                                row = row,
                                                node_pointer = node_pointer,
                                                comment_char = "#"
                                            )

        # ======
        # Firstly, check whether the line is empty
        # ======
        line = line_without_comment.rstrip()

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

def parse_kai_penn(stream: io.TextIOBase) -> typing.List[pt]:
    """
        Parse a text stream in the NPCMJ format.

        Parameters
        ----------
        stream: io.TextIOBase

        Returns
        -------
        trees: List[nltk.tree.ParentedTree]
    """

    def split_line(line: str) -> typing.List[
                                    typing.Tuple[
                                        str,
                                        int
                                        ]
                                    ]:
        # ======
        # go through every character
        # ======
        tokens = []
        token_reading = ""
        token_beginning_num = -1

        def append_and_clear_cache():
            # global token_reading
            # global token_beginning_num
            nonlocal tokens
            nonlocal token_reading
            nonlocal token_beginning_num

            # you got a new token
            tokens.append((token_reading, token_beginning_num))

            token_reading = ""
            token_beginning_num = -1

            # ===END===

        to_be_continued = False

        for column, char in enumerate(line_without_comment):
            if char in " \t\n()":
                if to_be_continued: append_and_clear_cache()

                if char in "()":
                    token_reading += char
                    token_beginning_num = column

                    # immediate tokenization
                    append_and_clear_cache()
                else:
                    # space
                    # do nothing
                    pass

                # ===END IF===
                
                to_be_continued = False
            else:
                # ordinary character
                # record the position of the new token
                token_reading += char
                if not to_be_continued: token_beginning_num = column

                to_be_continued = True

            # ===END IF===
        
        # final appending
        if token_beginning_num > 0: append_and_clear_cache()

        return tokens

    res_tree: pt = pt(None, children = [])
    node_pointer: pt = res_tree

    for row, line_raw in enumerate(stream):
        # ======
        # Strip out comments
        # ======
        line_without_comment = __strip_linear_comment_from_line(
                                                line_raw = line_raw.rstrip(),
                                                row = row,
                                                node_pointer = node_pointer,
                                                comment_char = ";;"
                                            )

        # ======
        # split the line into tokens
        # ======
        tokens = split_line(line_without_comment)

        # ======
        # go through each item
        # ======
        for token, column in tokens:
            if token == "(":
                # new node
                new_node = pt(None, children = [])

                node_pointer.append(new_node)

                # move the pointer
                node_pointer = new_node
            elif token == ")":
                # go back to the parent node

                # if the current node has no label
                # create an empty one
                if node_pointer.label is None:
                    node_pointer.set_label(
                        lbcx(
                            label = orc("", row, column),
                            ICHed = orc(0, row, column),
                            sort_info = orc("", row, column)
                            )
                    )
                
                # move the pointer to the parent
                node_pointer = node_pointer.parent()
            else:
                if node_pointer.label() is None:
                    # if the current node has no label
                    # then this token must be that
                    node_pointer.set_label(
                        lbcx.parse_from_kai_penn(token, row)
                    )
                else:
                    # we have found a terminal child node
                    # add them as its child
                    node_pointer.append(
                        pt(
                            node = lbcx(
                                label = orc(token, row, column),
                                ICHed = orc(0, row, column),
                                sort_info = orc("", row, column)
                                ),
                            children = []
                        )
                    )
                # ===END IF===
            # ===END IF===
        # ===END FOR===
    
    # TODO: check errors here

    return res_tree

    # ===END===