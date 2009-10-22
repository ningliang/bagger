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


def Square(scale):
  """
  Returns a list of coordinates representing a square centered
  at (0, 0) with sides of length 2 * scale.
  """
  return [(-scale, -scale), (scale, -scale), (scale, scale), (-scale, scale), (-scale, -scale)]


def RandomShape(radius, num_vertices):
  angle_step = 2 * math.pi / num_vertices
  theta = random.gauss(0, angle_step)
  points = []
  for n in xrange(num_vertices):
    theta += angle_step + random.gauss(0, 0.1 * angle_step)
    while True:
      r = random.gammavariate(alpha=0.5*radius, beta=1.0)
      if 0.3 * radius < r < radius:
        break
    print theta, r
    pt = (r * math.cos(theta), r * math.sin(theta))
    points.append(pt)
  points.append(points[0])
  return points


class DefaultShapeLoader(object):
  def __call__(self, shape_name):
    if shape_name == 'level':
      shape = RandomShape(radius=0.9, num_vertices=7)
      print shape
      return shape
    elif shape_name == 'world':
      return Square(1.0)
    elif shape_name == 'robot':
      return Square(0.05)
    elif shape_name == 'target':
      return RandomShape(radius=0.3, num_vertices=random.randint(3, 5))


def AffineTransform(position, angle):
  c = math.cos(angle)
  s = math.sin(angle)
  x, y = position
  xform = numpy.array([[ c, s, x],
                       [-s, c, y],
                       [ 0, 0, 1]])
  return xform


class PolygonDrawer(object):
  def __init__(self, color=(0, 0, 0), width=0):
    self.color = color
    self.width = width

  def __call__(self, screen, pts):
    pygame.draw.polygon(screen, self.color, pts, self.width)


class GameState(object):
  robot_speed = 1 / 1000.0
  robot_turn_speed = 2 * 3.14159 / 2.0 / 1000.0

  normal_level_color = (0, 255, 255)
  collided_level_color = (255, 0, 0)

  flip_every_ms = 1000

  def __init__(self, screen_shape, screen_offset):
    self.shape_factory = ShapeFactory(DefaultShapeLoader())
    self.level_color = self.normal_level_color
    w, h = screen_shape
    x, y = screen_offset
    self.world_transform = numpy.array([[ 0.5 * w,       0.0,  0.5 * w + x],
                                        [     0.0,  -0.5 * h,  0.5 * h + y],
                                        [     0.0,       0.0,          1.0]])
    self.objects = []
    self._cached_object_pts = []
    self.time_since_color_flip = 0
    self.AddObject('world', width=1, color=(0, 0, 0))
    self.AddObject('level', color=(0, 255, 255))
    self.AddObject('robot')
    self.AddObject('target', color=(255, 0, 0))
    self.objects[3][1]

  def GetRobotXform(self):
    "Return the robot position transform matrix"
    return self.objects[2][1]

  def SetLevelColor(self, new_color):
    self.level_color = new_color
    self.objects[1][2].color = new_color  # Object 1 is the level, and element 2 is the drawer.

  def AddObject(self, shape_name, position=(0, 0), angle=0, **kwargs):
    obj = self.shape_factory.LoadShape(shape_name)
    xform = AffineTransform(position, angle)
    drawer = PolygonDrawer(**kwargs)
    self.objects.append((obj, xform, drawer))
    return xform

  def ScreenPoints(self, obj_tuple, pts=None):
    pts = self.shape_factory.PointArray()
    (n, m), xform, _ = obj_tuple
    return numpy.dot(numpy.dot(self.world_transform, xform), pts[:, n:m]).transpose()[:, :-1]

  def WorldPoints(self, obj_tuple, pts=None):
    pts = self.shape_factory.PointArray()
    (n, m), xform, _ = obj_tuple
    return numpy.dot(xform, pts[:, n:m]).transpose()[:, :-1]

  def DrawWorld(self, screen):
    pts = self.shape_factory.PointArray()
    screen.fill((255,255,255))   # The window background is white
    for obj in self.objects:
      screen_pts = self.ScreenPoints(obj)
      obj[2](screen, screen_pts)

  def FlipLevelColor(self):
    if self.level_color == self.normal_level_color:
      self.SetLevelColor(self.collided_level_color)
    else:
      self.SetLevelColor(self.normal_level_color)

  def UpdateWorld(self, tick_time):
    self.time_since_color_flip += tick_time
    if self.time_since_color_flip > self.flip_every_ms:
      self.time_since_color_flip -= self.flip_every_ms

    keys_down = pygame.key.get_pressed()
    robot_xform = self.GetRobotXform()

    old_robot_xform = numpy.copy(robot_xform)

    if keys_down[pygame.K_DOWN]:
      # Move us backwards - however, it needs to be
      # along our primary axis, e.g. our current one.
      # That would be the first axis.
      robot_xform[:,2] -= (tick_time * self.robot_speed) * robot_xform[:,0]
    if keys_down[pygame.K_UP]:
      # Move us forwards.
      robot_xform[:,2] += (tick_time * self.robot_speed) * robot_xform[:,0]

    if keys_down[pygame.K_RIGHT]:
      # Turn us right.
      t = tick_time * self.robot_turn_speed
      rot = numpy.array([[ math.cos(t), math.sin(t)],
                         [-math.sin(t), math.cos(t)]])
      foo = robot_xform[:,:-1]
      robot_xform[:,:-1] = numpy.dot(foo, rot)
    if keys_down[pygame.K_LEFT]:
      # Turn us left.
      t = -tick_time * self.robot_turn_speed
      rot = numpy.array([[ math.cos(t), math.sin(t)],
                         [-math.sin(t), math.cos(t)]])
      foo = robot_xform[:,:-1]
      robot_xform[:,:-1] = numpy.dot(foo, rot)

    if keys_down[pygame.K_SPACE]:
      # Fire!
      pass

    if self.DetectCollisions():
      # self.SetLevelColor(self.collided_level_color)
      robot_xform[:] = old_robot_xform
      # TODO(fedele): figure out the exact _time_ the robot collided
      # with the scenery.  To do this, we calculate the robot's position as:
      # as [[  cos(t * vr), sin(t * vr), x + vx * t],
      #     [ -sin(t * vr), cos(t * vr), y + vy * t],
      #     [          0.0,        0.0,         1.0]]
      # and we wish to determine the first such t that will cause intersection
      # with the offending object, which 

  def DetectCollisions(self):
    shapes = []
    for n, obj in enumerate(self.objects):
      world_pts = self.WorldPoints(obj)
      # Why does the LineString here not work?
      shape = LineString([(x, y) for x, y in world_pts])
      shapes.append(shape)
    # We only need to check for collisions of the robot with the level.
    return shapes[2].crosses(shapes[1])




def main():
  if False:
    world_pts = numpy.array(Square(0.9))
    print "WORLD POINTS"
    print world_pts
    print "AS LINESTRING"
    shape = asLineString(world_pts)
    print list(shape.coords)
    return

  
  pygame.init()
  window_shape = (800, 620)       # The total size of the game window
  game_screen_shape = (600, 600)  # The size of the actual battlefield
  game_screen_offset = (10, 10)
  state = GameState(game_screen_shape, game_screen_offset)

  screen = pygame.display.set_mode(window_shape)

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
