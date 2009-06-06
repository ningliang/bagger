class Review
  include DataMapper::Resource
  
  property :id, Serial
  property :source, String
  property :content, String
  property :rating, String
  
  belongs_to :product
end