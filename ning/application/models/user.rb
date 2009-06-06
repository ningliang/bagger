class User
  include DataMapper::Resource
  
  property :id, Serial
  property :ip_address, String
  property :email, String
  
  has n, :questions
end