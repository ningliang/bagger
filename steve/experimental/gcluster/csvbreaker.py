"""Utility functions to break a CSV file into chunks for efficient multiprocessor
processing.

NOTE: I have no clue how this all actually works.  There are almost certainly a lot
of off-by-one errors that must magically cancel out.
"""

from cobra.steve.util.prelude import *
import csv


class RetardedFileReader(object):
  """On some platforms, when you use iter(file), the underlying file's tell() method
  may get out of sync due to buffering.  This is a small wrapper around a file object
  that does it correctly.
  """
  def __init__(self, f):
    self.f = f
    self.real_offset = 0

  def __iter__(self):
    while True:
      nextline = self.f.next()
      if not nextline:
        break
      self.real_offset += len(nextline)
      yield nextline

  def tell(self):
    return self.real_offset

  def next(self):
    ret = self.f.next()
    self.real_offset += len(ret)
    return ret

  def seek(self, offset):
    self.f.seek(offset)
    self.real_offset = offset



class ShardedCSVRecordMaker(object):
  """Given a local file path to a CSV file along with a range of offsets to process, this
  class produces an iterable over the records within that range.
  """
  def __init__(self, path, (start_offset, end_offset), grouper=None, integer_columns=(), skip_first_line=True):
    self.path = path
    self.start_offset = start_offset
    self.end_offset = end_offset
    self.grouper = grouper
    self.integer_columns = integer_columns
    self.skip_first_line = skip_first_line

  def __iter__(self):
    real_file = RetardedFileReader(open(self.path))
    real_file.seek(self.start_offset)
    if self.skip_first_line and self.start_offset == 0:
      real_file.next() # Skip the first line for these CSV files.
    record_iter = csv.reader(real_file)
    if self.integer_columns:
      identity = lambda x: x
      transform = [n in self.integer_columns and int or identity for n in range(max(self.integer_columns) + 1)]
      record_iter = imap(lambda xs: [f(x) for f, x in izip_longest(transform, xs, fillvalue=identity)],
                         record_iter)
    else:
      print "NOT USING INTEGER_COLUMNS", self.integer_columns
    if self.grouper is not None:
      record_iter = groupby(record_iter, self.grouper)
      # We skip the first group we encounter under the assumption that the previous shard would
      # have already taken care of it.  We don't need to do this if this is the first shard.
      # See below for the contortions to ensure this works.
      if self.start_offset > 0:
        record_iter.next()
    return takewhile(lambda x: real_file.tell() <= self.end_offset + 1, record_iter)

  def IdString(self):
    return "%s SHARD[%d-%d]" % (self.path, self.start_offset, self.end_offset)


def ShardCSVFile(path, chunk_size, grouper=None):
  """

  """
  f = open(path)
  f.seek(0, 2)
  file_size = f.tell()
  f.seek(0)
  for offset in range(0, file_size + chunk_size - 1, chunk_size):
    end_offset = min(offset + chunk_size, file_size)
    # If our random start_offset is in the middle of a line, our RecordMaker above
    # should process it as part of the previous chunk.  Thus, we want to get to the next
    # valid line, which is easy:  Of course, maybe we're already at the start of the file.
    if offset > 0:
      f.seek(offset)
      f.readline()
      start_offset = f.tell()
    else:
      start_offset = 0
    if start_offset > end_offset:
      break
    if grouper is not None and start_offset > 0:
      # If we aren't grouping, we've done enough.  However, if we _are_ grouping, we need
      # to do a little more - again, our RecordMaker above should process all lines that have
      # the same key, blasting through its shard's end_offset.  Now, normally we expect that
      # our random offset has dumped us in the middle of a string of records to be grouped -
      # thus we should IGNORE the first group extracted from here.  However, we may have
      # gotten (un)lucky and chosen to split right where one string of records begins.
      # In this case, we have to seek back to the start of the PREVIOUS line, look at the
      # keys for both - if they AREN'T the same, then smudge the offset backwards a bit
      # so that skipping the groupby's first group does the correct thing.
      f.seek(start_offset - 1)
      prev_line_start = _FindCurrentLineStart(f) + 1
      f.seek(prev_line_start)
      temporary_csv_reader = csv.reader(f)
      prev_line = temporary_csv_reader.next()
      first_line = temporary_csv_reader.next()
      if grouper(prev_line) != grouper(first_line):
        start_offset = prev_line_start
    # And finally, make sure our end_offset also ends on a line, or else shit gets fucked up.
    # So now our start and end_offsets should be correct.
    f.seek(end_offset)
    end_offset = _FindCurrentLineEnd(f)
    yield (start_offset, end_offset)


def _FindCurrentLineStart(f):
  STEP_SIZE = 1000
  start_pos = f.tell()
  try:
    while True:
      p1 = f.tell()
      f.seek(-STEP_SIZE, 1)
      if f.tell() == 0:
        # We're in the first line.
        return 0
      raw_text = f.read(STEP_SIZE)
      p2 = f.tell()
      assert p1 == p2, "seek then read yielded two different pos: %d vs %d (delta = %d)" % (p1, p2, p2 - p1)
      n = raw_text.rfind("\n")
      if n >= 0:
        # Found a newline!  Return its offset.
        return p1 - STEP_SIZE + n
      else:
        # No newline found, step backwards (to undo our read) and continue searching.
        f.seek(-STEP_SIZE, 1)
  finally:
    f.seek(start_pos)


def _FindCurrentLineEnd(f):
  STEP_SIZE = 1000
  start_pos = f.tell()
  try:
    while True:
      p1 = f.tell()
      raw_text = f.read(STEP_SIZE)
      if not raw_text:
        return f.tell()
      assert f.tell() == p1 + STEP_SIZE
      n = raw_text.find('\n')
      if n >= 0:
        return p1 + n
  finally:
    f.seek(start_pos)
