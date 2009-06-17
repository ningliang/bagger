BASE_URL = window.location.protocol + "//" + window.location.host;

GET = 'get';
POST = 'post';
PUT = 'put';
DELETE = 'delete';

OK = 200;
UNAUTHORIZED = 401;
FORBIDDEN = 403;
NOT_FOUND = 404;
SERVER_ERROR = 500;

function RequestProxy() {
	function request(path, method, data, successHandler, errorHandler) {
		data = data || {};
		data['_method'] = method;
		if (method == PUT || method == DELETE) method = POST;
		
		// AJAX parameters
		var options = {
			url: BASE_URL + path,
			contentType: 'application/json',
			dataType: 'json',
			type: method,
			data: JSON.stringify(data),
			cache: false,
			success: function(response) { if (successHandler) successHandler(response); },
			error: function(request, status, error) { if (errorHandler) errorHandler(request.status, JSON.parse(request.responseText)); }
		}
		
		$.ajax(options);
	}
	
	this.get = function(path, successHandler, errorHandler) { request(path, GET, null, successHandler, errorHandler); }
	this.post = function(path, data, successHandler, errorHandler) { request(path, POST, data, successHandler, errorHandler); }
	this.put = function(path, data, successHandler, errorHandler) { request(path, PUT, data, successHandler, errorHandler); }
	this.destroy = function(path, data, successHandler, errorHandler) { request(path, DELETE, data, successHandler, errorHandler); }
}
makeSingleton(RequestProxy);