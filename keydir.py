from typing import Optional, Tuple

import constants


class KeyDir:
    def __init__(self) -> None:
        self.keydir: dict[str, Tuple[int, int]] = {}
        self.build_keydir()

    def set(self, key: str, offset: int, size: int) -> None:
        self.keydir[key] = (offset, size)

    def get(self, key: str) -> Optional[Tuple[int, int]]:
        return self.keydir.get(key)

    def build_keydir(self) -> None:
        print("debug: building keydir")
        with open(constants.DATASTORE_FILE_NAME, "rb") as infile:
            current_position: int = infile.tell()
            line: bytes
            while line := infile.readline():
                length_bytes_including_newline = len(line)
                # print(f"length of line before stripping and decoding: {len(line)}")
                # print(f"at position {current_position}: {line} (raw bytes)")
                line_str: str = line.decode(
                    constants.ENCODING
                ).strip()  # Remove the trailing \n
                # print(f"length of line after stripping and decoding: {len(line_str)}")
                # print(f"at position {current_position}: {line_str} (decoded and stripped line)")
                key_str, value = line_str.split(",")
                # print(f"at position {current_position}: {key_str},{value}")
                self.set(key_str, current_position, length_bytes_including_newline)
                current_position: int = infile.tell()


keydir = KeyDir()
