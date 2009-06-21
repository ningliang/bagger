class QuestionService
  def self.get(id)
    server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    result = server.call("GetQuestion", id)
    result
  end
  
  def self.generate(user_id)
    server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    result = server.call("GetNewQuestion", user_id)
    result
  end
  
  def self.answer(question_id, choice_id) 
    server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    result = server.call("SetQuestionAnswer")
    result
  end
  
  def self.add_events(question_id, events)
    server = XMLRPC::Client.new2("http://67.23.10.86:1337/RPC2/")
    result = server.call("AddQuestionEvents")
    result
  end
end