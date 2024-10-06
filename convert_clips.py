#!/usr/bin/env python

# Convert all files in a directory to a given encoding using ffmpeg


import argparse
import os
import subprocess

arg_parser = argparse.ArgumentParser(description='Convert all files in a directory to a given encoding using ffmpeg')

arg_parser.add_argument('--dir', help='The directory containing the files to convert', default='/Volumes/OPTIPHONIC/CLIPS')
arg_parser.add_argument('--out-encoding', help='The encoding to convert the files to', default='prores')
arg_parser.add_argument('--out-extension', help='The extension to use for the converted files', default='mov')
arg_parser.add_argument('--accept-all', help='Don\'t prompt for confirmation before converting each file', action='store_true')
arg_parser.add_argument('--recursive', help='Recursively search for files to convert', action='store_true', default=True)

args = arg_parser.parse_args()

dir = args.dir
encoding = args.out_encoding
extension = args.out_extension
accept_all = args.accept_all
recursive = args.recursive

def get_file_encoding(file):
    probe_resp = subprocess.check_output(f"ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 '{file}'", shell=True)
    return probe_resp.decode('utf-8').strip()

def convert_file(file, encoding):
    name = os.path.splitext(file)[0]

    tmpfile = f"{name}_tmp.{extension}"
    finalfile = f"{name}.{extension}"

    retval = os.system(f"ffmpeg -i '{file}' -c:v {encoding} '{tmpfile}'")

    if retval != 0:
        print(f"Failed to convert {file}")
        exit(1)

    os.system(f"rm '{file}'")
    os.system(f"mv '{tmpfile}' '{finalfile}'")

files_to_convert = []

for root, dirs, files in os.walk(dir):
    for file in files:
        if file.startswith('.'):
            continue
        try:
            if get_file_encoding(f"{root}/{file}") == encoding:
                continue
        except subprocess.CalledProcessError:
            print(f"Failed to probe {file}")
            continue
        files_to_convert.append((root, file))

print(f"Found {len(files_to_convert)} files to convert:")
for root, file in files_to_convert:
    print(f"{root}/{file}")

if input('Proceed with conversion? (y/n) ') != 'y':
    exit(0)

for root, file in files_to_convert:
    if accept_all or input(f'Convert {file}? (y/n) ') == 'y':
        convert_file(f"{root}/{file}", encoding)
