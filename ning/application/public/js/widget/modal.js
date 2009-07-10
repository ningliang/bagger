function Modal() {
	var self = this;
	var node = $("<div/>").addClass("modal").appendTo($("body"));
	node.hide().jqm();
	
	this.showMessage = function(message) {
		node.empty().append($("<div/>").addClass("message").html(message));
		self.showModal(
			function(hash) { hash.w.css({ opacity: 0.88}).show(); },
			function(hash) { hash.w.fadeOut("1000", function() { hash.o.remove(); }); }
		);
	}
	
	this.showElement = function(element, onShow, onHide) {
		node.empty().append(element);
		self.showModal(onShow, onHide);
	}
	
	this.showModal = function(onShow, onHide) {
		node.jqm({ onShow: onShow, onHide: onHide });
		node.jqmShow();
	}
}