class Media
  include DataMapper::Resource
  
  property :id, Serial
  property :type, Discriminator
  
  belongs_to :product
end

class Photo < Media
  property :url, String
  property :width, Integer
  property :height, Integer
end

class Video < Media
  property :embed_code, String
  property :width, Integer
  property :height, Integer
end