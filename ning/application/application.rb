require 'rubygems'
require 'sinatra'
require 'data_mapper'
require 'json'
require 'haml'

require 'models/tag'
require 'models/media'
require 'models/product'
require 'models/purchase_point'
require 'models/review'
require 'models/question'
require 'models/user'

# Setup
DataMapper.setup(:default, {
  :adapter => 'sqlite3',
  :database => 'development.db'
})
DataMapper::Logger.new(STDOUT, :debug)

set :sessions, true
set :root, File.dirname(__FILE__)

# ROUTES
get "/" do 
  haml :'dashboards/index'
end

get "/products/:id" do |id|
  @product = Product.get(id);
  haml :'products/summary'
end

# Recommend dashboard
get "/recommend" do 
  haml :'dashboards/recommend'
end

# Get a question (JSON)
get "/questions/next" do
  content_type 'text/json'
  "Next question"
end

# Answer a question (JSON)
put "/questions/:id" do |id|
  content_type 'text/json'
  "You answered question #{id}"
end