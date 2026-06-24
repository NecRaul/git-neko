from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("git_neko")
except PackageNotFoundError:
    __version__: str = "dev"
