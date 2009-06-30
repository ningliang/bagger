function Recommendation(node) {
	
	var node = $(node);
	var modal = $("<div>").addClass("modal").appendTo(node).setModal();
	var self = this;
	var questionService = QuestionService.getInstance();
	var eventService = EventService.getInstance();

	var questions = [];
	var current;
	
	this.getNode = function() { return node; }
	
	this.getQuestion = function() {
		questionService.create(
			function(response) { 
				var question = new Question(response, self);
				questions.add(question);
				current = questions.length - 1;
				node.empty().append(question.getNode());
			},
			errorHandler
		);
	}
	
	this.answerQuestion = function(id, choice_id) {
		// TODO prevent concurrent answer events
		questionService.update(
			{id: id, choice_id: choice_id},
			function(response) { self.getQuestion(); },
			errorHandler
		);
	}
	
	this.previousQuestion = function() {
		if (current > 0) { 
			current--;
			node.empty().append(questions[current].getNode());
		}
	}
	
	this.nextQuestion = function() {
		if (current < questions.length - 1) {
			current++;
			node.empty().append(questions[current].getNode());
		}
	}
	
	this.addEvent = function(event) {	eventService.add(event); }
	
	function errorHandler(code, message) { modal.showMessage(code, message); }
	
	// Initialize!
	this.getNode();
}