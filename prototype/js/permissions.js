function permissionType(activeName,htmlTag,buttonTextActive,buttonTextUnactive,buttonId){
	this.activeName = activeName;
	this.htmlTag = htmlTag;
	this.buttonTextActive = buttonTextActive;
	this.buttonTextUnactive = buttonTextUnactive;
	this.buttonId = buttonId;
}

var allPermissionTypes = {
	admin:new permissionType('adminActive','adminOnly','Deactivate Admin','Activate Admin','permissionButtonAdmin'),
	treasurer:new permissionType('treasurerActive','treasurerOnly','Deactivate Treasurer','Activate Treasurer','permissionButtonTreasurer'),
	eventManager: new permissionType('eventManagerActive','eventManagerOnly','Deactivate Event Manager','Activate Event Manager','permissionButtonEventManager'),
	
	toArray: function (){
		//console.log('casting allPermissionTypes to array');
		return [this.admin,this.treasurer,this.eventManager];
	}
}

var permissions = {
	
	getPermissionTypeActive: function(activeName){
		//console.log('testing ' + activeName)
		if (localStorage[activeName] !== "undefined"){
			return (localStorage[activeName] == "true");
		}else{
			return false;
		}
	},
	
	togglePermissionDependantElements(permissionType,speed){
		if (this.getPermissionTypeActive(permissionType.activeName) == true){
			console.log("showing " + permissionType.htmlTag);
			//wrap in [] because that is the format for the jQuery selector
			$('[' + permissionType.htmlTag + ']').show(speed);
		}else{
			console.log("hiding " + permissionType.htmlTag);
			$('[' + permissionType.htmlTag + ']').hide(speed);
		}
	},
	
	togglePermissionButtons: function(permissionType){
		if (this.getPermissionTypeActive(permissionType.activeName)==true){
			$('#' + permissionType.buttonId).text(permissionType.buttonTextActive);
		}else{
			$('#' + permissionType.buttonId).text(permissionType.buttonTextUnactive);
		}
	},
	
	applyToUI: function(speed){
		
		//Permission dependant elements
		var permissionTypes = allPermissionTypes.toArray();
		for(var i = 0; i<permissionTypes.length;i++){
			this.togglePermissionDependantElements(permissionTypes[i],speed);
			this.togglePermissionButtons(permissionTypes[i]);
		}
	}, 
	
	togglePermissionTypeActive: function(activeName){
		console.log('toggle ' + activeName + ' active');
		
		if (this.getPermissionTypeActive(activeName)== false){
			localStorage[activeName] =  "true";
		}else{
			localStorage[activeName] = "false";
		}
		//console.log(localStorage[activeName]);
		
		this.applyToUI("slow");	
	
		
	},
	
	toggleTreasurerActive: function(){
		console.log('toggleTreasurerActive');
		this.togglePermissionTypeActive(allPermissionTypes.treasurer.activeName);
	},
	toggleAdminActive: function(){
		console.log('toggleAdminActive');
		this.togglePermissionTypeActive(allPermissionTypes.admin.activeName);
	},
	toggleEventMangerActive: function(){
		console.log('toggleEventMangerActive');
		this.togglePermissionTypeActive(allPermissionTypes.eventManager.activeName);
	}
}

$(window).ready(function(){
	permissions.applyToUI(0);
});