$(function() {
	
	var qs = QuestionService.getInstance();
	var modal = $('#modal').setModal();
	
	// Set up the question widget
	$('#recommendation').each(function() {
		var that = $(this);
		var currentId = null;
		
		function getQuestion() {
			qs.generate(
				function(response) {
					currentId = response.id;
					that.empty().append(questionNode(response));
				}, 
				function(code, message) { 
					console.log(code + " " + message);
					ms.showMessage(code + " " + message);
				});
		}
		
		function answerQuestion(id, choice) {
			qs.answer(
				{id: id, choice: choice}, 
				function(response) {
					// Generate a new question
				}, 
				function(code, message) {
					console.log(code + " " + message);
					ms.showMessage(code + " " + message);
				});
		}
		
		// Return a question node
		function questionNode(question) { 
			node = $("<div/>").addClass("question");
			
			if (question.type == "TagQuestion") {
				$(question.tags).each(function() {
					var tag = this;
					node.append($("<a/>").addClass("tag").attr("href", "#").attr("id", tag.id)
						.append($("<div/>").addClass("name").html(tag.name))
						.append($("<div/>").addClass("meta")));
				});
			} else if (question.type == "ProductQuestion") {
				$(question.products).each(function() {
					var product = this;
					var productNode = $("<a/>").addClass("product").attr("href", "#").attr("id", product.id)
						.append($("<div/>").addClass("name").html(product.name))
						.append($("<div/>").addClass("description").html(product.description));
					$(product.photos).each(function() {
						var photo = this;
						productNode.append($("<img/>").attr("width", PHOTO_WIDTH).attr("height", PHOTO_HEIGHT).attr("src", decodeURIComponent(photo.url)));
					});
					node.append(productNode);
				});
			} else {
				throw "Invalid question type";
			}
			
			// Bindings
			$(node).each(function() {
				var that = this;
				
			});
			
			return node;
		}
		
		// Initial question retrieval
		getQuestion();
	});
});