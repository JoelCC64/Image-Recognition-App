import hashlib
import os


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    data_type = os.path.splitext(filename)
    formato = data_type[1].lower()
    if formato in {".png", ".jpg", ".jpeg", ".gif"}:
        return True
    else:
        return False


async def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    md5_hasher = hashlib.md5()
    while chunk := await file.read(4096):
        md5_hasher.update(chunk)
    hex_hash = md5_hasher.hexdigest()
    await file.seek(0)
    name, extension = os.path.splitext(file.filename)
    filename = f"{hex_hash}{extension.lower()}"
    return filename
