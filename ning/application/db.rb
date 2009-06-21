require 'rubygems'

# Datamapper requires
require 'data_mapper'
require 'dm-serializer'
require 'dm-timestamps'

# Models
Dir.glob(File.join(File.dirname(__FILE__) + "/models/*.rb")).each do |f| require f end

DataMapper.setup(:default, {
  :adapter => 'mysql',
  :host => 'localhost',
  :username => 'root',
  :database => 'bagger_development'
})
DataObjects::Mysql.logger = DataObjects::Logger.new(STDOUT, 0)