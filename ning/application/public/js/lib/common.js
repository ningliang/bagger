// HTTP related constants
var BASE_URL = window.location.protocol + "//" + window.location.host;
var OK = 200;
var UNAUTHORIZED = 401;
var FORBIDDEN = 403;
var NOT_FOUND = 404;
var SERVER_ERROR = 500;

// Make anything a singleton
function makeSingleton(klass) {
	klass.instance = null;
	klass.getInstance = function() {
		if (!klass.instance) klass.instance = new klass();
		return klass.instance;
	}
}

// Array removal - all instances
Array.prototype.remove = function(object) {
	for (var i in this) {
		if (this[i] == object) {
			this.splice(i, 1);
			i--;
		}
	}
}

// Convenience function for a new event
function newEvent(type, data) {
	return $.extend(data, {
		type: type,
		timestamp: new Date().getTime()	
	});
}