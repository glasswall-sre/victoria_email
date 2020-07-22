from os.path import splitext


def file_ext(f: str) -> str:
    """Get the file extension of a file."""
    return splitext(f)[1]


def file_name(f: str) -> str:
    """Get the filename of a file without the extension."""
    return splitext(f)[0]