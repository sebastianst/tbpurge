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
    purge_tbdir(args.path, args.keep, args.dryrun)

def parse_args():
    parser = argparse.ArgumentParser(description=\
            "Purge Titanium Backup directory, only keeping newest backup(s) for each app")
    parser.add_argument("path", nargs="?", default=".",
            help="path to TB directory (default: current directory)")
    parser.add_argument("-k", "--keep", type=int, default=1,
            help="number of newest backups to keep per app (default: 1)")
    parser.add_argument("-d", "--dryrun", action='store_true',
            help="dryrun - only show what would be deleted")


    args = parser.parse_args()

    assert isdir(args.path), f"{args.path} is not a directory"
    assert args.keep > 0,\
        "Keep at least one backup, or you might as well just delete the whole directory"

    return args


def purge_tbdir(tbpath: str, keep: int, dryrun: bool):
    groups = {}
    # collect directory content
    print("Parsing properties files...")
    for i, propfile in enumerate(iglob(tbpath + '/*.properties')):
        print(f'{i}\t{basename(propfile)}   ', end='\r')

        base = splitext(propfile)[0]
        files = glob(f'{base}.*')

        name, date = parse_name_date(base)
        md5 = parse_apk_md5(propfile)
        apkfile = glob(f"{tbpath}/{name}-{md5}.apk.*") if md5 else None
        # If there's an apk, add it to the files list
        if apkfile:
            apkfile = apkfile[0]
            files.append(apkfile)
        else:
            apkfile = None

        groups.setdefault(name, []).append(\
                {'files': set(files), 'date': date, 'apk': apkfile})

    # delete all but latest files per app
    for name, appgroups in groups.items():
        print(name)
        appgroups.sort(key=lambda x: x['date'], reverse=True)
        keep_newest_groups(appgroups, keep)
        for group in appgroups[keep:]:
            delete_group_files(group, dryrun)
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

def keep_newest_groups(appgroups, keep):
    """Removes apks of groups that should be kept from groups that will be
    deleted. This can happen if APKs didn't get updated."""
    for group in appgroups[0:keep]:
        print("> keeping", group['date'].strftime(DATEF))
        # remove apk from other groups so we don't accidentially delete a non-updated app
        apkfile = group['apk']
        if apkfile:
            for othergroup in appgroups[keep:]:
                othergroup['files'].discard(apkfile)

def delete_group_files(group, dryrun):
    print("> deleting", group['date'].strftime(DATEF))
    files, apkfile = group['files'], group['apk']
    for file in files:
        if isfile(file):
            print('>> rm', file)
            if not dryrun:
                os.remove(file)
        else:
            # apk already got deleted by an earlier group
            print('>> --', file)
    # apk is part of another group that is kept
    if apkfile and apkfile not in files:
        print('>> ++', apkfile)


if __name__ == '__main__':
    main()
