// Parameters
//  product - hash containing product information
//  controller - reference to containing controller
function Product(product, index, controller) {
	var node = $("<div>").addClass("product");
	var self = this;
	var index = index;
	
	function build(productHash) {
		console.log(productHash);
	}
	
	this.getNode = function() { return this.node; }
	
	build(product);
}