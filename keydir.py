from typing import Optional, Tuple

import constants


keydir: dict[str, Tuple[int, int]] = {}


def set(key: str, offset: int, size: int):
    keydir[key] = (offset, size)

def get(key: str) -> Optional[Tuple[int, int]]:
    return keydir.get(key)

def build_keydir():
    with open(constants.DATASTORE_FILE_NAME, 'rb') as infile:
        current_position: int = infile.tell()
        line: bytes
        while line := infile.readline():
            length_bytes_including_newline = len(line)
            # print(f"length of line before stripping and decoding: {len(line)}")
            # print(f"at position {current_position}: {line} (raw bytes)")
            line_str: str = line.decode(constants.ENCODING).strip()  # Remove the trailing \n
            # print(f"length of line after stripping and decoding: {len(line_str)}")
            # print(f"at position {current_position}: {line_str} (decoded and stripped line)")
            key_str, value = line_str.split(",")
            # print(f"at position {current_position}: {key_str},{value}")
            set(key_str, current_position, length_bytes_including_newline)
            current_position: int = infile.tell()