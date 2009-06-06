require 'rubygems'
require 'data_mapper'

DataMapper.setup(:default, {
  :adapter => 'sqlite3',
  :database => 'development.db'
})
DataMapper.auto_migrate!

