function QuestionService() {
	var that = this;
	var path = "/questions";
	var proxy = RequestProxy.getInstance();
	
	this.create = function(successHandler, errorHandler) { proxy.post(path, null, successHandler, errorHandler); }
	this.update = function(data, successHandler, errorHandler) { proxy.put(path + "/" + data.id, data, successHandler, errorHandler); }
}
makeSingleton(QuestionService);

function EventService() {
	var that = this;
	var path = "/events";
	var proxy = RequestProxy.getInstance();
	var queue = [];
	
	// Add an event to the queue
	this.add = function(event) { queue.add(event); }
	
	// Flush
	this.flush = function() {
		if (queue.length > 0) {
			console.log("flushing " + queue.length + " events.");
			proxy.post(path, queue, 
				function(response) { console.log(response);	},
				function(status, message) { console.log(status + ": " + message); }
			);
		} else {
			console.log("nothing to flush.");
		}
	}
	
	// Start up the flush timer
	setInterval("this.flush()", 5000);
}
makeSingleton(EventService);