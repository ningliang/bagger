class User
  include DataMapper::Resource
  
  property :id, Serial
  property :last_ip, String
  property :answer_count, Integer, :default => 0
  property :email, String, :length => 1..60
  property :password, String
end