class PurchasePoint
  include DataMapper::Resource
  
  property :id, Serial
  property :price, Float
end

class StorePurchasePoint < PurchasePoint
  
end

class WebsitePurchasePoint < PurchasePoint
  property :url, String
end