#!/usr/bin/env python3
"""TarSync.py: Synchronize .fcstd and .tar files.

Usage: TarSync.py [OPTIONS] [DIR] ...

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
"""

# [Basic Git Concepts]
# (https://www.oreilly.com/library/view/version-control-with/9781449345037/ch04.html)
#
# FreeCAD forum topics:
# [https://forum.freecadweb.org/viewtopic.php?t=38353&start=30](1)
# [https://forum.freecadweb.org/viewtopic.php?f=8&t=36844a](2)
# [https://forum.freecadweb.org/viewtopic.php?t=40029&start=10](3)
# [https://forum.freecadweb.org/viewtopic.php?p=1727](4)
# [https://forum.freecadweb.org/viewtopic.php?t=8688](5)
# [https://forum.freecadweb.org/viewtopic.php?t=32521](6)
# [https://forum.freecadweb.org/viewtopic.php?t=57737)(7)
# [https://blog.lambda.cx/posts/freecad-and-git/](8)
# [https://tante.cc/2010/06/23/managing-zip-based-file-formats-in-git/](9)


from argparse import ArgumentParser
from io import BytesIO
import os
from pathlib import Path
from tarfile import TarFile, TarInfo
from tempfile import TemporaryDirectory
from typing import List, IO, Optional, Tuple
import time
from zipfile import ZIP_DEFLATED, ZipFile


# main():
def main() -> None:
    """Execute the main program."""
    # Create an *argument_parser*:
    parser: ArgumentParser = ArgumentParser(
        description="Synchronize .fcstd/.tar files."
    )
    parser.add_argument("directories", metavar="DIR", type=str, nargs="*",
                        help="Directory to recursively scan")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="verbose mode")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose mode")
    parser.add_argument("--unit-test", action="store_true",
                        help="run unit tests")

    # Parse arguments:
    arguments = parser.parse_args()
    directories: Tuple[str, ...] = tuple(arguments.directories)
    if arguments.unit_test:
        # Run the unit test:
        unit_test()
        directories = ()
    synchronize_directories(directories, arguments.dry_run, arguments.verbose)


# synchronize_directories():
def synchronize_directories(directory_names: Tuple[str, ...],
                            dry_run: bool, verbose: bool) -> Tuple[str, ...]:
    """Synchronize some directories.

    * Arguments:
      * *directory_names* (Tuple[str, ...):
        A list of directories to recursively synchronize.
      * dry_run (bool):
        If False, the directories are scanned, but not synchronized.  If True, the directories
        are both scanned and synchronized.
      * verbose (bool):
        If True, the a summary message is printed if for each (possible) synchronization.
        The actual synchronization only occurs if *dry_run* is False.
    * Returns
      * (Tuple[str, ...]) containing the summary
    """
    # Recursively find all *fcstd_paths* in *directories*:
    fcstd_paths: List[Path] = []
    directory_name: str
    for directory_name in directory_names:
        suffix: str = "fcstd"
        for suffix in ("fcstd", "fcSTD"):
            fcstd_paths.extend(Path(directory_name).glob(f"**/*.{suffix}"))

    # Perform all of the synchronizations:
    summaries: List[str] = []
    for fcstd_path in fcstd_paths:
        summary: str = synchronize(fcstd_path, dry_run)
        summaries.append(summary)
        if verbose:
            print(summary)  # pragma: no unit cover
    return tuple(summaries)


# Synchronize():
def synchronize(fcstd_path: Path, dry_run: bool = False) -> str:
    """Synchronize an .fcstd file with associated .tar file.

    * Arguments:
      * fcstd_path (Path):
        The `.fcstd` file to synchronize.
      * dry_run (bool):
        If True, no synchronization occurs and only the summary string is returned.
        (Default: False)
    * Returns:
      * (str) a summary string.

    Synchronizes an `.fcstd` file with an associated `.tar` file and.
    A summary is always returned even in *dry_run* mode.
    """
    # Determine timestamps for *fstd_path* and associated *tar_path*:
    tar_path: Path = fcstd_path.with_suffix(".tar")
    fcstd_timestamp: int = int(fcstd_path.stat().st_mtime) if fcstd_path.exists() else 0
    tar_timestamp: int = int(tar_path.stat().st_mtime) if tar_path.exists() else 0

    # Using the timestamps do the synchronization (or not):
    zip_file: ZipFile
    tar_file: TarFile
    tar_info: TarInfo
    fcstd_name: str = str(fcstd_path)
    tar_name: str = str(tar_path)
    summary: str
    if fcstd_timestamp > tar_timestamp:
        # Update *tar_path* from *tar_path*:
        summary = f"{fcstd_name} => {tar_name}"
        if not dry_run:
            with ZipFile(fcstd_path, "r") as zip_file:
                with TarFile(tar_path, "w") as tar_file:
                    from_names: Tuple[str, ...] = tuple(zip_file.namelist())
                    for from_name in from_names:
                        from_content: bytes = zip_file.read(from_name)
                        # print(f"Read {fcstd_path}:{from_name}:"
                        #       f"{len(from_content)}:{is_ascii(from_content)}")
                        tar_info = TarInfo(from_name)
                        tar_info.size = len(from_content)
                        # print(f"tar_info={tar_info} size={tar_info.size}")
                        tar_file.addfile(tar_info, BytesIO(from_content))
                os.utime(tar_path, (fcstd_timestamp, fcstd_timestamp))  # Force modification time.
    elif tar_timestamp > fcstd_timestamp:
        # Update *fcstd_path* from *tar_path*:
        summary = f"{tar_name} => {fcstd_name}"
        if not dry_run:
            with TarFile(tar_path, "r") as tar_file:
                tar_infos: Tuple[TarInfo, ...] = tuple(tar_file.getmembers())
                with ZipFile(fcstd_path, "w", ZIP_DEFLATED) as zip_file:
                    for tar_info in tar_infos:
                        buffered_reader: Optional[IO[bytes]] = tar_file.extractfile(tar_info)
                        assert buffered_reader
                        buffer: bytes = buffered_reader.read()
                        # print(f"{tar_info.name}: {len(buffer)}")
                        zip_file.writestr(tar_info.name, buffer)
                os.utime(fcstd_path, (tar_timestamp, tar_timestamp))  # Force modification time.

    else:
        summary = f"{fcstd_name} in sync with {tar_name}"
    return summary


# unit_test():
def unit_test() -> None:
    """Run the unit test."""
    directory_name: str
    # Use create a temporary *directory_path* to run the tests in:
    with TemporaryDirectory() as directory_name:
        a_content: str = "a contents"
        b_content: str = "b contents"
        buffered_reader: Optional[IO[bytes]]
        c_content: str = "c contents"
        directory_path: Path = Path(directory_name)
        tar_name: str
        tar_file: TarFile
        tar_path: Path = directory_path / "test.tar"
        tar_path_name: str = str(tar_path)
        zip_file: ZipFile
        zip_name: str
        zip_path: Path = directory_path / "test.fcstd"
        zip_path_name: str = str(zip_path)

        # Create *zip_file* with a suffix of `.fcstd`:
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as zip_file:
            zip_file.writestr("a", a_content)
            zip_file.writestr("b", b_content)
        assert zip_path.exists(), f"{zip_path_name=} not created"
        zip_timestamp: int = int(zip_path.stat().st_mtime)
        assert zip_timestamp > 0, f"{zip_path=} had bad timestamp."

        # Perform synchronize with a slight delay to force a different modification time:
        time.sleep(1.1)
        summaries = synchronize_directories((directory_name, ), False, False)
        assert len(summaries) == 1, "Only 1 summary expected"
        summary: str = summaries[0]
        desired_summary: str = f"{zip_path_name} => {tar_path_name}"
        assert summary == desired_summary, f"{summary} != {desired_summary}"
        assert tar_path.exists(), f"{tar_path_name=} not created"
        tar_timestamp: int = int(tar_path.stat().st_mtime)
        assert tar_timestamp == zip_timestamp, f"{zip_timestamp=} != {tar_timestamp=}"

        # Now read *tar_file* and verify that it has the correct content:
        with TarFile(tar_path, "r") as tar_file:
            tar_infos: Tuple[TarInfo, ...] = tuple(tar_file.getmembers())
            for tar_info in tar_infos:
                buffered_reader = tar_file.extractfile(tar_info)
                assert buffered_reader, f"Unable to read {tar_file=}"
                content: str = buffered_reader.read().decode("latin-1")
                found: bool = False
                if tar_info.name == "a":
                    assert content == a_content, f"'{content}' != '{a_content}'"
                    found = True
                elif tar_info.name == "b":
                    assert content == b_content, f"'{content}' != '{b_content}'"
                    found = True
                assert found, f"Unexpected tar file name {tar_info.name}"

        # Now run synchronize again and verify that nothing changed:
        summaries = synchronize_directories((directory_name, ), False, False)
        assert len(summaries) == 1, "Only one summary expected"
        summary = summaries[0]
        desired_summary = f"{str(zip_path)} in sync with {str(tar_path)}"
        assert summary == desired_summary, f"'{summary}' != '{desired_summary}'"
        zip_timestamp = int(zip_path.stat().st_mtime)
        tar_timestamp = int(tar_path.stat().st_mtime)
        assert tar_timestamp == zip_timestamp, f"timestamps {zip_timestamp=} != {tar_timestamp=}"

        # Now update *tar_file* with new content (i.e. `git pull`).:
        time.sleep(1.1)  # Use delay to force a different timestamp.
        with TarFile(tar_path, "w") as tar_file:
            tar_info = TarInfo("c")
            tar_info.size = len(c_content)
            tar_file.addfile(tar_info, BytesIO(bytes(c_content, "latin-1")))
            tar_info = TarInfo("a")
            tar_info.size = len(a_content)
            tar_file.addfile(tar_info, BytesIO(bytes(a_content, "latin-1")))

        # Verify that the timestamp changed and force a synchronize().
        new_tar_timestamp: int = int(tar_path.stat().st_mtime)
        assert new_tar_timestamp > tar_timestamp, f"{new_tar_timestamp=} <= {tar_timestamp=}"
        summary = synchronize(zip_path)
        desired_summary = f"{tar_path_name} => {zip_path_name}"
        assert summary == desired_summary, f"'{summary}' != '{desired_summary}'"

        # Verify that the *zip_path* got updated verify that the content changed:
        new_zip_timestamp: int = int(zip_path.stat().st_mtime)
        assert new_zip_timestamp == new_tar_timestamp, (
            f"{new_zip_timestamp=} != {new_tar_timestamp=}")
        with ZipFile(zip_path, "r") as zip_file:
            zip_names: Tuple[str, ...] = tuple(zip_file.namelist())
            for zip_name in zip_names:
                zip_content: str = zip_file.read(zip_name).decode("latin-1")
                assert buffered_reader
                found = False
                if zip_name == "a":
                    assert zip_content == a_content, "Content mismatch"
                    found = True
                elif zip_name == "c":
                    assert zip_content == c_content, "Content mismatch"
                    found = True
                assert found, "Unexpected file '{zip_name}'"


if __name__ == "__main__":
    main()
