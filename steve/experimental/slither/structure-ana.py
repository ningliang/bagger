from cobra.steve.util.prelude import *
from cobra.steve.experimental.slither import crawlstate, mytree

from collections import defaultdict

import libxml2


flags.DefineString("compare", None, "set to a comma separated pair of docids to compare them")
flags.DefineInteger("findlike", None, "find other docids that are like this one")

    
      
    
def MakeTree(url, path):
  data = open(path).read()
  doc = libxml2.htmlParseDoc(data, None)
  try:
    tree = mytree.XmlNodeToMyTree(doc)
  finally:
    doc.freeDoc()
  return tree
  

def ChildrenToMap(tree_node):
  tree_map = defaultdict(list)
  for c in tree_node.children:
    tree_map[c.FullName()].append(c)
  return tree_map
  
  
def ClipText(text, size):
  if len(text) > size:
    return "%s..." % text[:size-3]
  else:
    return text

  
def CoRecurse(tree1, tree2, indent=0, ctxt=None, noisy=False):
  if ctxt is None:
    ctxt = {'text': defaultdict(int),
            'struct': defaultdict(int),
            'coverage': 0
           }
  tree1_children = ' '.join(c.FullName() for c in tree1.children)
  tree2_children = ' '.join(c.FullName() for c in tree2.children)
  if noisy:
    print indent * "  ", tree1.FullName(), ("[%s] vs [%s]" % (ClipText(tree1.text, 40), ClipText(tree2.text, 40)) 
                                            if tree1.text != tree2.text else '')
    spaces = "  " * (indent + 1)
  if tree1_children == tree2_children:
    # These two trees have the exact same subnode types, recurse!
    for child1, child2 in zip(tree1.children, tree2.children):
      CoRecurse(child1, child2, indent + 1, ctxt, noisy)
  else:
    tree1_map = ChildrenToMap(tree1)
    tree2_map = ChildrenToMap(tree2)        
    common_set = set(tree1_map.keys()).intersection(tree2_map.keys())    
    if noisy:
      print spaces, "DISIMILAR SUBTREES"
      print spaces, tree1_children
      print spaces, tree2_children      
    for name in common_set:
      children1_list = tree1_map.get(name, [])
      children2_list = tree2_map.get(name, [])
      if len(children1_list) == 1 and len(children2_list) == 1:
        CoRecurse(children1_list[0], children2_list[0], indent + 1, ctxt, noisy)
      else:
        pass
  return ctxt
  
  
def CompareDocs(docs, docid1, docid2, noisy=False):
  doc_a  = docs[docid1]
  doc_b  = docs[docid2]
  tree_a = MakeTree(*doc_a)
  tree_b = MakeTree(*doc_b)  
  ctxt = CoRecurse(tree_a, tree_b, noisy=noisy)  
  coverage = 2.0 * ctxt['coverage'] / (len(tree_a) + len(tree_b))
  return coverage
  
    
def ErrorHandler(ctx, error):
  pass
  

def PrintSimilarities(docs_and_similarities, top=-1):
  for n, (d2, similarity) in enumerate(docs_and_similarities[:10]):
      print "%4d %6d %5.3f" % (n, d2, similarity)
  
def FindMoreLike(crawl_state, d1, docs, sample_size=100, top=10, noisy=False):
  docids = docs.keys()
  test_docids = random.sample(docids, sample_size)
  docs_and_similarities = []  
  for n, d2 in enumerate(test_docids):    
    similarity = CompareDocs(docs, d1, d2)
    docs_and_similarities.append((d2, similarity))
    if noisy and n % 10 == 0:
      print ".",
      
  docs_and_similarities.sort(reverse=True, key=itemgetter(1))
  if noisy:
    print
    print "TOP 10:"
    PrintSimilarities(docs_and_similarities, top=10)

  return docs_and_similarities[:top]


     
  
    
    
  

def ClusterShit(crawl_state, docs):
  docids = docs.keys()
  clusters = []
  while True:
    docid = random.choice(docids)
    cluster_similarities = [(c, CompareDocidToCluster(docs, d2, c)) for c in clusters]
    cluster_similarities.sort(reverse=True, key=itemgetter(1))
    for cluster, similarity in cluster_similarities:
      if cluster.DocidSimilar(docid, similarity):
        cluster.AddDocid(docid, similarity)
        break
    else:
      new_cluster = CreateCluster(crawl_state, docid, docs)
    
  
    
    

def main(argc):
  crawl, crawl_state = crawlstate.CrawlStateFromFlags()
  start_time = time.time()
  libxml2.registerErrorHandler(ErrorHandler, None)
  docs = dict((docid, (url, path)) for docid, url, path in crawl_state.DocsCachedLocallyIter())
  print len(docs)
  print time.time() - start_time
  docids = docs.keys()  
  
  if FLAGS.compare:
    d1, d2 = map(int, FLAGS.compare.split(','))
    print CompareDocs(docs, d1, d2, noisy=True)
    return
  elif FLAGS.findlike:
    d1 = FLAGS.findlike
    FindMoreLike(crawl_state, d1, docs, noisy=True)
  elif FLAGS.cluster:
    ClusterShit(crawl_state, docs)
  else:
    docid_range = docids[:25]    
    print "     %s" % " ".join("%4d" % d for d in docid_range)
    for d1 in docid_range:
      coverages = []
      for d2 in docid_range:      
        coverage = CompareDocs(docs, d1, d2)
        coverages.append(coverage)
      coverages_row_str = " ".join("%4.2f" % x for x in coverages)
      print "%4d %s %4d" % (d1, coverages_row_str, d1)    
  return
  
  for docid in docids[:100]:
    print docid
    similarities = [(other_docid, CompareDocs(docs, docid, other_docid)) for other_docid in docids[:100]]
    similarities.extend(FindMoreLike(crawl_state, docid, docs, 50, 50))
    similarities.sort(reverse=True, key=itemgetter(1))
    PrintSimilarities(similarities, top=10)    
  
  
if __name__ == '__main__':
  app.run()