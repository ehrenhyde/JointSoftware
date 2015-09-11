var permissions = {
	
	applyToUI: function(speed){
		
		//admin
		
		var adminActive = (localStorage.adminActive == "true");
		if (adminActive == true){
			console.log("showing");
			$('[adminOnly]').show(speed);
		}else{
			console.log("hiding");
			$('[adminOnly]').hide(speed);
		}
		
		if (adminActive==true){
			$('#permissionButtonAdmin').text("Deactivate Admin");
		}else{
			$('#permissionButtonAdmin').text("Activate Admin");
		}
	}, 
	
	toggleAdminActive: function(){
		console.log('toggleAdminActive');
		
		if (localStorage.adminActive !== "undefined"){
			if (localStorage.adminActive == "false"){
				localStorage.adminActive =  "true";
			}else{
				localStorage.adminActive = "false";
			}
		}else{
			localStorage.adminActive = "true";
		}
		console.log(localStorage.adminActive);
		
		this.applyToUI("slow");	
	
		
	}
}

$(window).ready(function(){
	permissions.applyToUI(0);
});