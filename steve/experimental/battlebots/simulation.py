#
# Things still to do:
#   - render a gun, treads, etc with the tank (explore expanding how shapes are rendered, and make multishapes)
#   - fire!  render missiles, have them move
#   - perform collision detection (e.g. using shapely) - with walls, with misiles, and trigger "events"
#   - ad a red patch that, when entered (collided with), wins
#   - create a framework for the simulation to simulate "battles" or "levels" - and once complete, things reset
#   - produce a surrounding object detector and render it to the screen - have it detect walls, enemies, have a range, etc
#   - shields, different weapons, different chases (speed, power, etc)
#   - powerups, traps
#   - enemies!  aka multiple robots
#   - run simulations with only robots, see which win - try to evolve neural nets etc that can produce output given inputs (sensors)
#   - add an option to produce swf movie files of battles
#   - make it easy to "human program" robots - also powerups, weapons, chases, detectors, missiles (e.g. a 'scripting language' for these things)
#   - online webservice to make it easy to program, upload, and fight robots


from cobra.steve.util.prelude import *

import pygame
import numpy
from shapely.geometry import *






class ShapeFactory(object):
  class Shape(tuple):
    """
    The ShapeFactory basically maintains one long list of points as a numpy
    array.  Shapes then become slices into this array - ShapeFactory.Shape
    is basically a glorified slice object.
    
    For simplicity, 
    """
    pass

  def __init__(self, shape_loader):
    """
    shape_loader is a callable that, given a string name, returns a sequence
    of coordinates that correspond to the shape.
    """
    self.point_list = []
    self.point_array = None    
    self.cached_shapes = {}
    self.shape_loader = shape_loader
    
  def LoadShape(self, shape_name):
    """
    Given a shape name like "level" or "robot", return a Shape
    object for that shape.
    """
    try:
      return self.cached_shapes[shape_name]
    except KeyError:
      start = len(self.point_list)
      self.point_list.extend(self.shape_loader(shape_name))
      end = len(self.point_list)
      shape = self.cached_shapes[shape_name] = self.Shape((start, end))
      self.point_array = None   # Our point array
      return shape
      
  def PointArray(self):
    """
    Return the complete list of shapes as a numpy array.
    Note that although
    """    
    if self.point_array is not None:
      return self.point_array
    self.point_array = numpy.ones((len(self.point_list), 3))
    self.point_array[:,0:2] = self.point_list
    self.point_array = self.point_array.transpose()    
    return self.point_array
    
  def GetShapeCoords(self, shape):
    """
    Return the list of a given shape's coords as a numpy array.
    """   
    start, end = shape
    return self.PointArray()[start:end]
    
  

class DefaultShapeLoader(object):
  def __call__(self, shape_name):
    if shape_name == 'level':
      # Right now our level is just a simple rectangle.
      return [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    elif shape_name == 'robot':
      # A robot is just a rectangle.  There are 10 robots to a side.
      return [(-0.1, -0.1), (0.1, -0.1), (0.1, 0.1), (-0.1, 0.1), (-0.1, -0.1)]
    
    


class GameState(object):
  robot_speed = 1 / 1000.0
  robot_turn_speed = 2 * 3.14159 / 2.0 / 1000.0
  
  
  def __init__(self, screen_shape):
    self.shape_factory = ShapeFactory(DefaultShapeLoader())    
    w, h = screen_shape
    self.world_transform = numpy.array([[ 0.5 * w,       0.0, 0.5 * w],
                                        [     0.0,  -0.5 * h, 0.5 * h],
                                        [     0.0,       0.0,     1.0]]) 
    self.level = self.shape_factory.LoadShape('level')    
    self.robot = self.shape_factory.LoadShape('robot')
    self.robot_position_transform = numpy.array([[ 1.0, 0, 0],
                                                 [ 0, 1.0, 0],
                                                 [ 0, 0, 1.0]])
    
    
  def DrawWorld(self, screen):    
    pts = self.shape_factory.PointArray()    
    screen.fill((255,255,255))
    def DrawShape(shape, color, xform=None):
      n, m = shape
      if xform is not None:
        xform = numpy.dot(self.world_transform, xform)
      else:
        xform = self.world_transform
      screen_pts = numpy.dot(xform, pts[:, n:m]).transpose()[:,:-1]      
      pygame.draw.polygon(screen, color, screen_pts, 1)
    DrawShape(self.level, (0,255,255))
    DrawShape(self.robot, (0,0,0), xform=self.robot_position_transform)
    
  def UpdateWorld(self, tick_time):
    keys_down = pygame.key.get_pressed()
    
    if keys_down[pygame.K_DOWN]:
      # Move us backwards - however, it needs to be
      # along our primary axis, e.g. our current one.
      # That would be the first axis.      
      self.robot_position_transform[:,2] -= (tick_time * self.robot_speed) * self.robot_position_transform[:,0]       
    if keys_down[pygame.K_UP]:
      # Move us forwards.
      self.robot_position_transform[:,2] += (tick_time * self.robot_speed) * self.robot_position_transform[:,0]
      
    if keys_down[pygame.K_RIGHT]:
      # Turn us right.
      t = tick_time * self.robot_turn_speed
      rot = numpy.array([[ math.cos(t), math.sin(t)],
                         [-math.sin(t), math.cos(t)]])
      foo = self.robot_position_transform[:,:-1]           
      self.robot_position_transform[:,:-1] = numpy.dot(foo, rot)
    if keys_down[pygame.K_LEFT]:
      # Turn us left.
      t = -tick_time * self.robot_turn_speed
      rot = numpy.array([[ math.cos(t), math.sin(t)],
                         [-math.sin(t), math.cos(t)]])
      foo = self.robot_position_transform[:,:-1]      
      self.robot_position_transform[:,:-1] = numpy.dot(foo, rot)
      
    if keys_down[pygame.K_SPACE]:
      # Fire!
      pass
      


def main():
  pygame.init()
  screen_shape = (300, 300)
  state = GameState(screen_shape)
  screen = pygame.display.set_mode(screen_shape)

  clock = pygame.time.Clock()
  done = False
  fps = 30
  while not done:
    tick_time = clock.tick(fps)
    state.UpdateWorld(tick_time)
    state.DrawWorld(screen)    
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        done = True
    pygame.display.update()
  
  
if __name__ == '__main__':
  main()