# code=utf-8
import sys

import yaml
import argparse
from suppose import parser

a_parser = argparse.ArgumentParser(description="p18004 server example")
a_parser.add_argument('--file')
a_parser.add_argument('--host')
a_parser.add_argument('--username')
a_parser.add_argument('--password')
a_parser.add_argument('--database')
args = a_parser.parse_args()

file_name = 'swagger.yaml'

file = open(args.file, 'r', encoding='utf-8')

context = file.read()

x = yaml.load(context)
x['file_path'] = args.file
parser.insert(x, args.host, args.username, args.password, args.database, build=True)
