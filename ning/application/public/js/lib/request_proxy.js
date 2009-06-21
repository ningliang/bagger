function RequestProxy() {
	function request(path, method, data, successHandler, errorHandler) {
		data = data || {}
		if (method == PUT || method == DELETE) {
			data['_method'] = method;
			method = POST;
		}
		
		// Sinatra does not play nice with JSON PUT / DELETE - don't nest!
		
		// AJAX parameters
		var options = {
			url: BASE_URL + path,
			dataType: "json",
			type: method,
			data: data,
			cache: false,
			success: function(response) { if (successHandler) successHandler(response); },
			error: function(request, status, error) { if (errorHandler) errorHandler(request.status, request.responseText); }
		}
		
		$.ajax(options);
	}
	
	this.get = function(path, successHandler, errorHandler) { request(path, GET, null, successHandler, errorHandler); }
	this.post = function(path, data, successHandler, errorHandler) { request(path, POST, data, successHandler, errorHandler); }
	this.put = function(path, data, successHandler, errorHandler) { request(path, PUT, data, successHandler, errorHandler); }
	this.destroy = function(path, data, successHandler, errorHandler) { request(path, DELETE, data, successHandler, errorHandler); }
}
makeSingleton(RequestProxy);