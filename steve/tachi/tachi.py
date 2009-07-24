from cobra.steve.util.prelude import *

from cobra.steve.tachi import wordnet
from cobra.steve.third_party.BeautifulSoup import *


def ReadSampleFile(path):
  data = open(path).read()
  soup = BeautifulSoup(data)
  current_speaker = None
  for n, p in enumerate(soup.findAll('p')):
    speaker = p.find('sp')
    if speaker is None:
      speaker = current_speaker
      dialogue = p.contents[0]
    else:
      current_speaker = speaker.contents[0]
      dialogue = p.contents[2]
    dialogue = dialogue.strip()
    if dialogue == '(Laughter)':
      continue
    if speaker is not None and dialogue:
      yield speaker, dialogue


def Sentences(words):
  end_punctuation = ('.', '?', '!')
  cur_sentence = []
  for word in words:
    if word[-1] in end_punctuation:
      cur_sentence.append(word[:-1])
      yield cur_sentence
      cur_sentence = []
    else:
      cur_sentence.append(word)
  if cur_sentence:
    yield cur_sentence


def main(argv):
  synsets, synset_mapping, pos_mapping = wordnet.LoadWordNet()
  for speaker, dialogue in ReadSampleFile('sample.html'):
    words = re.sub(r'\s+', ' ', dialogue).lower().split(' ')
    for sentence in Sentences(words):
      pos_sentence = map(lambda x: pos_mapping.get(x, x), sentence)
      print pos_sentence


if __name__ == '__main__':
  app.run()
