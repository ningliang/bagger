function InputQuestion(question, controller) {
	//console.log("initialize question");
	var node = $("<div/>").addClass("question");
	var modal = new Modal();
	
	var question = question;
	var controller = controller;
	var self = this;
	
	this.getNode = function() { return node; }
	
	this.answer = function(answer) {
		controller.answerQuestion(question.id, answer);
	}
	
	function build(hash) {
		//console.log(hash);
		node.empty().append($("<div/>").addClass("statement").html(hash.statement));
		node.append($("<form/>")
			.append($("<input type='text'/>"))
			.append($("<input type='submit' value='Submit' name='Submit'/>")));
	}
	build(question);
	
	$("input[type=submit]", node).click(function(e) {
		e.preventDefault();
		controller.answerQuestion(question.id, $("input[type=text]", node).val());
	});
}
