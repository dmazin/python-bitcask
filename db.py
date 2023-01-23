import argparse
from typing import Optional

from keydir import keydir
import constants


def _set_up_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--operation", choices=[constants.OPERATION_SET, constants.OPERATION_GET], required=True
    )
    parser.add_argument("--key", required=True)
    # TODO validate that value is present when operation=set
    parser.add_argument("--value", required=False)

    args = parser.parse_args()
    return args


def get(key: str) -> Optional[str]:
    keydir_value = keydir.get(key)
    if keydir_value is None:
        return None
    
    offset: int
    size: int
    offset, size = keydir_value

    # TODO ensure that this file exists before trying to open it
    datastore = open(constants.DATASTORE_FILE_NAME, mode='br')
    datastore.seek(offset)
    kv_pair_bytes = datastore.read(size)
    kv_pair_str: str = kv_pair_bytes.decode(constants.ENCODING)
    kv_pair_str_stripped = kv_pair_str.strip()

    # TODO return just the value, not the kv_pair

    return kv_pair_str_stripped


def set(key: str, value: str) -> None:
    kv_pair = f"{key},{value}\n"
    kv_pair_bytes: bytes = kv_pair.encode(constants.ENCODING)

    # `a` mode will create the file if it doesn't exist; if it does exist, we
    # will append to the end of the file
    datastore = open(constants.DATASTORE_FILE_NAME, mode="ab")

    current_position: int = datastore.tell()
    bytes_written: int = datastore.write(kv_pair_bytes)

    keydir.set(key, current_position, bytes_written)

    print(f"wrote {bytes_written} bytes at offset {current_position}")


if __name__ == "__main__":
    args = _set_up_args()

    if args.operation == constants.OPERATION_SET:
        set(args.key, args.value)

    if args.operation == constants.OPERATION_GET:
        print(get(args.key))
