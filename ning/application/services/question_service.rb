class QuestionService
  def self.get(id)
    #server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    #result = server.call("GetQuestion", id)
    #result
    { :id => 1, :choice => nil, :type => "ProductQuestion", :products => [Product.get(1), Product.get(2), Product.get(3), Product.get(4)] }
  end
  
  def self.generate(user_id)
    #server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    #result = server.call("GetNewQuestion", user_id)
    #result
    { :id => 1, :choice => nil, :type => "ProductQuestion", :products => [Product.get(1), Product.get(2), Product.get(3), Product.get(4)] }
  end
  
  def self.answer(question_id, choice_id) 
    #server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    #result = server.call("SetQuestionAnswer")
    #result
    { :success => true }
  end
  
  def self.add_events(events)
    #server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    #result = server.call("AddQuestionEvents")
    #result
    { :success => true }
  end
end