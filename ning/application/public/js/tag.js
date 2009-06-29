// Parameters
//  product - hash containing product information
//  controller - reference to containing controller
function Tag(tag, index, controller) {
	var node = $("<div/>").addClass("tag");
	var index = index;
	var self = this;
	
	function build(tagHash) {
		console.log(tagHash);
	}
	
	this.getNode = function() { return this.node; }
	
	build(tag);
}