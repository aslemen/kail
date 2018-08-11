import typing
import io
import re
import collections as coll

import nltk.tree as trees

"""
    This module provides classes that represent various linguistic structures.
"""

class Object_with_Row_Column:
    def __init__(
            self,
            content: object,
            row: int,
            column: int
            ) -> "String_with_Row_Column":
        self.content = content
        self.row = row
        self.column = column

    def __repr__(self) -> str:
        return "<{label}, Position:({row_add}, {col_add})>".format(
                        label = str(self.content),
                        row_add = self.row + 1,
                        col_add = self.column + 1
                        )
    
    def __str__(self) -> str:
        return str(self.content)

    # ===END===

class Label_Complex_with_Pos:
    def __init__(
            self,
            label: Object_with_Row_Column,
            ICHed: Object_with_Row_Column,
            sort_info: Object_with_Row_Column
            ) -> "Label_with_Pos":
        self.label = label
        self.ICHed = ICHed
        self.sort_info = sort_info

        # ===END===

    def __repr__(self):
        return "{label}-{ICHed};{sort_info}".format(
                    label = repr(self.label),
                    ICHed = repr(self.ICHed),
                    sort_info = repr(self.sort_info)
                )

        # ===END===

    def __str__(self):
        return self.print_kai_penn()

    @staticmethod
    def parse_from_kai_penn(text: str, current_row: int = -1):
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
        return "{label}{ICHed}{sort_info}".format(
            label = str(self.label),
            ICHed = ("-" + str(self.ICHed)) if self.ICHed.content > 0 else "",
            sort_info = (";" + str(self.sort_info)) \
                                if self.sort_info.content else ""
            )

        # ===END===

    def print_kail(self):
        return "{label}{ICHed}{sort_info}".format(
            label = str(self.label),
            ICHed = " " + str(self.ICHed) if self.ICHed.content > 0 or self.sort_info.content else "",
            sort_info = " " + str(self.sort_info) \
                                if self.sort_info.content else ""
            )
        # ===END===

#    @staticmethod
#    def generate_from_match_object(
#            match: "_sre.SRE_Match",
#            init_row: int = 0,
#            init_column: int = 0):
#        return String_with_Pos(
#                label = match.group(0),
#                row = init_row + match.start(),
#                column = init_column + match.end())
