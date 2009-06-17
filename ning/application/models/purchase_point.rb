class PurchasePoint
  include DataMapper::Resource
  
  property :id, Serial
  property :color, String
  property :source, String, :length => 1..500
  property :price, String
  
  belongs_to :product
end