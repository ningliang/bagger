class Photo 
  include DataMapper::Resource
  
  property :id, Serial
  
  property :uri, String, :lazy => false
  property :url, String, :length => 1..500, :lazy => false
  property :width, Integer, :lazy => false
  property :height, Integer, :lazy => false
  
  belongs_to :product
  
  def to_json
    { :id => self.id, :url => self.url, :width => self.width, :height => self.height }.to_json
  end
end