# Titanium Backup Directory Purger
When merging TB directories, backups will accumulate and waste space. Within the
TB app there's a command to clean the backup directory and only keep the newest
backup(s). With this little tool, you can do the same on your PC.

It handles changing archive extensions well and doesn't delete other files in
the directory that don't belong to app backups.
If several backups share an apk file, it is kept if one of the backups is to be
kept.

## Usage
```
usage: tbpurge.py [-h] [-k KEEP] [-d] [path]

Purge Titanium Backup directory, only keeping newest backup(s) for each app

positional arguments:
  path                  path to TB directory (default: current directory)

optional arguments:
  -h, --help            show this help message and exit
  -k KEEP, --keep KEEP  number of newest backups to keep per app (default: 1)
  -d, --dryrun          dryrun - only show what would be deleted
```

Licensed under the GPLv3, see `COPYING`.
Copyright 2019 Sebastian Stammler.
