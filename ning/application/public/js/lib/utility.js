// Make any class a singleton
function makeSingleton(klass) {
	klass.instance = null;
	klass.getInstance = function() {
		if (!klass.instance) klass.instance = new klass();
		return klass.instance;
	}
}

// Convenient array remove
Array.prototype.remove = function(obj) {
	for (var i in this) {
		if (this[i] == obj) {
			this.splice(i, 1);
			i--;
		}
	}
}

// Convenience function for enabling the global modal window
$.fn.setModal = function() {
	// Modal is hidden by default
	var node = $(this).hide();

	// Functions
	node.showMessage = function(message) { console.log("modal: " + message); }
	node.showElement = function(element) { console.log(element); }
	
	// Chain the jQuery object
	return node;
}