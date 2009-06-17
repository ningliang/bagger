class Tag
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String, :length => 1..500, :lazy => false
  property :type, String, :length => 1..500, :lazy => false
  property :meta, Json, :lazy => false
  
  has n, :products, :through => Resource
  has n, :tag_questions, :through => Resource
  
  def to_json
    { 
      :id => self.id, 
      :name => self.name, 
      :type => self.type, 
      :meta => self.meta 
    }.to_json
  end
end