function sendAttending(status,eventId,userId){
	console.log("calling sendAttending");
	console.log('status = ' +status);
	console.log('eventId = ' + eventId);	
	console.log('userId = ' + userId);
	$.ajax({
		type: "POST",
		url: "/toggleAttendance",
		dataType: 'json',
		data: JSON.stringify({
			"status": status,
			"eventId":eventId,
			"userId" : userId
		})
	})
	.done(function( data ) {
		console.log('returned');
		if (data.success == true){
			console.log('was a success');
		}else{
			console.log('fail');
			console.log(data.success);
		}
		location.reload();
	});
}

function toggleAttendance(eventId,userId,htmlCaller,reload){
	console.log('called toggleAttendance eventId: ' + eventId + ' userId: ' + userId);
	
	$.ajax({
		type: "POST",
		url: "/toggleAttendance",
		dataType: 'json',
		data: JSON.stringify({
			"eventId":eventId,
			"userId" : userId
		})
	})
	.done(function( data ) {
		console.log('toggleAttendance returned');
		if (data.success == true){
			console.log('toggleAttendance was a success. version: ' + data.version + ' oldStatus: ' + data.oldStatus +' newStatus: ' + data.newStatus);
			$(htmlCaller).text(data.newButtonMsg);
			if (reload){
				location.reload();
			}
		}else{
			console.log('toggleAttendance fail');
			$(htmlCaller).css("border-color", "red");
			$(htmlCaller).css("color", "red");
				window.alert(data.comment);
				//console.log(data.success);
			}
		//location.reload();
	});
	
}

function addAttending(status,eventId){
	console.log("calling addAttending");
	var Input = $("#Adduser");
	var userId = +Input.val();
	console.log('userId = ' + userId);
	sendAttending(status,eventId,userId);
}

function SaveComment(eventId){
	console.log("calling SaveComment");
	console.log('eventId = ' + eventId);	
	var Input = $("#Comment");
	var comment = Input.val();
	$.ajax({
		type: "POST",
		url: "/SaveComment",
		dataType: 'json',
		data: JSON.stringify({
			"Comment": comment,
			"eventId":eventId,
		})
	})
	.done(function( data ) {
		console.log('returned');
		if (data.success == true){
			console.log('was a success');
		}else{
			console.log('fail');
			console.log(data.success);
		}
		location.reload();
	});
}

function changeCredits(userId,creditsChange,triggerControl){
	
	//disable two clicks at the same time
	if ($(triggerControl).attr("loading") == "true"){
		return;
	}
	console.log('calling changeCredits');
	console.log('userId = ' + userId);
	console.log('creditsChange = ' + creditsChange);
	
	//disable control
	if (triggerControl){
		var oldColour = $(triggerControl).css('color');
		$(triggerControl).attr("loading","true");
		$(triggerControl).css('color','orange');
	}
	
	$.ajax({
		type:"POST",
		url:'/changeCredits',
		dataType:'json',
		data: JSON.stringify({
			"userId":userId,
			'creditsChange':creditsChange
		})
	})
	.done(function(data){
		console.log('returned');
		if (data.success == true){
			console.log('was a success');
		}else{
			console.log('fail');
		}
		
		//re-enable control
		if (triggerControl){
			$(triggerControl).css('color',oldColour);
			$(triggerControl).attr("loading","false");
		}
		
		//update appropriate labels on the UI
		$('[dynamic-credits-accountId-'+userId + ']').text(data.newCredits);
		
	})
	.fail(function(jqXHR,textStatus) {
		alert( "Oh dear! " + textStatus + " Better luck next time..." );
		//re-enable control
		if (triggerControl){
			$(triggerControl).css('color',oldColour);
			$(triggerControl).attr("loading","false");
		}
	});
}