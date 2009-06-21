require 'rubygems'
require 'sinatra'
require 'json/pure'
require 'haml'
require 'cgi'
require 'db'
require 'xmlrpc/client'

# Backend services
require 'services/question_service'

# Constants
PHOTO_WIDTH = 163
PHOTO_HEIGHT = 203

# Setup
set :sessions, true
set :root, File.dirname(__FILE__)

mime :json, "application/json"
#mime :json, "text/json"

# Helpers
helpers do
  def json_response(code, retval)
    content_type :json
    status code
    retval.to_json if retval
  end
end

# Index
get "/" do 
  haml :'dashboards/index'
end

# Product summary
get "/products/:id" do |id|
  @product = Product.get(id);
  raise NotFound unless @product
  haml :'products/full'
end

# Recommend dashboard
get "/recommend" do 
  haml :'dashboards/recommend'
end

# Question Service Proxy

# Get a question
get "/questions/:id" do |id|
  question = QuestionService.get(id)
  raise ServerError unless question
  puts question
  json_response(200, question)
end

# Generate a question (JSON)
post "/questions" do
  question = QuestionService.generate(0)
  raise ServerError unless question
  puts question
  json_response(200, question)
end

# Answer a question
put "/questions/:id" do |id|
  result = QuestionService.answer(id, 0)
  puts result
  json_response(200, result)
end

# Add events
post "/questions/:id/events" do |id|
  # TODO STUB
end
