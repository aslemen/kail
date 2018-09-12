import typing
import io
import re
import collections as coll
import itertools

"""
    This module provides classes that represent various linguistic structures.
"""

class Object_with_Row_Column:
    """
        An arbitrary object with the row-column position in the due source document. 
    """

    def __init__(
            self,
            content: object,
            row: int,
            column: int
            ) -> "String_with_Row_Column":
        """
            The initializer.

            Parameters
            ----------
            content: any
                An arbitrary object. Retrivable from self.content.
            row: int
                The row in the source document (beginning with 0).
            column: int
                The column in the source document (beginning with 0).
        """
        self.content = content
        self.row = row
        self.column = column

        # ===END===

    def __repr__(self) -> str:
        """
            Give a detailed representation of the instance.

            Returns
            -------
            repr: str
                The information of this instance in the format
                    "<{label}, Position:({row_add}, {col_add})>"
                    where
                        {label} is the content converted to a string,
                        {row_add} is the row number beginning with 1, and
                        {col_add} is the column number beginning with 1.
                Example:
                    <NP-SBJ, (3, 12)>
        """
        return "<{label}, Position:({row_add}, {col_add})>".format(
                        label = str(self.content),
                        row_add = self.row + 1,
                        col_add = self.column + 1
                        )
        # ===END===
    
    def __str__(self) -> str:
        """
            Give a simplized representation of the instance, which is merely a string of the content.

            Returns
            -------
            repr: str
                The content as a string.
        """
        return str(self.content)

    # ===END===

class Label_Complex_with_Pos:
    """
        A representation of an NPCMJ tree label complex (a triple of label name, ICH index, and sort information) with annotations of row-column information from the source document.
    """
    def __init__(
            self,
            label: Object_with_Row_Column,
            ICHed: Object_with_Row_Column,
            sort_info: Object_with_Row_Column
            ) -> "Label_with_Pos":
        """
            The initializer.

            Parameters
            ----------
            label: Object_with_Row_Column[str]
                A label.
                Example:
                    NP-SBJ (for NP-SBJ-3;{ABC})
            ICHed: Object_with_Row_Column[int]
                An ICH index. 0 when not specified.
                Example:
                    3 (for NP-SBJ-3;{ABC})
            sort_info: Object_with_Row_Column[str]
                A sort information. None or "" when not specified.
                Example:
                    ABC (for NP-SBJ-3;{ABC})
        """
        self.label = label
        self.ICHed = ICHed
        self.sort_info = sort_info

        # ===END===

    def __repr__(self):
        """
            A detailed representation of this instance.

            Returns
            -------
            repr: str
                The representation of this instance in the format
                    "{label}-{ICHed};{sort_info}" (the same as NPCMJ)
                Example:
                    <NP-SBJ, Position:(1, 4)>-<3, Position:(1, 11)>;<ABC, Position(1, 13)>
        """
        return "{label}-{ICHed};{sort_info}".format(
                    label = repr(self.label),
                    ICHed = repr(self.ICHed),
                    sort_info = repr(self.sort_info)
                )

        # ===END===

    def __str__(self):
        """
            Give the representation of this instance in the NPCMJ style,
            doing the same as the function print_kai_penn.

            Returns
            -------
            repr: str
                The representation of this instance in the format
                    "{label}-{ICHed};{sort_info}" (the same as NPCMJ).
                Example:
                    NP-SBJ-3;{ABC}
        """
        return self.print_kai_penn()

    @staticmethod
    def parse_from_kai_penn(text: str, current_row: int = -1):
        """
        Parse an NPCMJ label to obtain an instance of this class.

        Parameters
        ----------
        text: str
            The label complex to be parsed.
        current_row: int
            The current row number in the source document (beginning with 0).

        Returns
        -------
        instance: self
            The instance created from the label text.
        """
        re_str: "_sre.SRE_Match" = re.compile(
            r"^([_\d\w\-]*?)(?:-([0-9]+))?(?:;({[^\s{}]+}|\*.*\*|\*))?$"
            )

        current_items: "_sre.SRE_Match" = re_str.match(text)

        # Label
        current_label = Object_with_Row_Column(
                    content = current_items.group(1) or "",
                    row = current_row,
                    column = current_items.span(1)[0]
                )

        # ICHed
        current_ICHed = Object_with_Row_Column(
                    content = int(current_items.group(2) or 0),
                    row = current_row,
                    column = current_items.span(2)[0]
                )

        # sort info
        current_sort_info = Object_with_Row_Column(
                    content = current_items.group(3) or "",
                    row = current_row,
                    column = current_items.span(3)[0]
                )

        # Constitute a label compex
        return Label_Complex_with_Pos(
                                label = current_label, 
                                ICHed = current_ICHed,
                                sort_info = current_sort_info
                                )
        # ===END===
    
    @staticmethod
    def parse_from_kail(text: str, current_row: int = -1):
        """
        Parse an Kail label to obtain an instance of this class.

        Parameters
        ----------
        text: str
            The label complex to be parsed.
        current_row: int
            The current row number in the source document (beginning with 0).

        Returns
        -------
        instance: self
            The instance created from the label text.
        """
        re_word: "_sre.SRE_Match" = re.compile(r"[^ \t]+")

        current_items: typing.Iterable["_sre.SRE_Match"] = re_word.finditer(text)

        # The label
        current_label: Object_with_Row_Column = None
        try:
            current_label_raw = next(current_items)
            current_label = Object_with_Row_Column(
                                content = current_label_raw.group(),
                                row = current_row,
                                column = current_label_raw.span()[0]
                            )
        except StopIteration:
            current_label = Object_with_Row_Column(
                                content = "",
                                row = current_row,
                                column = -1
                            )
        
        # ICHed number
        current_ICHed: int = 0

        try:
            current_ICHed_raw = next(current_items)
            current_ICHed = Object_with_Row_Column(
                                content = int(current_ICHed_raw.group()),
                                row = current_row,
                                column = current_ICHed_raw.span()[0]
                            )
        except StopIteration:
            current_ICHed = Object_with_Row_Column(
                                content = 0,
                                row = current_row,
                                column = -1
                            )

        # Sort info
        current_sort_info: Object_with_Row_Column = None
        try:
            current_sort_info_raw = next(current_items)
            current_sort_info = Object_with_Row_Column(
                                content = current_sort_info_raw.group(),
                                row = current_row,
                                column = current_sort_info_raw.span()[0]
                            )
        except StopIteration:
            current_sort_info = Object_with_Row_Column(
                                content = "",
                                row = current_row,
                                column = -1
                            )

        # If there are remaining items, then they are redundant
        for redundant in current_items:
            raise SyntaxError(
                "A redundant label constituent is found " \
                "at Line {row_add}, Column {col_add}".format(
                        row_add = current_row + 1,
                        col_add = redundant.span()[0] + 1
                        )
                    )

        # Constitute a label compex
        return Label_Complex_with_Pos(
                                label = current_label, 
                                ICHed = current_ICHed,
                                sort_info = current_sort_info
                                )
        # ===END===

    def print_kai_penn(self):
        """
            Give the representation of this instance in the NPCMJ style.
            
            Returns
            -------
            repr: str
                The representation of this instance in the format
                    "{label}-{ICHed};{sort_info}" (the same as NPCMJ).
                Example:
                    NP-SBJ-3;{ABC}
        """
        return "{label}{ICHed}{sort_info}".format(
            label = str(self.label),
            ICHed = ("-" + str(self.ICHed)) if self.ICHed.content > 0 else "",
            sort_info = (";" + str(self.sort_info)) \
                                if self.sort_info.content else ""
            )

        # ===END===

    def print_kail(self):
        """
            Give the representation of this instance in the Kail style.
            
            Returns
            -------
            repr: str
                The representation of this instance in the format
                    "{label} {ICHed} {sort_info}".
                Examples:
                    NP-SBJ 3 ABC (corresponding to the NPCMJ representation "NP-SBJ-3;{ABC}")
                    NP-SBJ 3 ("NP-SBJ-3")
                    NP-SBJ 0 ABC ("NP-SBJ;{ABC}")
                    NP-SBJ ("NP-SBJ")
        """
        return "{label}{ICHed}{sort_info}".format(
            label = str(self.label),
            ICHed = " " + str(self.ICHed) if self.ICHed.content > 0 or self.sort_info.content else "",
            sort_info = " " + str(self.sort_info) \
                                if self.sort_info.content else ""
            )
        # ===END===

class Comment_with_Pos:
    """
        A representation of an NPCMJ/Kail comment with annotations of row-column information from the source document.
    """
    def __init__(
            self,
            comment: Object_with_Row_Column
            ) -> "Comment_with_Pos":
        """
            The initializer.

            Parameters
            ----------
            comment: Object_with_Row_Column[str]
                A comment.
                Example:
                    abcedfg (for ";abcedfg\\n")
        """
        self.comment = comment
        # ===END===
    
    @staticmethod
    def parse(text: str, current_row: int, current_column: int):
        return Comment_with_Pos(comment = text)

        # ===END===
    
    def print_kai_penn(self) -> str:
        return ";;" + str(self.comment)

        # ===END===

    def print_kail(self) -> str:
        return "#" + str(self.comment)

        # ===END===

    def __repr__(self):
        return "<COMMENT: {text}>".format(text = repr(self.comment))

        # ===END==
    
    def __str__(self):
        return self.print_kai_penn()

        # ===END===

class TreeWithParent(coll.deque):
    def __init__(
            self, 
            node: object = None, 
            children: coll.deque = tuple(),
            parent: "TreeWithParent" = None
        ):
        super().__init__(self)

        self.set_label(node)
        self.extend(children)
        self.set_parent(parent)
        # ===END===

    # ======
    # Helpers
    # ======

    @staticmethod
    def __check_type_TreeWithParent(x):
        if x is None: return
        if not isinstance(x, TreeWithParent):
            raise ValueError(TreeWithParent)
        # ===END===

    @staticmethod
    def __check_type_TreeWithParent_parented(x):
        TreeWithParent.__check_type_TreeWithParent(x)

        if x.get_parent() is not None:
            raise Exception(
                "The item {repr} has already got a parent {par}!".format(
                    repr = repr(x),
                    par = repr(x.get_parent())
                    )
                )
        # ===END===

    # ======
    # Parent controls
    # ======

    def get_label(self): return self.__label
    def set_label(self, l): self.__label = l

    def get_parent(self): return self.__parent
    def set_parent(self, p: "TreeWithParent"):
        self.__check_type_TreeWithParent(p)
        self.__parent = p
        # ===END===

    # ======
    # Insertion
    # ======

    def append(self, x: "TreeWithParent"):
        self.__check_type_TreeWithParent_parented(x)

        x.set_parent(self)
        super().append(x)

        # ===END===

    def appendleft(self, x: "TreeWithParent"):
        self.__check_type_TreeWithParent_parented(x)

        x.set_parent(self)
        super().appendleft(x)

        # ===END===

    def extend(self, x: typing.Iterable):
        for child in x:
            self.append(child)

        # ===END===

    def extendleft(self, x: typing.Iterable):
        for child in x:
            self.appendleft(child)

        # ===END===

    def insert(self, i, x):
        self.__check_type_TreeWithParent_parented(x)

        x.set_parent(self)
        super().insert(i, x)
        # ===END===

    # ======
    # Deletion
    # ======

    def pop(self):
        popped: "TreeWithParent" = super().pop()
        popped.set_parent(None)
        return popped

        # ===END===
    
    def popleft(self):
        popped: "TreeWithParent" = super().popleft()
        popped.set_parent(None)
        return popped
        
        # ===END===
    
    def remove(self, value: "TreeWithParent"):
        removed: "TreeWithParent" = super().remove(value)
        removed.set_parent(None)
        return removed

        # ===END===

    # ======
    # Tree traversing
    # ======
    def get_parent_index(self): return self.get_parent().index(self)

    def get_left_siblings(self):
        parent = self.get_parent()
        if not isinstance(parent, TreeWithParent): return None

        index = self.get_parent_index()
        return itertools.islice(
            iter(self),
            index
        )
        
        # ===END===

    def get_right_siblings(self):
        parent = self.get_parent()
        if not isinstance(parent, TreeWithParent): return None

        index = self.get_parent_index()

        return itertools.islice(
            iter(self),
            index + 1,
            None
        )
        
        # ===END===

    def get_all_siblings(self):
        left = self.get_left_siblings()
        right = self.get_right_siblings()

        if left is None:
            if right is None:
                return None
            else:
                return right
        else:
            if right is None:
                return left
            else:
                return itertools.chain(left, right)

        # ===END===

    # ======
    # Parsing
    # ======


    @staticmethod
    def __strip_linear_comment_from_line(
            line_raw: str, 
            row: int, 
            node_pointer: "TreeWithParent",
            comment_char: str = ";;"
        ) -> str:
        split_result = line_raw.split(comment_char, 1)

        line_cleared = split_result[0]

        if len(split_result) > 1:
            current_comment_raw = split_result[1]
            current_comment = Comment_with_Pos(
                                Object_with_Row_Column(
                                    content = current_comment_raw,
                                    row = row,
                                    column = len(line_cleared)
                                    )
                                )
            node_pointer.append(TreeWithParent(current_comment, children = []))

        return line_cleared

        # ===END===

    @staticmethod
    def parse_kail(stream: io.TextIOBase) -> typing.List["TreeWithParent"]:
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

        res_tree: "TreeWithParent" = TreeWithParent(None, children = [])
        node_pointer: "TreeWithParent" = res_tree

        re_indent: "_sre.SRE_Match" = re.compile(r"[ \t]*")

        for row, line_raw in enumerate(stream):
            # ======
            # Strip out comments
            # ======
            line_without_comment = TreeWithParent.__strip_linear_comment_from_line(
                                                    line_raw = line_raw.rstrip(),
                                                    row = row,
                                                    node_pointer = node_pointer,
                                                    comment_char = "#"
                                                )

            # ======
            # Firstly, check whether the line is emTreeWithParenty
            # ======
            line = line_without_comment.rstrip()

            if line == "": continue

            # ======
            # The line being non-emTreeWithParenty, find the indent
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
            current_label_complex: Label_Complex_with_Pos = Label_Complex_with_Pos.parse_from_kail(line, row)

            # ======
            # Create a chile node
            # ======
            current_node = TreeWithParent(current_label_complex, children = [])

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
                # keep on that tree deTreeWithParenth
                # make a sibling
                current_node = TreeWithParent(current_label_complex, children = [])
                node_pointer.get_parent().append(current_node)

            else:
                # go back to the parent

                # find the anchor
                while True:
                    # discard the previous indent
                    indent.pop()
                    # make the pointer point to the ancestor
                    node_pointer = node_pointer.get_parent()

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
                        current_node = TreeWithParent(current_label_complex, children = [])
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

    @staticmethod
    def parse_kai_penn(stream: io.TextIOBase) -> typing.List["TreeWithParent"]:
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

        res_tree: "TreeWithParent" = TreeWithParent(None, children = [])
        node_pointer: "TreeWithParent" = res_tree

        for row, line_raw in enumerate(stream):
            # ======
            # Strip out comments
            # ======
            line_without_comment = TreeWithParent.__strip_linear_comment_from_line(
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
                    new_node = TreeWithParent(None, children = [])

                    node_pointer.append(new_node)

                    # move the pointer
                    node_pointer = new_node
                elif token == ")":
                    # go back to the parent node

                    # if the current node has no label
                    # create an emTreeWithParenty one
                    if node_pointer.get_label() is None:
                        node_pointer.set_label(
                            Label_Complex_with_Pos(
                                label = Object_with_Row_Column("", row, column),
                                ICHed = Object_with_Row_Column(0, row, column),
                                sort_info = Object_with_Row_Column("", row, column)
                                )
                        )
                    
                    # move the pointer to the parent
                    node_pointer = node_pointer.get_parent()
                else:
                    if node_pointer.get_label() is None:
                        # if the current node has no label
                        # then this token must be that
                        node_pointer.set_label(
                            Label_Complex_with_Pos.parse_from_kai_penn(token, row)
                        )
                    else:
                        # we have found a terminal child node
                        # add them as its child
                        node_pointer.append(
                            TreeWithParent(
                                node = Label_Complex_with_Pos(
                                    label = Object_with_Row_Column(token, row, column),
                                    ICHed = Object_with_Row_Column(0, row, column),
                                    sort_info = Object_with_Row_Column("", row, column)
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

    # ======
    # Printing
    # ======
    def print_kai_penn_indented(
            self, 
            indent: int = 0, 
            show_comments = True
        ) -> str:
        """
            Generate the well-indented representation of this tree, given the overall indent

            Parameters
            ----------
            indent: int, default 0
                the overall indent.
            show_comments: bool, default True
                whether to show comments

            Returns
            -------
            indented_tree: str
                the indented tree representation
        """

        def __raise_comments(tree: "TreeWithParent") -> "TreeWithParent":
            # A helper method that raise comment nodes.
            for child in tree:
                __raise_comments(child)

            for comment in filter(
                            lambda x: isinstance(
                                x.get_label(), 
                                Comment_with_Pos
                            ),
                            tree
                        ):
                parent: "TreeWithParent" = comment.get_parent()
                grandparent: "TreeWithParent" = parent.get_parent()

                if not comment.get_right_siblings():
                    # the comment is on the rightmost of its parent

                    if grandparent is not None:
                        # if it is raisable
                        parent.remove(comment)
                        grandparent.insert(parent.parent_index() + 1, comment)

            return tree
            # ===END===

        def __internal_routine(
                tree: "TreeWithParent", 
                indent: int = 0, 
                show_comments = True
            ) -> str:

            label_object: str = tree.get_label()
            self_label_raw: str = None

            if isinstance(label_object, Label_Complex_with_Pos):
                self_label_raw = label_object.print_kai_penn()
            elif isinstance(label_object, Comment_with_Pos):
                if show_comments:
                    self_label_raw = str(label_object)
                else:
                    return ""
            else:
                self_label_raw = str(label_object)

                # ===END IF===

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
                    res for res in (
                            __internal_routine(
                                st,
                                indent = indent \
                                        + 1 \
                                        + len(self_label_raw) \
                                        + 1,
                                show_comments = show_comments
                                )
                            for st in tree
                        ) if res
                    ]

                # cut out the spaces at the beginning and the end of the first subtree
                str_subtrees[0] = str_subtrees[0].strip()

                # generate
                return "{indent}({label} {subtrees})".format(
                            indent = " " * indent,
                            label = self_label_raw,
                            subtrees = "\n".join(str_subtrees)
                            )

                # ===END IF===

            # ===END===

        tree_comments_raised = __raise_comments(self)
        return __internal_routine(tree_comments_raised, indent, show_comments)
        # ===END===

    def print_kai_penn_squeezed(self) -> str:
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
            string = self.print_kai_penn_indented(show_comments = False)
            )

        # ===END===

    def print_kail(self, indent_amount: int = 2, indent: int = 0) -> str:
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
        label_object: str = self.get_label()
        self_label_raw: str = None

        if isinstance(label_object, Label_Complex_with_Pos):
            self_label_raw = label_object.print_kail()
        elif isinstance(label_object, Comment_with_Pos):
            self_label_raw = label_object.print_kail()
        else:
            self_label_raw = str(label_object)

        return (" " * indent) + "\n".join(
                        itertools.chain(
                            (self_label_raw, ),
                            map(
                                lambda subtree: subtree.print_kail(
                                    indent_amount = indent_amount,
                                    indent = indent + indent_amount
                                    ),
                                iter(self)
                            )
                        )
        )
