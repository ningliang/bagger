require 'rubygems'
require 'data_mapper'
Dir.glob(File.join(File.dirname(__FILE__) + "/models/*.rb")).each do |f| require f end

DataMapper.setup(:default, {
  :adapter => 'mysql',
  :host => 'localhost',
  :username => 'root',
  :database => 'bagger_development'
})
DataObjects::Mysql.logger = DataObjects::Logger.new(STDOUT, 0)