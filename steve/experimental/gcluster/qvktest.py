import sys
import csvbreaker
from operator import itemgetter


chunk_size = 1000000 - 9020
grouper = itemgetter(0)
path = "/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/top_terminals_before.csv"

total_records = 0
for n, offsets in enumerate(csvbreaker.ShardCSVFile(path, chunk_size, grouper)):
  record_maker = csvbreaker.ShardedCSVRecordMaker(path, offsets, grouper, [])
  for (key, rows) in record_maker:
    items = list(rows)
    print key, len(items)
    total_records += 1
  print "*" * 80
  print >> sys.stderr, n, total_records
  print "*" * 80
  if n > 1:
    break
print >> sys.stderr, "TOTAL RECORDS", total_records
