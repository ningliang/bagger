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

# Special handling on JSON data
before do
  data = JSON.parse(params[:data]) unless params[:data].nil?
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
  json_response(200, question)
end

# Generate a question (JSON)
post "/questions" do
  # TODO user id
  puts "Generating question for user #{0}"
  question = QuestionService.generate(0)
  raise ServerError unless question
  json_response(200, question)
end

# Answer a question
put "/questions/:id" do |id|
  puts "Answering question with id #{id} and answer #{data[:choice_id]}"
  result = QuestionService.answer(id, data[:choice_id])
  json_response(200, result)
end

# Add events
post "/events" do 
  puts "Adding events of the form #{data.to_json}"
  result = QuestionService.addEvents(data)
end
