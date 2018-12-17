#!/usr/bin/python

import sys
import os
import yaml
import argparse

def load_config_file(filepath):
    try:
        with open(filepath, 'r') as file:
            f = yaml.load(file)
            return f
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=1, help="Input yaml file")
    args = parser.parse_args()

    yml = load_config_file(args.file[0])
    