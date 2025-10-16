from glob import glob
import sys
from pathlib import Path
import argparse
from zipfile import ZipFile
from typing import Iterable
from collections import OrderedDict
from typing import Optional, Dict, Set
import toml

def escape_string(string: str) -> str:
    return string\
        .replace('\r', '') \
        .replace('\n', '\\n') \
        .replace('\"', '\\"')


def get_potext(key_value_pairs: Iterable[tuple[str, str]]):
    lines = [
        "msgid \"\"",
        "msgstr \"\"",
        f"\"Language: en\\n\"",
        "\"MIME-Version: 1.0\\n\"",
        "\"Content-Type: text/plain\\n\"",
        "\"Content-Transfer-Encoding: 8bit; charset=UTF-8\\n\"",
        ""
    ]

    for key, value in key_value_pairs:
        lines.append(f'msgid "{key}"')
        lines.append(f'msgstr ""')
        lines.extend(map(lambda x: f'"{escape_string(x)}"', value.splitlines(keepends=True)))
        lines.append('')

    return '\n'.join(lines)


def read_string_file(buffer: bytes) -> Optional[str]:
    encodings = ('utf-16', 'utf-8')
    for encoding in encodings:
        try:
            return buffer.decode(encoding)
        except UnicodeDecodeError as e:
            pass
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_directory', help='The directory that contains the data')
    parser.add_argument('output_path')
    parser.add_argument('--config_path', default='config.toml', required=False)

    args = parser.parse_args()

    config_path = Path(args.config_path).expanduser().resolve()
    config = toml.load(open(config_path))

    # TODO: figure out in what order the game seems to be loading things in.
    #  my guess is it goes in alphabetical order.
    data_directory = Path(args.data_directory)

    if not data_directory.is_dir(follow_symlinks=True):
        sys.exit(1)

    data: Dict[str, str] = OrderedDict()

    # Read all text files in the OS file system.
    text_paths: Set[Path] = set()
    for pattern in config['files']['include']['path_patterns']:
        for path in glob(f'**/{pattern}', root_dir=data_directory, recursive=True):
            text_paths.add(Path(path))
        
    for text_path in text_paths:
        data[text_path] = read_string_file(open(data_directory / text_path, 'rb').read())

    # Read all text files in the archive files.
    archive_paths = set()
    for pattern in config['archive']['path_patterns']:
        for path in glob(pattern, root_dir=data_directory):
            archive_paths.add(data_directory / path)
    
    for path in archive_paths:
        zipfile = ZipFile(path)
        for name in zipfile.namelist():
            path = Path(name)
            if not any(map(lambda x: path.match(x), config['files']['include']['path_patterns'])):
                continue
            data[name] = read_string_file(zipfile.read(str(path)))

    # Write out the file.
    output_path = Path(args.output_path).expanduser().resolve()
    with open(output_path, 'w', encoding='utf-8') as fp:
        fp.write(get_potext(data.items()))
