function QuestionService() {
	var that = this;
	var path = "/questions";
	var proxy = RequestProxy.getInstance();
	
	this.create = function(successHandler, errorHandler) { proxy.post(path, null, successHandler, errorHandler); }
	this.update = function(data, successHandler, errorHandler) { proxy.put(path + "/" + data.id, data, successHandler, errorHandler); }
}
makeSingleton(QuestionService);