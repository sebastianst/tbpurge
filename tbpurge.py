#!/usr/bin/env python
#
# Purge Titanium Backup directory, only keeping newest backup(s) for each app
# Copyright © 2019 Sebastian Stammler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from glob import glob, iglob
import os
from os.path import basename, splitext, isfile, isdir
import re
from datetime import datetime

DATEF = "%Y-%m-%d %H:%M:%S"

def main():
    args = parse_args()
    purge_tbdir(args.path, args.keep)

def parse_args():
    parser = argparse.ArgumentParser(description=\
            "Purge Titanium Backup directory, only keeping newest backup(s) for each app")
    parser.add_argument("path", nargs="?", default=".",
            help="path to TB directory (default: current directory)")
    parser.add_argument("-k", "--keep", type=int, default=1,
            help="number of newest backups to keep per app (default: 1)")

    args = parser.parse_args()

    assert isdir(args.path), f"{args.path} is not a directory"
    assert args.keep > 0,\
        "Keep at least one backup, or you might as well just delete the whole directory"

    return args


def purge_tbdir(tbpath: str, keep: int):
    groups = {}
    # collect directory content
    print("Parsing properties files...")
    for i, propfile in enumerate(iglob(tbpath + '/*.properties')):
        print(f'{i}\t{basename(propfile)}   ', end='\r')

        base = splitext(propfile)[0]
        files = glob(f'{base}.*')

        name, date = parse_name_date(base)
        md5 = parse_apk_md5(propfile)
        if md5:
            # If there's an apk, add it to the files list
            files.extend(iglob(f"{tbpath}/{name}-{md5}.apk.*"))

        groups.setdefault(name, []).append({'files': files, 'date': date})

    # delete all but latest files per app
    for name, appgroups in groups.items():
        print(name)
        appgroups.sort(key=lambda x: x['date'], reverse=True)
        for group in appgroups[0:keep]:
            print("> keeping", group['date'].strftime(DATEF))
        for group in appgroups[keep:]:
            delete_group_files(group)
        print()

def parse_name_date(base: str):
    m = re.match(r'([\w.]+)-(20\d{6}-\d{6})', basename(base))
    assert len(m.groups()) == 2, "Couldn't parse app name and date"
    name, date = m.groups()
    date = datetime.strptime(date, '%Y%m%d-%H%M%S')
    return name, date

def parse_apk_md5(propfile: str):
    with open(propfile, 'r') as f:
        for line in f:
            if line.startswith("app_apk_md5"):
                return line.split('=')[1].strip()
    # Didn't find any md5, must be a misc data backup
    return None

def delete_group_files(group):
    print("> deleting", group['date'].strftime(DATEF))
    for file in group['files']:
        print('>> rm', file)
        os.remove(file)


if __name__ == '__main__':
    main()
