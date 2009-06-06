class Product
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String
  
  has n, :medias
  has n, :purchase_points
  has n, :reviews
  has n, :tags, :through => Resource

  has n, :product_questions, :through => Resource
end