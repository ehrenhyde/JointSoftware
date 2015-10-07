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
			console.log(data.success);
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

function changeCredits(userId,creditsChange){
	console.log('calling changeCredits');
	console.log('userId = ' + userId);
	console.log('creditsChange = ' + creditsChange);
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
		location.reload();
	});
}