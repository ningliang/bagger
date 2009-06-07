from cobra.steve.util.prelude import *

flags.DefineString("foobar", "baz", "what the foobar is")

def main(argv):
  print FLAGS.foobar


if __name__ == '__main__':
  app.run()
