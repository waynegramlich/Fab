# fcstd_tar_sync.py: Synchronize .fcstd and .tar files.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Functions](#functions)
  * 2.1 [Synchronize](#synchronize)
  * 2.2 [main](#main)
  * 2.3 [synchronize\_directories](#synchronize-directories)
  * 2.4 [unit\_test](#unit-test)

## 1 <a name="introduction"></a>Introduction


Usage: fcstd_tar_sync [OPTIONS] [DIR] ...

Recursively scans directories searching for `.fcstd`/`.FCstd` files
and synchronizes them with associated `.tar` files.  The current
directory is used if no explicit directory or files are listed.

Options:
* [-n] Visit all files without doing anything.  Use with [-v] option.
* [-v] Verbose mode.

Rationale:

A FreeCAD `.fcstd` file is basically a bunch of text files compressed with gzip.
For fun, the `unzip -l XYZ.fcstd` command lists the files contained in `XYZ.fcstd`.
Due to the repetitive nature of the text files contained therein, the gzip algorithm
can achieve significant overall file compression.

A `git` repository basically consists of a bunch files called blob's, where the
term "blob" stands for Binary Large Object.  Each blob represents some version
of a file stored the repository.  Being binary files, `.fcstd` files can be
stored inside of a git repository.  However, the compressed (i.e. binary)
nature  of `.fcstd` files can make the git repository storage requirements
grow at a pretty rapid rate as multiple versions of the `.fcstd` files get stored
into a git repository.

To combat the storage growth requirements, `git` uses a compression algorithm that
is applied to the repository as a whole. These compressed files are called Pack files.
Pack files are generated and updated whenever git decides to do so.  Over time,
the overall git storage requirements associated with uncompressed files grows at a
slower rate than gzip compressed files. In addition, each time a git repositories
are synchronized, the over the wire protocol is via Pack file.

This program will convert a file from compressed in gzip format into simpler
uncompressed format call a `.tar` file.  (`tar` stands for Tape ARchive for
back in the days of magnetic tapes.)  Basically, what this program does is
manage two files in tandem, `XYZ.fcstd` and `XYZ.tar`.  It does this by
comparing the modification times between the two files translates the content
of the newer file on top of the older file.  When done, both files will have
the same modification time.  This program works recursively over an entire
directory tree.

To use this program with a git repository, configure your `.gitignore` to
ignore `.fcstd` files in your repository by adding `*.fcstd` to your
`.gitignore` file.  Run this program before doing a `git commit`
Whenever you update your git repository from a remote one, run this program
to again, to keep the `.fcstd` files in sync with any updated `.tar` files.

## 2 Functions <a name="functions"></a>

### 2.1 Synchronize <a name="synchronize"></a>

def *synchronize*(fcstd\_path:  Path, *dry\_run*:  *bool* = False) -> *str*:

Synchronize an .fcstd file with associated .tar file.

* Arguments:
  * fcstd\_path (Path):
    The `.fcstd` file to synchronize.
  * dry\_run (bool):
    If True, no synchronization occurs and only the summary string is returned.
    (Default: False)
* Returns:
  * (str) a summary string.

Synchronizes an `.fcstd` file with an associated `.tar` file and.
A summary is always returned even in *dry\_run* mode.

### 2.2 main <a name="main"></a>

def *main*() -> None:

Execute the main program.

### 2.3 synchronize\_directories <a name="synchronize-directories"></a>

def *synchronize\_directories*(directory\_names:  Tuple[str, ...], *dry\_run*:  *bool*, *verbose*:  *bool*) -> Tuple[str, ...]:

Synchronize some directories.

* Arguments:
  * *directory\_names* (Tuple[str, ...):
    A list of directories to recursively synchronize.
  * dry\_run (bool):
    If False, the directories are scanned, but not synchronized.  If True, the directories
    are both scanned and synchronized.
  * verbose (bool):
    If True, the a summary message is printed if for each (possible) synchronization.
    The actual synchronization only occurs if *dry\_run* is False.
* Returns
  * (Tuple[str, ...]) containing the summar

### 2.4 unit\_test <a name="unit-test"></a>

def *unit\_test*() -> None:

Run the unit test.
