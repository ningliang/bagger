require 'rubygems'
require 'sinatra'
require 'data_mapper'
require 'haml'

require 'models/tag'
require 'models/media'
require 'models/product'
require 'models/purchase_point'
require 'models/review'
require 'models/question'
require 'models/user'

# Setup the DB

DataMapper.setup(:default, {
  :adapter => 'sqlite3',
  :database => 'development.db'
})

# TODO process Steve's data here

DataMapper.auto_migrate!


# Pages
# Product page
get "/products/:id" do |id|
  "Product #{id}"
end

get "/recommend" do 
  "Recommendation Dashboard"
end

# Get a question
get "/questions/next" do
  "Next question"
end

# Answer a question
put "/questions/:id" do |id|
  "You answered question #{id}"
end