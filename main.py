import sys
from pathlib import Path
import os
from glob import glob
import argparse
from zipfile import ZipFile
from typing import Iterable
from collections import OrderedDict


def okay(key_value_pairs: Iterable[tuple[str, str]]):
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

        value_lines = value.splitlines(keepends=True)

        lines.append(f'msgstr ""')
        for l in value_lines:
            l = l.replace('\r', '')
            l = l.replace('\n', '\\n')
            l = l.replace('\"', '\\"')
            lines.append(f'"{l}"')
        lines.append('')

    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_directory')
    parser.add_argument('--output_directory', default='.', required=False)
    parser.add_argument('--flatten', default=True, required=False)

    # TODO: figure out in what order the game seems to be loading things in.
    #  my guess is it goes data, texts then patch, in order of name.

    args = parser.parse_args()

    data_directory = Path(args.data_directory)

    if not data_directory.is_dir(follow_symlinks=True):
        sys.exit(1)

    pathname = str(data_directory / '*.pak')
    encodings = ('utf-16', 'utf-8')

    data = OrderedDict()
    
    for path in glob(pathname):
        # Path(path)
        zipfile = ZipFile(path)
        for name in zipfile.namelist():
            p = Path(name)
            if p.suffix != '.txt':
                continue
            d = zipfile.read(str(p))
            s = None
            for encoding in encodings:
                try:
                    s = d.decode(encoding)
                    break
                except UnicodeDecodeError as e:
                    pass
            if s is None:
                print(f'Failed to decode {name}')
                continue
            data[name] = s

    output_directory = Path(args.output_directory).resolve()
    os.makedirs(output_directory, exist_ok=True)

    components = OrderedDict()
    # Go through each data item and split them based on the top-level directory that they're in.

    print(len(data))

    for key, value in data.items():
        component = Path(key).parts[0].lower()
        if component not in components:
            components[component] = OrderedDict()
        # print(component)
        components[component][key] = value

    for component, strings in components.items():
        output_path = output_directory / f'{component}.en.po'
        with open(output_path, 'w') as fp:
            lines = okay(strings.items())
            fp.writelines(lines)
