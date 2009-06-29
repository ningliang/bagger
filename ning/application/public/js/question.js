// Parameters
// 	question - hash containing id, choices, etc.
//  controller - reference to containing controller
function Question(question, controller) {

	var node = $("<div>").addClass("question");
	var modal = $("<div>").addClass("modal").appendTo(node).setModal();
	var self = this;
	var items = [];
	
	var selection = null;
	
	this.getNode = function() { return node; }
	
	this.setSelection = function(index) { 
		if (selection) items[index].setSelected(false);
		selection = index; 
		items[index].setSelected(true);
		// TODO delegate handling to controller (event)
	}
	
	this.confirmSelection = function() {
		if (!selection) {
			modal.showMessage("No selection yet!");
		} else {
			controller.answerQuestion(question.id, selection);
		}
	}
	
	// Build node from hash
	function build(questionHash) {
		node.empty();
		int index = 0;
		if (questionHash.type == "TagQuestion") {
			$(questionHash.tags).each(function() {
				var tag = new Tag(this, index++, self);
				node.append(tag.getNode());
				items.add(tag);
			});
		} else if (questionHash.type == "ProductQuestion"){
			$(questionHash.products).each(function() {
				var product = new Product(this, index++, self);
				node.append(product.getNode());
				items.add(product);
			});
		} else if (questionHash.type == "TermQuestion") {
			throw "Not implemented";
		}
	}
	
	// Build!
	build(question);	
}