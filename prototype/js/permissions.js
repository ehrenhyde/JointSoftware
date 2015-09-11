var permissions = {
	
	getAdminActive: function(){
		if (localStorage.adminActive !== "undefined"){
			return (localStorage.adminActive == "true");
		}else{
			return false;
		}
	},
	
	applyToUI: function(speed){
		
		//admin
		
		if (this.getAdminActive() == true){
			console.log("showing");
			$('[adminOnly]').show(speed);
		}else{
			console.log("hiding");
			$('[adminOnly]').hide(speed);
		}
		
		if (this.getAdminActive()==true){
			$('#permissionButtonAdmin').text("Deactivate Admin");
		}else{
			$('#permissionButtonAdmin').text("Activate Admin");
		}
	}, 
	
	toggleAdminActive: function(){
		console.log('toggleAdminActive');
		
		if (this.getAdminActive()== false){
			localStorage.adminActive =  "true";
		}else{
			localStorage.adminActive = "false";
		}
		console.log(localStorage.adminActive);
		
		this.applyToUI("slow");	
	
		
	}
}

$(window).ready(function(){
	permissions.applyToUI(0);
});