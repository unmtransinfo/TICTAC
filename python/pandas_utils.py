#!/usr/bin/env python3
###
import sys,os,argparse
import pandas

if __name__=='__main__':
  parser = argparse.ArgumentParser(
        description='Pandas utilities for simple datafile transformations.')
  ops = ['csv2tsv', 'summary','showcols','extractcol']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i",dest="ifile",help="input (CSV|TSV)")
  parser.add_argument("--o",dest="ofile",help="output (CSV|TSV)")
  parser.add_argument("-v","--verbose",action="count")
  args = parser.parse_args()

  if not args.ifile:
    parser.error('Input file required.')
  fin = open(args.ifile)

  if args.ofile:
    fout = open(args.ofile, "w")
  else:
    fout = sys.stdout

  if args.ifile[-4:].lower()=='.csv': delim=','
  else: delim='\t'

  if args.op == 'summary':
    pass
  elif args.op == 'csv2tsv':
    data = pandas.read_table(fin, ',')
    data.to_csv(fout, '\t', index=False)

  elif args.op == 'showcols':
    data = pandas.read_table(fin, delim)
    for i,coltag in enumerate(data.columns):
      print('%d. %s'%(i+1,coltag))

  else:
    parser.error('Unknown operation: %s'%args.op)
