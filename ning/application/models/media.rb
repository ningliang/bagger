class Media
  include DataMapper::Resource
  
  property :id, Serial
  property :type, Discriminator
end

class Photo < Media
  property :url, String
  property :width, Integer
  property :height, Integer
end