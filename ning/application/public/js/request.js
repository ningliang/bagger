// Handles only JSON requests
function RequestProxy() {
	// For convenience - should never be accessed outside of this class
  var	GET = 'GET';
	var POST = 'POST';
	var PUT = 'PUT';
	var DELETE = 'DELETE';
	
	// General request method
	function request(path, method, data, successHandler, errorHandler) {
		// Pre process data
		var requestData = {	_method: method, data: data || {}	};
		if (method == PUT || method == DELETE) method = POST;
		
		// Set options
		var options = {
			url: BASE_URL + path,
			dataType: "json",
			data: requestData,
			cache: false,
			success: function(response) { if (successHandler) successHandler(response); },
			error: function(request, status, error) { if (errorHandler) errorHandler(request.status, request.responseText)}
		}
		
		// Run the call
		$.ajax(options);
	}
	
	// Methods
	this.get = function(path, successHandler, errorHandler) { request(path, GET, null, successHandler, errorHandler); }
	this.post = function(path, data, successHandler, errorHandler) { request(path, POST, data, successHandler, errorHandler); }
	this.put = function(path, data, successHandler, errorHandler) { request(path, PUT, data, successHandler, errorHandler); }
	this.destroy = function(path, data, successHandler, errorHandler) { request(path, DELETE, data, successHandler, errorHandler); }
}
makeSingleton(RequestProxy);