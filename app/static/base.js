function addFriend(requester_id, requested_id){

	var button_id = '#addFriend'+requested_id.toString();
		$.ajax({
			url:"/add_friend",
			type:"POST",
			data:{requester_id: requester_id, requested_id: requested_id },
				success:function(data)
				{
					$(button_id).html("Friend Request Sent");
					$(button_id).removeAttr("onclick");
				},
				error:function(jqXHR, textStatus, error){
					$(button_id).html("Error: "+textStatus+" "+error);
				}
			});
return false;
}


function mouseover()
{
  element.className += ' hover';
  for(var x=0;x!=element.childNodes.length;++x)
  {
    if(element.childNodes[x].nodeType==1)
    {
      element.childNodes[x].className += 
        ' parent_hover';
    }
  }
}

function mouseout()
{
  element.className =
    element.className.replace(/ ?hover$/,'');
  for(var x=0;x!=element.childNodes.length;++x)
  {
    if(element.childNodes[x].nodeType==1)
    {
      element.childNodes[x].className =
      element.childNodes[x].className.replace
        (/ ?parent_hover$/,'');
    }
  }
}
if (window.attachEvent) window.attachEvent("onmouseout", mouseout);
if (window.attachEvent) window.attachEvent("onmouseover", mouseover);

sfHover = function() {
	var sfEls = document.getElementById("notif_dropdown");
	for (var i=0; i<sfEls.length; i++) {
		sfEls[i].onmouseover=function() {
			this.className+=" sfhover";
		}
		sfEls[i].onmouseout=function() {
			this.className=this.className.replace(new RegExp(" sfhover\\b"), "");
		}
	}
}
if (window.attachEvent) window.attachEvent("onload", sfHover);


function approveFriendRequest(requester_id, requested_id, approve=true){
		var button_id = '#approve_'+requester_id.toString();

		$.ajax({
			url:"/approve_friend",
			type:"POST",
			data:{requester_id: requester_id, 
				requested_id: requested_id ,
				approve: true
			},
				success:function(data)
				{
					$(button_id).html("Approved");
					$(button_id).removeAttr("onclick");
					$(button_id).addClass("button_disabled");
				},
				error:function(jqXHR, textStatus, error){
					$(button_id).html("Error: "+textStatus+" "+error);
				}
			});

return false;
}

function ignoreFriendRequest(requester_id, requested_id, approve=true){
		var button_id = '#ignore_'+requester_id.toString();

		$.ajax({
			url:"/ignore_friend",
			type:"POST",
			data:{requester_id: requester_id, 
				requested_id: requested_id ,
				approve: true
			},
				success:function(data)
				{
					$(button_id).html("Ignored");
					$(button_id).removeAttr("onclick");
					$(button_id).addClass("button_disabled");
				},
				error:function(jqXHR, textStatus, error){
					$(button_id).html("Error: "+textStatus+" "+error);
				}
			});

return false;
}



