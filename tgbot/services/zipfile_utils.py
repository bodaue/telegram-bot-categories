import os
import shutil
import zipfile


def unpack_zipfile(filename: str, extract_dir: str, encoding='cp866') -> list[str]:
    """
    :param filename: path of ZIP file
    :param extract_dir: path where ZIP file should be extracted
    :param encoding:
    :return: list of extracted files
    """
    result = []
    with zipfile.ZipFile(filename) as archive:
        for entry in archive.infolist():
            name = entry.filename.encode('cp437').decode(encoding)

            if name.startswith('/') or '..' in name:
                continue

            target = os.path.join(extract_dir, *name.split('/'))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not entry.is_dir():  # file
                with archive.open(entry) as source, open(target, 'wb') as dest:
                    shutil.copyfileobj(source, dest)
            result.append(name)
    return result
