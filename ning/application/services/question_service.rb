class QuestionService
  def self.get(id)
    questions = [
      { :id => id, :statement => "What color do you like?", :choices => ["red", "blue", "green"], :type => "MULTI" },
      { :id => id, :statement => "What photo do you like?", :choices => [
        { :url => "http://1.bp.blogspot.com/_r7ZVb5hINHY/R0zqkactjPI/AAAAAAAAAIk/QRwxzXCfuTM/s320/lolcats2.jpg" }, 
        { :url => "http://1.bp.blogspot.com/_r7ZVb5hINHY/R0zqkactjPI/AAAAAAAAAIk/QRwxzXCfuTM/s320/lolcats2.jpg" }
      ], :type => "MULTI" },
      { :id => id, :statement => "Tell us your favorite thing to do", :type => "INPUT" }
    ]
    questions[rand(3)]
  end
  
  def self.generate(user_id)
    questions = [
      { :id => 1, :statement => "What color do you like?", :choices => ["red", "blue", "green"], :type => "MULTI" },
      { :id => 2, :statement => "What photo do you like?", :choices => [
        { :url => "http://1.bp.blogspot.com/_r7ZVb5hINHY/R0zqkactjPI/AAAAAAAAAIk/QRwxzXCfuTM/s320/lolcats2.jpg" }, 
        { :url => "http://1.bp.blogspot.com/_r7ZVb5hINHY/R0zqkactjPI/AAAAAAAAAIk/QRwxzXCfuTM/s320/lolcats2.jpg" }
      ], :type => "MULTI" },
      { :id => 3, :statement => "Tell us your favorite thing to do", :type => "INPUT" }
    ]    
    questions[rand(3)]
  end
  
  def self.answer(question_id, choice_id)
    { :success => true }
  end
end