import pytest
import pathlib

import kail.parse as parse
import kail.output as out
import kail.structures as strs

from nltk.tree import ParentedTree as pt

@pytest.fixture(
    autouse = True,
    scope = "module"
)
def sample_correct_kail(request):
    print('[Open sample files]')

    f = open("./tests/sample_correct.kail")

    def dispose():
        f.close()

    request.addfinalizer(dispose)

    return f

@pytest.fixture(
    autouse = True,
    scope = "module"
)
def sample_correct_kai_penn(request):
    return "./tests/sample_correct.kai"

def test_parse_print_kai_penn_indented(sample_correct_kail):
    trees = parse.parse_kail(sample_correct_kail)
    print("""
======
Input style: the Kail Style
Output style: the Kainoki Penn Style
======""")
    print("\n\n".join(out.print_kai_penn_indented(tree) for tree in trees))

    sample_correct_kail.seek(0)

def test_parse_print_kai_penn_squeezed(sample_correct_kail):
    trees = parse.parse_kail(sample_correct_kail)
    print("""
======
Input style: the Kail Style
Output style: the Kainoki Penn Squeezed Style
======""")
    print("\n\n".join(out.print_kai_penn_squeezed(tree) for tree in trees))

    sample_correct_kail.seek(0)

def test_parse_print_kail(sample_correct_kail):
    trees = parse.parse_kail(sample_correct_kail)
    print("""
======
Input style: the Kail Style
Output style: the Kail Style
======""")
    print("\n\n".join(out.print_kail(tree) for tree in trees))

    sample_correct_kail.seek(0)

def test_parsekai_penn_print_kail(sample_correct_kai_penn: str):
    trees = parse.convert_kai_penn_tree_file([sample_correct_kai_penn])
    #for n, tree in enumerate(trees):
    #s    print(n, type(tree))
    print("""
======
Input style: the Kainoki Penn Style
Output style: the Kail Style
======""")
    print("\n\n".join(out.print_kail(tree) for tree in trees))

@pytest.mark.parametrize(
    ("text", "result"),
    (
        ("NP-SBJ", "NP-SBJ"),
        ("NP-SBJ2", "NP-SBJ2"),
        ("NP-SBJ-2", "NP-SBJ 2"),
        ("NP-SBJ;*", "NP-SBJ 0 *"),
        ("NP-SBJ-2-2;{test}", "NP-SBJ-2 2 {test}")
    )
)
def test_parse_label_complex_kai_penn(text, result):
    assert strs.Label_Complex_with_Pos.parse_from_kai_penn(text).print_kail() == result