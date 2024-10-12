"""
Simple fuzzy finder implementation.

Provide a path to a directory as first argument and 
    a string query as second. The program will then 
    try to fuzzy match the query against the files 
    in the directory.

"""
import argparse
import pathlib
import sys
import os

from termcolor import colored

from string import printable


class Fuzzable:
    """
    Receives a path/query string and counts all the characters inside to
        creat a `non_zero` dict containing the characters that appear
        more than once.
    """

    path: str
    shared: dict # Uinitialized and unused for query
    non_zero: dict

    def __init__(self, path: str):
        self.path = path 
        letter_counts = {x: [0, []] for x in printable} # TODO: Check valid filename characters
        for idx, char in enumerate(path):
            letter_counts[char][0] += 1
            letter_counts[char][1].append(idx)

        self.non_zero = {x: y for x, y in letter_counts.items() if y[0] > 0}


def compare_dicts(fuzz1: Fuzzable, fuzz2: Fuzzable) -> bool:
    """
    Returns True if dict1 contains the same keys as dict2, and dict1
    has equal or greater counts of characters (aka dict1 contains dict2).
    """

    # Shave off letters not appearing in fuzz2
    common_dict: dict = {x: y for x, y in fuzz1.non_zero.items() if x in fuzz2.non_zero}

    if len(common_dict) != len(fuzz2.non_zero):
        return False

    # Check sizes
    for key in common_dict:
        file_count  = common_dict[key][0]
        query_count = fuzz2.non_zero[key][0]
        if not file_count >= query_count:
            return False
        common_dict[key][1] = common_dict[key][1][:query_count]

    fuzz1.shared = common_dict
    return True


def colorize(fuzzable: Fuzzable, color: str) -> str:
    matching_indexes = []
    for key in fuzzable.shared:
        for i in fuzzable.shared[key][1]:
            matching_indexes.append(i)
        
    path = pathlib.Path(fuzzable.path)
    #print(f"DEBUG: {path = }")
    #print(f"DEBUG: {fuzzable.shared = }")
    output   = ""
    dirname  = path.parent

    for idx, char in enumerate(str(path.absolute())):
        if idx in matching_indexes:
            output += colored(char, color) # type: ignore
        else:
            output += char

    return os.path.join(dirname, output)


def main(path: pathlib.Path, query: str, color: str) -> None:
    """
    Main program logic. It does some quick checks on the directory path,
        checks on whether it should just list the directory, and if a 
        query is received, tries to find matches based on letter counts.
    """
    if not path.exists():
        print(f"Path '{path}' does not exist.", file=sys.stderr)

    if not path.is_dir():
        print(f"Path '{path}' is not a directory.", file=sys.stderr)

    files_iter = os.scandir(path)

    # print(f"DEBUG: {query = }")
    if len(query) == 0:
        for file in files_iter:
            print(file.path)
        exit(0)

    fuzzable_query: Fuzzable = Fuzzable(query) # type: ignore

    for file in files_iter:
        fuzzable_file = Fuzzable(os.path.join(path.absolute(), file.name))
        if compare_dicts(fuzzable_file, fuzzable_query):
            print(colorize(fuzzable_file, color))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="FuzzySearch",
        description="Fuzzy find files or directories!",
    )

    parser.add_argument("path")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("-c", "--color", nargs=1, default="red", choices=[
        "black",
        "grey",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "light_grey",
        "dark_grey",
        "light_red",
        "light_green",
        "light_yellow",
        "light_blue",
        "light_magenta",
        "light_cyan",
        "white",
    ])

    args = parser.parse_args()
    main(pathlib.Path(args.path), args.query, args.color[0])
