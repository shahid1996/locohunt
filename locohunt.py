import argparse
import sys
import threading
import os
import re
import csv
from pull import PULL
from parser import PARSER

pull = PULL()

class LOCOHUNT:

	def __init__(self, prs):
		self.tgtlist = prs.list
		self.regexs  = prs.regexs

	def engage(self):
		pull.run(
			"Starting Locohunt RGX [{regexs}] FLS [{files}]".format(
				regexs=pull.DARKCYAN+str(len(self.regexs))+pull.END,
				files=pull.DARKCYAN+str(len(self.tgtlist))+pull.END,	
			)
		)
		pull.linebreak()

		for tgt in self.tgtlist:
			ds_list = []

			try:
				fl  = open(tgt)
				lns = fl.read().splitlines()
			except UnicodeDecodeError:
				continue

			for ln in lns:
				for (regname, regvalue) in self.regexs.items():
					if re.search(regvalue, ln, re.I):
						ds_list.append( (regname, ln, lns.index(ln)+1) )

			if ds_list:
				pull.info(
					"Path: {filepath}".format(
						filepath=pull.YELLOW+tgt+pull.END
					)
				)

				for ds in ds_list:
					pull.liner(ds[2], ds[0], ds[1])

				pull.linebreak()

def main():
	parser = argparse.ArgumentParser(add_help=False)

	parser.add_argument('-h', '--help', dest="help", default=False, action="store_true")
	parser.add_argument('-t', '--target', dest="target", default="", type=str)
	parser.add_argument('-r', '--regex', dest="regex", default="", type=str)
	parser.add_argument('-f', '--regex-json', dest="regfile", default="", type=str)
	parser.add_argument('-d', '--depth', dest="depth", default=0, type=int)

	opts = parser.parse_args()
	parser = PARSER(opts)

	locohunt = LOCOHUNT(parser)
	locohunt.engage()

if __name__ == "__main__":
	pull.logo()
	main()