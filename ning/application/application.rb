# Dependencies
require 'rubygems'
require 'sinatra'
require 'json/pure'
require 'haml'
require 'xmlrpc/client'
require 'db'

# Services
require 'services/question_service'

# Settings
set :sessions, true
set :root, File.dirname(__FILE__)
mime :json, "application/json"

# Helper
helpers do
  def json_response(code, retval)
    content_type :json
    status code
    retval.to_json if retval
  end
end

# Session, JSON handling
before do
  # TODO generate a user 
  session[:user_id] ||= User.create.id
  params[:data] = JSON.parse(params[:data]) unless params[:data].nil?
end

# Index
get "/" do 
  haml :index 
end

get "/recommendation" do 
  haml :recommendation 
end

# Question resource 

get "/questions/:id" do |id|
  question = QuestionService.get(id)
  raise ServerError unless question
  json_response(200, question)
end

post "/questions" do
  question = QuestionService.generate(session[:user_id])
  raise ServerError unless question
  json_response(200, question)
end

put "/questions/:id" do |id|
  result = QuestionService.answer(id, params[:data][:answer])
  raise ServerError unless result[:success]
  json_response(200, result)
end