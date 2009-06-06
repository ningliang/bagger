class Question
  include DataMapper::Resource
  
  property :id, Serial
  property :choice, Integer
  property :type, Discriminator
  
  belongs_to :user
end

class TagQuestion < Question
  has n, :tags, :through => Resource
end

class ProductQuestion < Question
  has n, :products, :through => Resource
end