from cobra.steve.util.prelude import *

flags.DefineString("wordnet_root_directory",
                   "/export/hda3/home/fedele/my/WordNet-3.0",
                   "The root directory in which WordNet is located.")


class PartOfSpeechClassifier(object):
  """A little object that takes words and returns the various parts
  of speech in which it may exist."""

  def __init__(self, wordnet_root):
    pass


class WordNet(object):
  def __init__(self, wordnet_root=None):
    if wordnet_root is None:
      wordnet_root = FLAGS.wordnet_root_directory
    self.wordnet_root = wordnet_root
    self.initialized = False
    self.synset_mapping = {}
    self.pos_mapping = {}
    self.synsets = {}
    self.irregular_verbs = {}

  def LookupPOS(self, word):
    word = word.lower()
    poses = set()
    poses += self.pos_mapping.get(word, set())
    if word in self.irregular_verbs:
      root = self.irregular_verbs[word]
      poses += self.pos_mapping.get(root)

  def Load(self):
    dict_dir = os.path.join(self.wordnet_root, './dict/')
    for file_pos in ('verb', 'noun', 'adj', 'adv'):
      filename = os.path.join(dict_dir, "data.%s" % file_pos)
      print "loading", filename
      for line in WordnetFileLineReader(filename):
        data, gloss = line.strip().split(' | ')
        args = data.split()
        synset_id = int(args.pop(0))
        lex_filenum = args.pop(0)
        synset_type = args.pop(0)
        synset_wordcount = int(args.pop(0), 16)
        synset_words = []
        for n in range(synset_wordcount):
          synset_words.append(args.pop(0))
          lex_id = args.pop(0)
        pointer_count = int(args.pop(0))
        for n in xrange(pointer_count):
          pointer = (args.pop(0) for n in range(4))
          # TODO(fedele): actually process the pointers.
        if file_pos == 'verb':
          # TODO(fedele): extract the frames for verbs.
          pass
        synsets[synset_id] = synset_words
        for word in synset_words:
          self.synset_mapping.setdefault(word, []).append(synset_id)
          self.pos_mapping.setdefault(word, set()).add(synset_type)



def WordnetFileLineReader(path):
  at_start = True
  for line in open(path, 'r'):
    if at_start and re.match(r'  \d+ ', line):
      # A comment line, don't do anything
      continue
    else:
      at_start = False
    yield line


def main(argv):
  print "starting..."
  start_time = time.time()
  synsets, synset_mapping, pos_mapping = LoadWordNet()
  print "took %f seconds to load %d synsets" % (time.time() - start_time,
                                                len(synsets))
  print synset_mapping.get('alarm')
  print pos_mapping.get('alarm')


if __name__ == '__main__':
  app.run()
