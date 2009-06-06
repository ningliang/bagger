class Tag
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String
  property :type, String
  
  has n, :products, :through => Resource
  has n, :tag_questions, :through => Resource
end