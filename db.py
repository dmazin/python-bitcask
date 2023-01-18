import argparse
from typing import Optional


DATASTORE_FILE_NAME = "datastore.txt"
OPERATION_SET = "set"
OPERATION_GET = "get"


def _set_up_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--operation", choices=[OPERATION_SET, OPERATION_GET], required=True
    )
    parser.add_argument("--key", required=True)
    # TODO validate that value is present when operation=set
    parser.add_argument("--value", required=False)

    args = parser.parse_args()
    return args


def get(key: str) -> Optional[str]:
    # TODO ensure that this file exists before trying to open it
    datastore = open(DATASTORE_FILE_NAME)

    value: Optional[str] = None
    for line in datastore:
        line: str = line.strip()  # Remove the trailing \n
        current_key, current_value = line.split(",")
        if current_key == key:
            value = current_value

    return value


def set(key: str, value: str) -> None:
    # `a` mode will create the file if it doesn't exist; if it does exist, we
    # will append to the end of the file
    datastore = open(DATASTORE_FILE_NAME, mode="a")
    datastore.write(f"{key},{value}\n")


if __name__ == "__main__":
    args = _set_up_args()

    if args.operation == OPERATION_SET:
        set(args.key, args.value)

    if args.operation == OPERATION_GET:
        print(get(args.key))
