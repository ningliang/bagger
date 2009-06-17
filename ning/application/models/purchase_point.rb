class PurchasePoint
  include DataMapper::Resource
  
  property :id, Serial
  property :color, String, :lazy => false
  property :source, String, :length => 1..500, :lazy => false
  property :price, String, :lazy => false
  
  belongs_to :product
end