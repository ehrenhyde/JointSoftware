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

function removeAttending(eventId,userId){
	console.log("calling removeAttending");
	console.log('eventId = ' + eventId);	
	console.log('userId = ' + userId);
	$.ajax({
		type: "POST",
		url: "/removeAttendance",
		dataType: 'json',
		data: JSON.stringify({
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