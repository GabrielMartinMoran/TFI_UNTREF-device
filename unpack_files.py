import gc
import json
import os
from sys import platform

"""
IMPORTANT: This script is intended to be run in the ESP32, not in the PC
"""

NUM_PACKAGES = 2

DEPLOY_PACKAGE_FILENAMES = [f'deploy-package-{i}.json' for i in range(NUM_PACKAGES)]

FILES_TO_AVOID_DELETION = set(DEPLOY_PACKAGE_FILENAMES + ['state.json'])


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


def unpack_package(package_name: str) -> None:
    print(f'    - Unpacking {package_name}')

    with open(package_name, 'r') as f:
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

    del package

    gc.collect()


def unpack() -> None:
    print('Unpacking files...')

    for package_name in DEPLOY_PACKAGE_FILENAMES:
        unpack_package(package_name)


def delete_package_file() -> None:
    print('Deleting package files...')
    for package_name in DEPLOY_PACKAGE_FILENAMES:
        os.rmdir(package_name)


def main() -> None:
    if platform != 'esp32':
        raise Exception('Platform is not esp32 - aborting...')

    clean_device()

    unpack()

    delete_package_file()

    print('Done!')


if __name__ == '__main__':
    main()
