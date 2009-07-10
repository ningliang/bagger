function RequestProxy() {
	var GET = "GET";
	var POST = "POST";
	var PUT = "PUT";
	var DELETE = "DELETE";
	
	function request(path, method, data, successHandler, errorHandler) {
		var requestData = { _method: method, data: data || {}};
		requestData["data"] = JSON.stringify(requestData["data"]);
		if (method == PUT || method == DELETE) method = POST;
		
	
		var options = {
			url: BASE_URL + path,
			type: method,
			dataType: "json",
			data: requestData,
			cache: false,
			success: function(response) { if (successHandler) successHandler(response); },
			error: function(request, status, error) { if (errorHandler) errorHandler(request.status, request.responseText)}
		};
		$.ajax(options);
	}
	
	this.get = function(path, successHandler, errorHandler) { request(path, GET, null, successHandler, errorHandler); }
	this.post = function(path, data, successHandler, errorHandler) { request(path, POST, data, successHandler, errorHandler); }
	this.put = function(path, data, successHandler, errorHandler) { request(path, PUT, data, successHandler, errorHandler); }
	this.destroy = function(path, data, successHandler, errorHandler) { request(path, DELETE, data, successHandler, errorHandler); }
}
makeSingleton(RequestProxy);