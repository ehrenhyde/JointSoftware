function permissionType(activeName,htmlTag,buttonTextActive,buttonTextUnactive,buttonId){
	this.activeName = activeName;
	this.htmlTag = htmlTag;
	this.buttonTextActive = buttonTextActive;
	this.buttonTextUnactive = buttonTextUnactive;
	this.buttonId = buttonId;
}

function hasPermissionTag(element,attrName){
	var attr = element.attr(attrName);

	// For some browsers, `attr` is undefined; for others,
	// `attr` is false.  Check for both.
	if (typeof attr !== typeof undefined && attr !== false){
		//console.log('element ' + element.attr('id') + ' has attribute ' + attrName);
		return true;
	}else{
		//console.log('not');
		return false;
	}
}

var allPermissionTypes = {
	admin:new permissionType('adminActive','adminAllowed','Deactivate Admin','Activate Admin','permissionButtonAdmin'),
	treasurer:new permissionType('treasurerActive','treasurerAllowed','Deactivate Treasurer','Activate Treasurer','permissionButtonTreasurer'),
	eventManager: new permissionType('eventManagerActive','eventManagerAllowed','Deactivate Event Manager','Activate Event Manager','permissionButtonEventManager'),
	
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
	
	togglePermissionDependantElements(permissionTypes,permissionType,speed){
		
		
		if (this.getPermissionTypeActive(permissionType.activeName) == true){
			//console.log("showing " + permissionType.htmlTag);
			//wrap in [] because that is the format for the jQuery selector
			$('[' + permissionType.htmlTag + ']').show(speed);
		}else{
			//test all permission types to check if another doesn't keep it shown
			var getPermissionTypeActive = this.getPermissionTypeActive;
			
			
			$('[' + permissionType.htmlTag + ']').each(function(){
				var shouldHide = true;
				for (var i = 0;i<permissionTypes.length;i++){
					var elementHasPermissionTag = hasPermissionTag($(this),permissionTypes[i].htmlTag);
					//check if the tag is present and that the user has the associated active permission
					var activeName = permissionTypes[i].activeName
					if (elementHasPermissionTag && getPermissionTypeActive(activeName)){
						shouldHide = false;
					}
				}
				if (shouldHide){
					$(this).hide(speed);
				}
			})
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
		
		var permissionTypes = allPermissionTypes.toArray();
		for(var i = 0; i<permissionTypes.length;i++){
			this.togglePermissionDependantElements(permissionTypes,permissionTypes[i],speed);
			this.togglePermissionButtons(permissionTypes[i]);
		}
	}, 
	
	togglePermissionTypeActive: function(activeName){
		//console.log('toggle ' + activeName + ' active');
		
		if (this.getPermissionTypeActive(activeName)== false){
			localStorage[activeName] =  "true";
		}else{
			localStorage[activeName] = "false";
		}
		//console.log(localStorage[activeName]);
		
		this.applyToUI("slow");	
	
		
	},
	
	toggleTreasurerActive: function(){
		//console.log('toggleTreasurerActive');
		this.togglePermissionTypeActive(allPermissionTypes.treasurer.activeName);
	},
	toggleAdminActive: function(){
		//console.log('toggleAdminActive');
		this.togglePermissionTypeActive(allPermissionTypes.admin.activeName);
	},
	toggleEventManagerActive: function(){
		//console.log('toggleEventMangerActive');
		this.togglePermissionTypeActive(allPermissionTypes.eventManager.activeName);
	}
}

$(window).ready(function(){
	permissions.applyToUI(0);
});