import json
import os
from sys import platform

"""
IMPORTANT: This script is intended to be run in the ESP32, not in the PC
"""

DEPLOY_PACKAGE_FILENAME = 'deploy-package.json'

FILES_TO_AVOID_DELETION = {DEPLOY_PACKAGE_FILENAME, 'state.json'}


def remove_path(path: str) -> None:
    for x in os.listdir(path):
        if x in FILES_TO_AVOID_DELETION:
            continue
        curr_path = f'{path}/{x}'
        if '.' not in curr_path:
            # This is a dir
            remove_path(curr_path)
        os.rmdir(curr_path)


def clean_device() -> None:
    print('Cleaning device...')
    remove_path('')


def unpack() -> None:
    print('Unpacking files...')

    with open(DEPLOY_PACKAGE_FILENAME, 'r') as f:
        package = json.loads(f.read())

    for file in package:
        parents = file.split('/')[:-1]

        parent_path = ''
        full_path = ''
        for parent in parents:
            full_path += f'/{parent}'
            if parent not in os.listdir(parent_path):
                os.mkdir(full_path)
            parent_path = full_path

        with open(file, 'w', encoding='utf-8') as f:
            print(f'Unpacking file: {file}')
            f.write(package[file])


def delete_package_file() -> None:
    print('Deleting package file...')
    os.rmdir(DEPLOY_PACKAGE_FILENAME)


def main() -> None:
    if platform != 'esp32':
        raise Exception('Platform is not esp32 - aborting...')

    clean_device()

    unpack()

    delete_package_file()

    print('Done!')


if __name__ == '__main__':
    main()
