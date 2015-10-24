function sendAttending(status,eventId,userId,callbackFunc){
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
		if (callbackFunc){
			callbackFunc();
		}
		
	});
}

function toggleAttendance(eventId,userId,htmlCaller,callbackFunc){
	console.log('called toggleAttendance eventId: ' + eventId + ' userId: ' + userId);
	
	//disable two clicks at the same time
	if ($(htmlCaller).attr("loading") == "true"){
		console.log("already loading");
		return;
	}
	
	//disable control
	if (htmlCaller){
		var oldColour = $(htmlCaller).css('color');
		$(htmlCaller).attr("loading","true");
		$(htmlCaller).css('color','orange');
	}
	
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
		
		if (data.success == true){
			console.log('toggleAttendance was a success. version: ' + data.version + ' oldStatus: ' + data.oldStatus +' newStatus: ' + data.newStatus);
			$(htmlCaller).text(data.newButtonMsg);
			//update appropriate labels on the UI
			$('[dynamic-credits-accountId-'+userId + ']').text(data.newCredits);
			$('#eventRow-'+eventId).removeClass();

			if (data.newStatus == 'Attending'){
				$('#eventRow-'+eventId).addClass('success');
			}else if(data.newStatus == 'Maybe'){
				$('#eventRow-'+eventId).addClass('info');
			}
			
			if(callbackFunc){
				callbackFunc();
			}
			
			
			
		}else{
			console.log('toggleAttendance fail');
			$(htmlCaller).css("border-color", "red");
			$(htmlCaller).css("color", "red");
			window.alert(data.comment);
		}
		
		//re-enable control
		if (htmlCaller){
			$(htmlCaller).css('color',oldColour);
			$(htmlCaller).attr("loading","false");
		}
		
	})
	.fail(function(jqXHR,textStatus) {
		//re-enable control
		if (htmlCaller){
			$(htmlCaller).css('color',oldColour);
			$(htmlCaller).attr("loading","false");
		}
	});
	
}

function addAttending(status,eventId,callbackFunc){
	console.log("calling addAttending");
	var Input = $("#Adduser");
	var userId = +Input.val();
	console.log('userId = ' + userId);
	sendAttending(status,eventId,userId,callbackFunc);
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

function updateAttendeesCount(elementId,eventId){
	console.log('updating attendees count');
	
	$.ajax({
		type:"POST",
		url:'/GetAttendeesCount',
		dataType:'json',
		data: JSON.stringify({
			'eventId':eventId
		})
	})
	.done(function(data){
		console.log('returned');
		if (data.success == true){
			console.log('was a success');
			console.log(data.attendeesCount);
			var jQSelect = '#'+elementId;
			console.log('jQSelect :' + jQSelect);
			$(jQSelect).text(data.attendeesCount);
		}else{
			console.log('fail');
		}
		
	})
	.fail(function(jqXHR,textStatus) {
		$('#'+elementId).html("Could not get attendees count");
	});
}

function fillAttendeesListItems(listId,eventId,status){
	
	console.log('filling attendees list');
	
	$.ajax({
		type:"POST",
		url:'/GetAttendees',
		dataType:'json',
		data: JSON.stringify({
			'eventId':eventId,
			'status':status
		})
	})
	.done(function(data){
		console.log('returned');
		if (data.success == true){
			console.log('was a success');
			console.log(data.attendeeNames);
			var names = data.attendeeNames;
			//update appropriate labels on the UI
			$('#'+listId).html("");
			for(var i = 0;i<names.length;i++){
				$("<li>"+names[i]+"</li>").appendTo('#'+listId);
			}
		}else{
			console.log('fail');
		}
		
	})
	.fail(function(jqXHR,textStatus) {
		$('#'+listId).html("Could not get attendees");
	});
}

function DeleteUser(UserID){
	console.log('called DeleteUser userId: ' + UserID);
	var r = confirm("Press OK, to Confirm Delete User");
	if (r == true) {
		$.ajax({
			type: "POST",
			url: "/DeleteAccount",
			dataType: 'json',
			data: JSON.stringify({
				"userId" : UserID
			})
		}).done(function( data ) {
			console.log('DeleteUser returned');
			if (data.success == true){
				console.log('User Removed');
				window.location.replace( '/users')
			}else{
				console.log('Delete Failed');
					//console.log(data.success);
				}
			//location.reload();
		});
	}else{
		console.log('Aborted DeleteUser userId: ' + UserID);
	}
}

function deleteEvent(eventId){
	console.log('called deleteEvent eventId: ' + eventId);
	var r = confirm("Press OK, to Confirm Delete Event");
	if (r == true) {
		$.ajax({
			type: "POST",
			url: "/DeleteEvent",
			dataType: 'json',
			data: JSON.stringify({
				"eventId" : eventId
			})
		}).done(function( data ) {
			console.log('DeleteEvent returned');
			if (data.success == true){
				console.log('Event Removed');
				window.location.replace( '/events')
			}else{
				console.log('Delete Failed');
					//console.log(data.success);
				}
			//location.reload();
		});
	}else{
		console.log('Aborted deleteEvent eventId: ' + eventID);
	}
}