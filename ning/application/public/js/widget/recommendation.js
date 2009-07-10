function RecommendationDashboard(node) {
	//console.log("initializing");
	var node = $(node);
	var modal = new Modal();
	var self = this;	
	var questions = [];
	var current;
	
	var questionService = QuestionService.getInstance();
	
	this.getNode = function() { return node; }
	
	this.newQuestion = function() {
		//console.log("new question");
		questionService.create(
			function(response) {
				var question = null;
				if (response.type == "MULTI") {
					question = new MultiQuestion(response, self);
				} else if (response.type == "INPUT") {
					question = new InputQuestion(response, self);
				}
				questions.push(question);
				current = questions.length - 1;
				node.empty().append(question.getNode());
			},
			errorHandler);
	}
	
	this.answerQuestion = function(id, answer) {
		//console.log("answering");
		//console.log(id + " " + answer);
		questionService.update({id: id, answer: answer},
			function(response) { self.newQuestion(); },
			errorHandler
		);
	}
	
	this.selectQuestion = function(index) {
		//console.log("getting question " + index)
		if (index < questions.length && index > 0) {
			current = index;
			node.empty().append(questions[current].getNode());
		}
	}
	
	function errorHandler(code, message) { modal.showMessage(code + ": " + message); }
	
	this.newQuestion();
	
	return node;
}