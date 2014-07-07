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