import json
import os
import subprocess
from typing import List

EXCLUDES = {'__pycache__'}

WRITE_FILE_TIMEOUT_SECONDS = 10

WRITE_FILE_TRIES = 3


def search_files_to_copy(path: str) -> List[str]:
    files = []
    for x in os.listdir(path):
        if x in EXCLUDES:
            continue
        curr_path = os.path.join(path, x)
        if os.path.isdir(curr_path):
            files += search_files_to_copy(curr_path)
        else:
            files.append(curr_path)
    return files


def generate_package(files: List[str]) -> dict:
    package = {}
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            package[file] = f.read()
    return package


def main():
    should_generate_package = input('Generate package [yes / no]: ').lower() in {'y', 'yes'}

    if should_generate_package:
        print('Searching for files to deploy...')
        files_to_copy = ['boot.py']
        files_to_copy += search_files_to_copy('src')

        print('Generating deployment package...')
        package = generate_package(files_to_copy)
        with open('deploy-package.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(package))

        print('Uploading packaged scripts (this operation may take some time)...')
        subprocess.run(['ampy', '-p', '/dev/ttyUSB0', 'put', 'deploy-package.json', 'deploy-package.json'],
                       cwd=os.getcwd())
    else:
        print('Skipping package generation...')

    print('Requesting file unpackaging...')
    subprocess.run(['ampy', '-p', '/dev/ttyUSB0', 'run', 'unpackage_files.py'], cwd=os.getcwd())

    print('✅All scripts uploaded!')


if __name__ == '__main__':
    main()
