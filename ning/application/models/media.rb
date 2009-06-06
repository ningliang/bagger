class Media
  include DataMapper::Resource
  
  property :id, Serial
end

class Photo < Media
  property :url, String
  property :width, Integer
  property :height, Integer
end