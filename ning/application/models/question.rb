class Question
  include DataMapper::Resource
  
  property :id, Serial
  property :choice, Integer
  property :type, Discriminator
  
  belongs_to :user
end

class TagQuestion < Question
  has n, :tags, :through => Resource
  def to_json; { :id => self.id, :type => self.type, :tags => self.tags.map do |t| t.to_json end }.to_json end
end

class ProductQuestion < Question
  has n, :products, :through => Resource
  def to_json; { :id => self.id, :type => self.type, :products => self.products.map do |p| p.to_json end }.to_json end
end