function MultiQuestion(question, controller) {
	//console.log("initialize question");
	var node = $("<div/>").addClass("question");
	var modal = new Modal();
	
	var question = question;
	var controller = controller;
	var self = this;
	var choices = [];
	
	this.getNode = function() { return node; }
	
	this.answer = function(answer) {
		controller.answerQuestion(question.id, answer);
	}
	
	// Construct the node - behavior on the choice nodes
	function build(hash) {
		//console.log(hash);
		node.empty().append($("<div/>").addClass("statement").html(hash.statement));
		for (var i = 0; i < hash.choices.length; i++) {
			var choice = new Choice(i, hash.choices[i], self);
			choices.push(choice);
			node.append(choice.getNode());	
		}	
	}
	build(question);
}

function Choice(index, choice, controller) {
	var node = $("<a/>").addClass("choice").attr("href", "#");
	var index = index;
	var choice = choice;
	var self = this;
	
	this.getNode = function() { return node; }
	
	// Construct the node
	function build(hash) {
		if (hash.url) node.append($("<img/>").attr("src", hash.url));
		else node.html(hash);
	}
	build(choice);
	
	// Binding
	node.click(function(e) {
		e.preventDefault();
		controller.answer(index);
	});
}