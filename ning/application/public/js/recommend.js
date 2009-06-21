$(function() {
	
	var qs = QuestionService.getInstance();
	var modal = $("#modal").setModal();
	
	// Set up the question widget
	$("#recommendation").each(function() {
		var that = $(this);
		var currentId = null;
		var currentQuestionNode = null;
		
		function getQuestion() {
			qs.generate(
				function(response) {
					currentId = parseInt(response.id);
					currentQuestionNode = bindNode(questionNode(response));
					that.empty().append(currentQuestionNode);
				}, 
				function(code, message) { 
					console.log(code + " " + message);
					modal.showMessage(code + " " + message);
				});
		}
		
		function answerQuestion(id, choice_id) {
			unbindNode(currentQuestionNode);
			qs.answer(
				{id: id, choice: choice_id}, 
				function(response) {
					response.success ? getQuestion() : modal.showMessage(response.message);
				}, 
				function(code, message) {
					console.log(code + " " + message);
					modal.showMessage(code + " " + message);
				});
		}
		
		// Return a question node
		function questionNode(question) { 
			var node = $("<div/>").addClass("question");
			
			if (question.type == "TagQuestion") {
				$(question.tags).each(function() {
					var tag = this;
					tagNode = $("<a/>").addClass("tag").attr("href", "#").attr("choice_id", tag.id).attr("selected", tag.id == question.choice)
						.append($("<div/>").addClass("name").html(decodeURIComponent(tag.name)))
						.append($("<div/>").addClass("meta"));
					node.append(tagNode);
				});
			} else if (question.type == "ProductQuestion") {
				$(question.products).each(function() {
					var product = this;
					var productNode = $("<a/>").addClass("product").attr("href", "#").attr("choice_id", product.id).attr("selected", product.id == question.choice)
						.append($("<div/>").addClass("name").html(decodeURIComponent(product.name)))
						.append($("<div/>").addClass("description").html(decodeURIComponent(product.description)));
					$(product.photos).each(function() {
						var photo = this;
						productNode.append($("<img/>").attr("width", PHOTO_WIDTH).attr("height", PHOTO_HEIGHT).attr("src", decodeURIComponent(photo.url)));
					});
					node.append(productNode);
				});
			} else {
				throw "Invalid question type";
			}
			
			return node;
		}
		
		function unbindNode(questionNode) {	
			var node = $(questionNode);
			node.children("a").unbind();	
			return node;
		}
		
		function bindNode(questionNode) {
			var node = $(questionNode);
			node.children("a").each(function() {
				$(this).click(function(e) {
					e.preventDefault();
					answerQuestion(currentId, $(this).attr("choice_id"));
				});
			}); 
			return node;
		}
	
		// Initial question retrieval
		getQuestion();
	});
});