import typing
import io
import re
import collections as coll

import nltk.tree as trees

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
            r"^([_\d\w\-]*?)(?:-([0-9]+))?(?:;({\w+}|\*.*\*|\*))?$"
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
