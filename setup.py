from setuptools import setup

setup(
        name = "kail",
        version = "1.1.0",
        author = "aslemen",
        author_email = "net@hayashi-lin.net",
        packages = ["kail"],
        install_requires = [
            "click",
            "nltk",
            "pathlib"
            ],
        entry_points = """
        [console_scripts]
        kail = kail.__main__:routine
        """
        )
