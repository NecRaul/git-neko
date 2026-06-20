from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("git_neko")
except PackageNotFoundError:
    __version__ = "dev"
