function QuestionService() {
	var that = this;
	var path = "/questions"
	var proxy = RequestProxy.getInstance();
	
	this.generate = function(successHandler, errorHandler) { proxy.post(path, null, successHandler, errorHandler); }
	this.answer = function(data, successHandler, errorHandler) { proxy.put(path, data, successHandler); }
}
makeSingleton(QuestionService);