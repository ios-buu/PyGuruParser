from suppose import parser
import argparse
a_parser = argparse.ArgumentParser(description="p18004 server example")
a_parser.add_argument('--host')
a_parser.add_argument('--username')
a_parser.add_argument('--password')
a_parser.add_argument('--database')
args = a_parser.parse_args()

parser.convert(args.host,args.username,args.password,args.database)