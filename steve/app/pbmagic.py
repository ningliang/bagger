"""Magic to make protobuffer imports and compilation easier.

Its a pain in the buttocks to have to call the proto compiler
every time you update your proto file.  Sure, in a compiled language
like C++ or Java you could build this step into your build rules,
but python doesn't normally _have_ build rules - when you update
something, you expect it to be reflected the next time you run your
script.

Google's protobuffers break that: unless you re-compile your python
proto output, any changes to your proto file will _not_ be reflected.

As this is very annoying, this module aims to fix that by providing
a special import hook that invokes a bit of special import magic
when importing any file that ends in '_pb' - the importer will look
for the source .proto file and then compare their last modified times.
If the _pb.py file doesn't exist, or it was last modified less recently
than the .proto file, this module invokes the proto compiler to
regenerate the code and THEN imports it.
"""

import sys
import os
import subprocess

from cobra.steve.util import cobrastuff


PYPB_SUFFIX = '_pb2'
PROTO_SUFFIX = '.proto'


class ProtocolBufferMagicImportHook(object):
  def find_module(self, module_name, package_paths):
    if not module_name.endswith(PYPB_SUFFIX):
      return
    module_base = module_name.split('.')[-1][:-len(PYPB_SUFFIX)]
    # TODO(fedele): is just blindly taking the first package_path here
    # the correct thing to do?
    python_file = os.path.join(package_paths[0], module_base + PYPB_SUFFIX + ".py")
    proto_file = os.path.join(package_paths[0], module_base + PROTO_SUFFIX)
    if not os.path.exists(python_file):
      if os.path.exists(proto_file):
        CompileProtocolBuffer(proto_file)
      else:
        # If we can't even find the corresponding .proto file, give
        # up and hope the default mechanism knows what its doing.
        return
    else:
      proto_time = os.stat(proto_file).st_mtime
      python_time = os.stat(python_file).st_mtime
      if proto_time > python_time:
        CompileProtocolBuffer(proto_file)
    return

  def load_module(self, module_name):
    # This _shouldn't_ ever need be called.
    raise NotImplementedError
    pass


def CompileProtocolBuffer(proto_file):
  "Compile the protobuffer at the specified path."
  assert proto_file.endswith(PROTO_SUFFIX)
  python_file = proto_file[:-6] + PYPB_SUFFIX + ".py"
  cobra_basedir = cobrastuff.ExtractCobraDir(proto_file)
  outdir = os.path.dirname(proto_file)
  cmd = "protoc -I=%s --python_out=%s %s" % (cobra_basedir, cobra_basedir, proto_file)
  subprocess.check_call(cmd.split())


if False:
  def GetCobraBasedir(proto_filepath):
    "Given a path to a protofile, try to find the cobra root directory."
    COBRA = 'cobra'
    n = proto_filepath.find(COBRA) + len(COBRA) + 1
    basedir = proto_filepath[:n]
    print proto_filepath
    print basedir
    assert os.path.exists(basedir) and os.path.isdir(basedir), "basedir '%s' (inferred from '%s') is not a valid directory" % (basedir, proto_filepath)
    return basedir


sys.meta_path.append(ProtocolBufferMagicImportHook())
