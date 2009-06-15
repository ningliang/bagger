$(function() {
	var qs = QuestionService.getInstance();
	
	// Set up the question widget
	$('#recommendation').each(function() {
		var that = this;
		var currentId = null;
		
		function getQuestion() {
			qs.generate(
				function(response) {
					console.log(response);
					currentId = response.id;
					that.clear().append(questionNode(response));
				}, 
				function(code, message) { ms.
					// TODO make this better later on
					ms.showMessage(message);
				});
		}
		
		function answerQuestion(id, choice) {
			qs.answer(
				{id: id, choice: choice}, 
				function(response) {
					// Generate a new question
				}, 
				function(code, message) {
					
				});
		}
		
		function questionNode() { return $("<div/>").attr("id", "question"); }
		
		getQuestion();
	});
});