function callWebservice(status,eventId){
	console.log("calling webservice");
	
	$.ajax({
		type: "POST",
			url: "/toggleAttendance",
            dataType: 'json',
            data: JSON.stringify({
				"status": status,
				"eventId":eventId
			})
	})
	.done(function( data ) {
		console.log('returned');
		if (data.success == true){
			console.log('was a success');
			
			$('#testButtonA').css('visibility','hidden');
			$('#testButtonB').css('visibility','visible');
		}else{
			console.log('fail');
			console.log(data.success);
		}
		
	});
}


function sendAttending(status,eventId){
	console.log('status = ' +status);
	console.log('eventId = ' + eventId);
	
	var nameInput = $("#testText");
	var name = nameInput.val();
	
	console.log('name = ' + name);
	
	callWebservice(status,eventId);
	
}