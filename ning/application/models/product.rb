class Product
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String, :length => 1..500, :lazy => false
  property :description, String, :length => 1..2000, :lazy => false
  
  has n, :photos
  has n, :purchase_points
  has n, :reviews
  has n, :tags, :through => Resource
  
  def to_json
    {
      :id => self.id, 
      :name => self.name, 
      :description => self.description, 
      :photos => self.photos.all.to_a
    }.to_json
  end
end