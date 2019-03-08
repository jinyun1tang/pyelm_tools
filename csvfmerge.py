import csv
import numpy as np
import os,time,sys,argparse


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--csvfiles', dest="csvfiles", metavar='csvfiles', type=str, nargs='*', default=[""],
  help='csv files to be merged')

parser.add_argument('--mergf', dest="mergf", metavar='mergf', type=str, nargs=1, default=[""],
  help='output csv files')


args = parser.parse_args()

csvfiles=args.csvfiles
outfile=args.mergf[0]

name=[]
rows=[]
rowt=[]
#for file in csvfiles:
for file in csvfiles:
    words=file.split('.')
    name.append(words[1])
    rowt=[]
    with open(file,'rb') as f:
        reader=csv.reader(f,delimiter=',')
        for row in reader:
            rowt.append(row)
    rows=rows+rowt

nf=len(name)
lenf=len(rows)/nf

with open(outfile,'w') as f:
    for j in range(nf-1):
        f.write('%s,'%name[j])
    f.write('%s\n'%name[nf-1])
    for j in range(lenf):
        for k in range(nf-1):
            f.write('%s,'%(rows[j+k*lenf][0]))
        f.write('%s\n'%(rows[j+(nf-1)*lenf][0]))
