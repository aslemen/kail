import typing
import io
import collections as col

"""
    This module provides classes that represent various linguistic structures.
"""

Row_Column = col.namedtuple("Row_Column", ("row", "column"))

class String_with_Pos:
    def __init__(self, label: str, row: int, column:int) -> "Label_with_Pos":
        self.label = label
        self.pos = Row_Column(row, column) # both starting with 0

    def __repr__(self):
        return "<{t}; Label: \"{label}\", Line: {row_add} ({row}+1), Column: {col_add} ({col}+1)>".format(
                t = type(self).__name__,
                label = str(self.label),
                row = self.pos.row,
                row_add = self.pos.row + 1,
                col = self.pos.column
                col_add = self.pos.col + 1,
                )

    def __str__(self):
        return str(self.label)

    @staticmethod
    def generate_from_match_object(
            match: "_sre.SRE_Match",
            init_row: int = 0,
            init_column: int = 0):
        return String_with_Pos(
                label = match.group(0),
                row = init_row + match.start(),
                column = init_column + match.end())

class PennSyntaxError(SyntaxError):
    pass

class LangSyntaxError(SyntaxError):
    pass

class Tree:
    """
        This class provides a (sub)tree instance the contents of which are mutable.

        Attributes
        ----------
        label: Any
            The label of the root node. It can be a string, or an AVM.
        *children: tuple of Tree
            The children of the root node.
    """

    def __init__(self, label: typing.Any = None, *children: typing.Tuple["Tree"]) -> None:
        """
            Generate a (sub)tree instance the contents of which are mutable.

            Parameters
            ----------
            label: Any, default ""
                The label of the root node. It can be a string, or an AVM.
            *children: tuple of Tree
                The children of the root node.

            Raises
            ------
            #TypeError
            #    when a non-Tree is designated as one of the children.
        """
        self.label = label

        #for child in children:
        #    if not isinstance(child, Tree):
        #        raise TypeError("The children are expected to be of the type Tree.")

        self.children = list(children)



    def get_depth(self) -> int:
        """
            Get the depth of the current tree.

            Parameters
            ----------

            Returns
            -------
            depth: int
                the depth of the current tree
        """
        if len(self.children) == 0:
            return 1
        else:
            return max(child.get_depth() for child in self.children) + 1

    def __len__(self) -> int:
        return len(self.children)

    def __repr__(self) -> str:
        return "<{label}, \n\t[{children}]>".format(
                label = repr(self.label),
                children = ", ".join(map(repr, self.children)))

    def __str__(self) -> str:
        return self.print_indented(indent = 0)

class Parented_Tree(Tree):
    """
        This class provides a (sub)tree instance the contents of which are mutable.

        Attributes
        ----------
        label: Any
            The label of the root node. It can be a string, or an AVM.
        parent: Parented_Tree
                The parent of this tree.
        *children: tuple of Tree
            The children of the root node.
     """

    def __init__(self, label: typing.Any = "", 
                 parent: "Parented_Tree" = None, *children: typing.Tuple["Tree"]):
        """
            Generate a (sub)tree instance with a single parent.

            Parameters
            ----------
            label: Any, default ""
                The label of the root node. It can be a string, or an AVM.
            parent: Parented_Tree, default None
                The parent of this tree.
            *children: tuple of Tree
                The children of the root node.

            Raises
            ------
            TypeError
                when a non-Tree is designated as one of the children.
        """

        self.parent = parent
        super(Parented_Tree, self).__init__(label, *children)

    def __repr__(self) -> str:
        return "<{label}, parent = {parent}, [{children}]>".format(
                label = repr(self.label),
                parent = hex(id(self.parent)),
                children = ", ".join(map(repr, self.children)))


    @staticmethod
    def init_from_tree(tree: Tree, parent: Tree = None) -> "Parented_Tree":
        """
            Generate a Parent_Tree instance from a Tree.

            Parameters
            ----------
            tree: Tree
                The target tree.
            parent: Tree, default None
                The parent tree.

            Returns
            -------
            parented_tree: Parented_Tree
                The resulted tree.
        """

        main_tree = Parented_Tree(label = tree.label,
                                 parent = parent)
        main_tree.children = [Parented_Tree.init_from_tree(st) for st in tree.children]

        return main_tree
