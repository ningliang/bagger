class PurchasePoint
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String
  property :address, String
  property :price, Float
  
  belongs_to :product
end