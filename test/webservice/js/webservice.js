function callWebservice(){
	console.log("calling webservice");
	
	$.ajax({
		type: "POST",
			url: "/monster",
            dataType: 'json',
            data: JSON.stringify({ "name": "Fred"})
	})
	.done(function( data ) {
		console.log('returned');
		alert("Dear " + data.favouriteFood + "\nPrepare to be chewed by a " + data.colour + " monseter with " + data.teeth.num + " " + data.teeth.size + " teeth");
	});
}