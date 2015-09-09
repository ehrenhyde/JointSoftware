$( document ).ready(function() {
    //alert('js jQuery');
	
	//setup permisions buttons
	var link = $("#permissionButtonTreasurer");
	var oldRef = link.attr("href");
	console.log(oldRef);
	var url = window.location.href
	link.attr("href", oldRef + "&url="+ url);
	console.log( oldRef + "&url="+ url);
	
	link = $("#permissionButtonEventManager");
	oldRef = link.attr("href");
	console.log(oldRef);
	link.attr("href", oldRef + "&url="+ url);
	console.log( oldRef + "&url="+ url);
	
	link = $("#permissionButtonAdmin");
	oldRef = link.attr("href");
	console.log(oldRef);
	link.attr("href", oldRef + "&url="+ url);
	console.log( oldRef + "&url="+ url);
	
  });