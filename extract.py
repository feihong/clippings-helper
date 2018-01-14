from pathlib import Path
import re
from datetime import datetime
from collections import defaultdict
import json

import maya
import click


defaults_file = Path(__file__).parent / 'defaults.json'


@click.command()
@click.option('--title', default='', help='Title of book/document')
@click.option('--date', help='Date from which you wish to start extraction')
def main(title, date):
    """
    Print all clippings text for given title, starting from given date.

    """
    import ipdb; ipdb.set_trace()
    if not title:
        title = get_default_title()
    start_dt = maya.parse(date).datetime(naive=True)

    clippings_file = Path('/Volumes/Kindle/documents/My Clippings.txt')
    clippings_file = Path('clippings.txt')
    if not clippings_file.exists():
        print('Kindle is not connected to your computer')
        return

    print()

    # Create map of titles to clips.
    titles = defaultdict(list)
    for clip in get_clips('clippings.txt'):
        title = clip['title']
        titles[title].append(clip)

    for clip in titles[title]:
        if clip['datetime'] > start_dt:
            print(clip['body'] + '\n')

    write_defaults(title=title)


def get_default_title():
    if defaults_file.exists():
        return json.loads(defaults_file.read_text())['title']
    else:
        return None


def write_defaults(title):
    with defaults_file.open('w') as fp:
        json.dump({'title': title}, fp)


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
