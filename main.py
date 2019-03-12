# code=utf-8
import sys

import yaml

from util import parser

file_name = 'swagger.yaml'

file = open(sys.argv[1], 'r', encoding='utf-8')

context = file.read()

x = yaml.load(context)

parser.insert(x, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], build=True)