from pathlib import Path
import shutil
import re
from datetime import datetime
from collections import defaultdict

import maya


def main():
    clippings_file = Path('/Volumes/Kindle/documents/My Clippings.txt')
    if not clippings_file.exists():
        print('Kindle is not connected to your computer')
        return

    shutil.copy(clippings_file, 'clippings.txt')

    titles = defaultdict(list)
    for clip in get_clips('clippings.txt'):
        title = clip['title']
        titles[title].append(clip)

    for clip in titles['明朝那些事儿1']:
        if clip['datetime'] > datetime(2018, 1, 8):
            print(clip['body'] + '\n')


def get_clips(clippings_file):
    EOR = "=========="
    BOM = '\ufeff'

    with open(clippings_file) as fp:
        record = []
        for line in fp:
            if line.strip() == EOR:
                assert record[2] == '', f"Non-blank line expected separating the header from the body of the clipping: {record[2]}"

                match = re.match(r'(?P<title>.*?) \((?P<attribution>.*)\)$', record[0])
                clip = match.groupdict()
                if clip['title'].startswith(BOM):
                    clip['title'] = clip['title'][1:]

                match = re.match(r'- Your (?P<type>Highlight|Bookmark|Note) .* \| Added on (?P<datetime>.*)$', record[1])
                clip.update(match.groupdict())
                clip['type'] = clip['type'].lower()
                clip['datetime'] = maya.parse(clip['datetime']).datetime(naive=True)

                clip['body'] = "\n".join(record[3:]).strip()

                # Yield and reset for next record.
                if clip['body']:
                    yield clip
                record = list()
            else:
                record.append(line.strip())


if __name__ == '__main__':
    main()
