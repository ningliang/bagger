class Tag
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String
  property :type, String
  property :meta, Json
  
  has n, :products, :through => Resource
  has n, :tag_questions, :through => Resource
end