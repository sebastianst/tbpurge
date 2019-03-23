# Titanium Backup Directory Purger
When merging TB directories, backups will accumulate and waste space. Within the
TB app there's a command to clean the backup directory and only keep the newest
backup(s). With this little tool, you can do the same on your PC.

It handles changing archive extensions well and doesn't delete other files in
the directory that don't belong to app backups.

## Usage
```
usage: tbpurge.py [-h] [-k KEEP] [path]

Purge Titanium Backup directory to only keep newest backup(s) for each app

positional arguments:
  path                  Path to TB directory. Defaults to current directory.

optional arguments:
  -h, --help            show this help message and exit
  -k KEEP, --keep KEEP  Number of newest backups to keep per app. Default: 1.
```

Licensed under the GPLv3, see `COPYING`.
Copyright 2019 Sebastian Stammler.
