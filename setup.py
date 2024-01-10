from setuptools import setup, find_packages

VERSION = "1.15"
DESCRIPTION = "CLI for downloading all repositories from a specified user."
with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()
AUTHOR = "NecRaul"

setup(
    name="git_neko",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    packages=find_packages(),
    install_requires=["requests"],
    keywords=[
        "python",
        "repository downloader",
        "downloader",
        "repository",
        "git-neko",
        "kuroneko",
    ],
    url="https://github.com/NecRaul/git-neko",
    project_urls={
        "Documentation": "https://github.com/NecRaul/git-neko#readme",
        "Source": "https://github.com/NecRaul/git-neko",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
    ],
    py_modules=["download", "environment"],
    entry_points={
        "console_scripts": [
            "git-neko = git_neko.__init__:main",
        ],
    },
)
