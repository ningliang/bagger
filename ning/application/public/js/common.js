// HTTP related constants
BASE_URL = window.location.protocol + "//" + window.location.host;
OK = 200;
UNAUTHORIZED = 401;
FORBIDDEN = 403;
NOT_FOUND = 404;
SERVER_ERROR = 500;

// Event related constants
SELECTION = 0;
CONFIRMATION = 1;
PHOTO_VIEW = 2;
PHOTO_CLOSE = 3;


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
	return $.extend(data, 
		type: type,
		timestamp: new Date().getTime()
	);
}