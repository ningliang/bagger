class Photo 
  include DataMapper::Resource
  
  property :id, Serial
  
  property :uri, String
  property :url, String, :length => 1..500
  property :width, Integer
  property :height, Integer
  
  belongs_to :product
end