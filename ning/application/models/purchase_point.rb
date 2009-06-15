class PurchasePoint
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String
  property :color, String
  property :source, String
  property :price, String
  
  belongs_to :product
end