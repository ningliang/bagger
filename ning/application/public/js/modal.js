$.fn.setModal = function() {
	var node = $(this);
	node.hide().jqm();
	
	node.showMessage = function(message) {
		node.empty().append($("<div>").addClass("message").html(message));
		node.showModal(
			function(hash) { hash.w.css({ opacity: 0.88 }).show(); },
			function(hash) { hash.w.fadeOut('1000', function() { hash.o.remove(); }); }
		}
	}
	
	node.showElement = function(element, onShow, onHide) {
		node.empty().append(element);
		node.showModal(onShow, onHide);
	}
	
	node.showModal = function(onShow, onHide) {
		node.jqm({ onShow: onShow, onHide: onHide });
		node.jqmShow();
	}
	
	return node;
}