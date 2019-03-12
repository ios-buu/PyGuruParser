# code=utf-8
import yaml
import os
import parser
import sys

file_name = 'swagger.yaml'

file = open(sys.argv[1], 'r', encoding='utf-8')

context = file.read()

x = yaml.load(context)

parser.insert(x, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], build=True)