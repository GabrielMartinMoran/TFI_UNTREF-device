import json
import os
import subprocess
from dataclasses import dataclass
from typing import List, Optional

USB_INTERFACE = '/dev/ttyUSB0'

EXCLUDES = {'__pycache__'}

WRITE_FILE_TIMEOUT_SECONDS = 10

WRITE_FILE_TRIES = 3

MOCKED_MODULES = [
    {
        'name': 'micropython_typing',
        'rename': 'typing'
    }
]

NUM_PACKAGES = 2


@dataclass
class FileToSend:
    name: str
    name_override: Optional[str] = None

    def get_content(self) -> str:
        with open(self.name, 'r', encoding='utf-8') as f:
            return f.read()

    def get_final_name(self) -> str:
        if self.name_override is not None:
            return self.name_override
        return self.name


def search_files_to_copy(path: str) -> List[FileToSend]:
    files = []
    for x in os.listdir(path):
        if x in EXCLUDES:
            continue
        curr_path = os.path.join(path, x)
        if os.path.isdir(curr_path):
            files += search_files_to_copy(curr_path)
        else:
            files.append(FileToSend(curr_path))
    return files


def generate_packages(files: List[FileToSend]) -> List[dict]:
    packages = []
    package = {}
    for file in files:
        if len(package) >= len(files) / NUM_PACKAGES:
            packages.append(package)
            package = {}
        package[file.get_final_name()] = file.get_content()
    packages.append(package)
    return packages


def search_mocked_modules_to_copy() -> List[FileToSend]:
    modules_content = []
    for mocked_module in MOCKED_MODULES:
        module_content = search_files_to_copy(mocked_module['name'])
        for module in module_content:
            module.name_override = module.name.replace(mocked_module['name'], mocked_module['rename'])
        modules_content += module_content
    return modules_content


def main() -> None:
    print('Searching for files to deploy...')
    files_to_copy = [FileToSend('boot.py')]
    files_to_copy += search_files_to_copy('src')

    files_to_copy += search_mocked_modules_to_copy()

    print('Generating deployment packages...')
    packages = generate_packages(files_to_copy)
    for i, package in enumerate(packages):
        with open(f'deploy-package-{i}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(package))

    print('Uploading packaged scripts (this operation may take some time)...')
    for i, package in enumerate(packages):
        package_name = f'deploy-package-{i}.json'
        print(f'    - Uploading {package_name}')
        subprocess.run(['ampy', '-p', USB_INTERFACE, 'put', package_name, package_name],
                       cwd=os.getcwd())

    print('Requesting file unpacking...')
    subprocess.run(['ampy', '-p', USB_INTERFACE, 'run', 'unpack_files.py'], cwd=os.getcwd())

    print('✅All scripts uploaded!')


if __name__ == '__main__':
    main()
