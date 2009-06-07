require 'rubygems'
require 'sinatra'
require 'data_mapper'
require 'json'
require 'haml'
require 'db'

# Setup
set :sessions, true
set :root, File.dirname(__FILE__)

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
  content_type 'text/json'  
  # TODO call over to Steve's service, giving all data  
  # For now just create an unanswered tag or product question
  question = nil
  n = rand(2)
  if (n == 0)
    question = TagQuestion.create
    count = Tag.all.count
    4.times do 
      n = rand(count) + 1
      question.tags << Tag.get(n)
    end
  else
    question = ProductQuestion.create
    count = Product.all.count
    2.times do
      n = rand(count) + 1
      question.products << Product.get(n)
    end
  end
  question.to_json
end

# Answer a question
put "/questions/:id" do |id|
  content_type 'text/json'  
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