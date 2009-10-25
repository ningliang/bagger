# Methods we need
#
#  1) convert :: LibXML2Tree => MyTree
#        converts a tree produced from libxml2 parsing into one that's "MyTree",
#        
#  2) insert  :: MyTreeTrie -> MyTree -> MyTreeTrie
#        
#  3) 

from cobra.steve.util.prelude import *


class MyTree(object):
  def __init__(self, name, id=None, children=(), text=None):
    self.name = name
    self.id = id
    self.children = list(children)
    self.text = text
    
  def FullName(self):
    if self.id is None:
      return self.name
    return "%s.%s" % (self.name, self.id)
    
  _cached_len = None
  def __len__(self):
    if self._cached_len is not None:
      return self._cached_len
    self._cached_len = 1 + sum(len(c) for c in self.children)
    return self._cached_len
    
  def Print(self, out=None, indent=0):
    if out is None:
      out = sys.stdout
    spaces = "  " * indent
    print spaces, self.name, (self.text if self.text else '')
    for child in self.children:
      child.Print(out, indent + 1)

      
def XmlNodeToMyTree(xml_node, n=0):  
  kwargs = {'name': xml_node.name}
  if xml_node.hasProp('id'):
    kwargs['id'] = xml_node.prop('id')  
  direct_children = GetDirectChildren(xml_node)  
  if any(x.type == 'text' for x in direct_children):
    if all(IsFlowingTextTag(x) for x in direct_children):      
      kwargs['text'] = PrintToText(direct_children)      
    else:
      # Mixed text and non-text children      
      kwargs['children'] = MakeSeparateTextChildren(direct_children)
  else:
    kwargs['children'] = (XmlNodeToMyTree(x, n=n+1) for x in direct_children)
  return MyTree(**kwargs)

  
def GetDirectChildren(xml_node):
  direct_children = []
  child = xml_node.children
  while child is not None:
    if child.type == 'element' or (child.type == 'text' and child.getContent().strip()):
      direct_children.append(child)
    child = child.next
  return direct_children
  
  
def IsFlowingTextTag(xml_node):
  if xml_node.type == 'text':
    return True
  return xml_node.name in set(['br', 'i', 'b', 'strong', 'em', 'ul', 'font'])

  
def NotIsFlowingTextTag(xml_node):
  return not IsFlowingTextTag(xml_node)

  
def MakeSeparateTextChildren(children):
  mytree_children = []
  child_iter = iter(children)
  while True:
    text_kids = list(takewhile(IsFlowingTextTag, child_iter))
    if text_kids:
      text = PrintToText(text_kids)
      new_node = MyTree(name='text', text=text)
      mytree_children.append(new_node)    
    element_kids = list(XmlNodeToMyTree(x) for x in takewhile(NotIsFlowingTextTag, child_iter))
    if element_kids:
      mytree_children.extend(element_kids)
    if not text_kids and not element_kids:
      break
  return mytree_children 
  
  
def PrintToText(xml_node_list, chunks=None):
  text_chunks = chunks or []
  for xml_node in xml_node_list:
    if xml_node.type == 'text':
      text_chunks.append(xml_node.getContent().strip())
    elif xml_node.type== 'element':
      text_chunks.append('<%s>' % xml_node.name)
      PrintToText(GetDirectChildren(xml_node), chunks=text_chunks)
      text_chunks.append('</%s>' % xml_node.name)  
  if chunks is None:
    return ''.join(text_chunks)
