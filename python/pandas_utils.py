#!/usr/bin/env python3
###
import sys,os,argparse
import pandas

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
        description='Pandas utilities for simple datafile transformations.')
  ops = ['csv2tsv', 'summary','showcols','selectcol']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input (CSV|TSV)")
  parser.add_argument("--o", dest="ofile", help="output (CSV|TSV)")
  parser.add_argument("--coltags", help="cols specified by tag (comma-separated)")
  parser.add_argument("--cols", type=int, help="cols specified by idx (1+) (comma-separated)")
  parser.add_argument("-v", "--verbose", action="count")
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
    df = pandas.read_table(fin, delim)
    print("rows: %d ; cols: %d"%(df.shape[0], df.shape[1]))

  elif args.op == 'csv2tsv':
    df = pandas.read_table(fin, ',')
    df.to_csv(fout, '\t', index=False)

  elif args.op == 'showcols':
    df = pandas.read_table(fin, delim)
    for i,coltag in enumerate(df.columns):
      print('%d. %s'%(i+1,coltag))

  elif args.op == 'selectcols':
    df = pandas.read_table(fin, delim)
    if args.cols:
      cols = [(int(col)-1) for col in re.split(r'\s*,\s*', args.cols)]
      ds = df.iloc[:, [cols]]

    elif args.coltags:
      ds = df[[args.coltag]]
    else:
      parser.error('--cols or --coltags required.')
    ds.to_csv(fout, '\t', index=False)

  else:
    parser.error('Unknown operation: %s'%args.op)
