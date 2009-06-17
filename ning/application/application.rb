require 'rubygems'
require 'sinatra'
require 'json/pure'
require 'haml'
require 'db'

# Setup
set :sessions, true
set :root, File.dirname(__FILE__)

mime :json, "application/json"
#mime :json, "text/json"

# Before filters
before do
  # User detection (strategies)
  # 1) User set in the cookie?
  # 2) Lookup via IP
  # 3) Create new user and set in cookie
  # End: @user is set
end

# Helpers
helpers do
  def json_response(code, retval)
    status code
    retval.to_json
  end
end

# ROUTES
get "/" do 
  haml :'dashboards/index'
end

get "/products/:id" do |id|
  @product = Product.get(id);
  raise NotFound unless @product
  haml :'products/full'
end

# Recommend dashboard
get "/recommend" do 
  haml :'dashboards/recommend'
end

# Generate a question (JSON)
post "/questions" do
  content_type :json
  
  # Create a tag question
  question = nil
  if rand(2) == 0
    question = TagQuestion.create
    count = Tag.all.count
    4.times do 
      tag = Tag.get(rand(count))
      question.tags << Tag.get(rand(count)) 
    end
  else 
    question = ProductQuestion.create
    count = Product.all.count
    3.times do
      product = Product.get(rand(count))
      question.products << product
    end
  end
  question.save
  question.to_json
end

# Answer a question
put "/questions/:id" do |id|
  content_type :json
  question = Question.get(id)
  raise NotFound unless question
  choice, choice_id = nil, params[:choice].to_i
  case question.type
    when ProductQuestion then choice = Product.get(choice_id)
    when TagQuestion then choice = Tag.get(choice_id)
  end
  raise NotAcceptable unless choice
  question.choice = choice
  if question.save 
    json_response(200, :success => true) 
  else
    json_response (500, :errors => question.errors)
  end
end
