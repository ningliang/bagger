class Question
  include DataMapper::Resource
  
  property :id, Serial
  property :choice, Integer
  property :type, Discriminator
  property :created_at, DateTime
    
  belongs_to :user
  
  def to_hash
    {:id => self.id, :choice => self.choice, :type => self.type, :created_at => self.created_at }
  end
end

class TagQuestion < Question
  has n, :tags, :through => Resource
  def to_json
    self.to_hash.merge(:tags => self.tags.all.to_a).to_json 
  end
end

class ProductQuestion < Question
  has n, :products, :through => Resource
  def to_json
    self.to_hash.merge(:products => self.products.all.to_a).to_json 
  end
end