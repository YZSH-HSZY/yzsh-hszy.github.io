import re
import shutil
import sys
import argparse
import os
from os.path import splitext, join, dirname, basename, abspath, isdir
from typing import List

CURRENT_FILE_PATH = dirname(abspath(__file__))

REMOVE_DIRS: List[str] = ["author", "category", "feeds", "theme"]

REGEX_PATH: List[re.Pattern] = [re.compile(r".*\.html$")]

def clear_dir():
    args.log.write("start clear dir...\n")

    for _ in os.listdir(args.path):
        the_handle_dir_path = join(args.path, _)
        if isdir(the_handle_dir_path) and _ in REMOVE_DIRS:
            args.log.write(f"remove: {the_handle_dir_path}\n")
            shutil.rmtree(the_handle_dir_path)
    
    args.log.write("start clear dir done.\n")

def clear_other_match_files():
    args.log.write("start clear other files...\n")

    for root, dirs, files in os.walk(args.path, topdown=False):
        for file in files:
            the_handle_file_path = join(root, file)
            if any([_.match(file) for _ in REGEX_PATH]):
                args.log.write(f"remove: {the_handle_file_path}\n")
                os.remove(the_handle_file_path)
        
    args.log.write("start clear other files done.\n")

def clear_main():
    args.log.write("clear main operation starting...\n")

    if not isdir(args.path):
        args.log.write("clear path is illegality.\n")
    
    clear_dir()
    clear_other_match_files()

    args.log.write("clear done.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='clear pelican auto generate content.')
    
    parser.add_argument(
        '--path', default=CURRENT_FILE_PATH, type=str,
        help='the generate static website path.')
    
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('w'),
        help='the clear output log information file.')
    args = parser.parse_args()
    
    args.log.write(f"start clear path {args.path}\n")

    clear_main()

    args.log.close()