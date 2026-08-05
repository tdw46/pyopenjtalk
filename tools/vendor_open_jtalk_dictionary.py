"""Vendor the pinned OpenJTalk dictionary into release wheels."""

import hashlib
import io
import shutil
import tarfile
from pathlib import Path
from urllib.request import Request, urlopen


DICTIONARY_NAME = "open_jtalk_dic_utf_8-1.11"
DICTIONARY_URL = (
    "https://github.com/r9y9/open_jtalk/releases/download/v1.11.1/"
    f"{DICTIONARY_NAME}.tar.gz"
)
DICTIONARY_SHA256 = (
    "fe6ba0e43542cef98339abdffd903e062008ea170b04e7e2a35da805902f382a"
)


def main():
    request = Request(DICTIONARY_URL, headers={"User-Agent": "Beyond-VRM-Wheel-Build"})
    with urlopen(request, timeout=120) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != DICTIONARY_SHA256:
        raise RuntimeError("OpenJTalk dictionary SHA-256 verification failed")
    destination_root = Path(__file__).resolve().parent.parent / "pyopenjtalk"
    destination = destination_root / DICTIONARY_NAME
    if destination.exists():
        shutil.rmtree(destination)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        members = bundle.getmembers()
        expected_prefix = DICTIONARY_NAME + "/"
        if not members or any(
            member.issym()
            or member.islnk()
            or (member.name != DICTIONARY_NAME and not member.name.startswith(expected_prefix))
            or ".." in Path(member.name).parts
            for member in members
        ):
            raise RuntimeError("OpenJTalk dictionary archive paths are unsafe")
        bundle.extractall(destination_root)
    required = ("sys.dic", "char.bin", "matrix.bin", "COPYING")
    if not all((destination / filename).is_file() for filename in required):
        raise RuntimeError("OpenJTalk dictionary archive is incomplete")


if __name__ == "__main__":
    main()
