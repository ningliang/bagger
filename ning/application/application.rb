require 'rubygems'
require 'sinatra'
require 'data_mapper'
require 'haml'

require 'models/label'
require 'models/media'
require 'models/product'
require 'models/purchase_point'
require 'models/review'
require 'models/selection'
require 'models/user'

# Setup the DB

DataMapper.setup(:default, {
  :adapter => 'sqlite3',
  :database => 'development.rb'
})

# TODO process Steve's data here

DataMapper.auto_migrate!


# Responses
get '/' do
  "INDEX"
end




#/ - index
#/products/:id/select
#/selections/:id/select
#/products/search?{params}



