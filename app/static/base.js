function readURL(input) {

	if (input.files && input.files[0]) {
		var reader = new FileReader();

		reader.onload = function(e) {
			$('#preview_img').attr('src', e.target.result);
			$('#add_picture').html("Picture Added");
			}
		reader.readAsDataURL(input.files[0]);
	}
	return true;
}

$(window).load(function () {
	var cur_pic_id = "#current_pic_url"
	var hello = $(cur_pic_id).length.toString()
	if ( $(cur_pic_id).length > 0) {
		var pic_url = $(cur_pic_id).val();
		if (pic_url !== ""){
	    	var pic_src = pic_url + "?" + new Date().getTime();
	    	$("#preview_img").attr("src", pic_src) ;
		}
	}
});

 // $(window).load(function () {
	// var selected_val = $('#project_select').val();
	// var new_url = "/post?"+selected_val.toString();
	// $('#create_post').href(new_url);
 // });


// function postStatus(this_id_in){

// 		var formData = new FormData($('form.post_status')[0]);

// 		var this_id ='#'+this_id_in;
// 		var user_id = $("meta[name='user_id']");
// 		var post_type = "status";

// 		$.ajax({
// 			url:"/post",
// 			type:"POST",
// 			data:{user_id: user_id, 
// 				project_id: project_id
// 				post_text: post_text 
// 			},
// 				success:function(data)
// 				{	
// 					msg = "";
// 					if (approved) {
// 						msg = "Friend Request Approved";
// 					} else {
// 						msg = "Friend Request Ignored";
// 					}
// 					$(this_id).html(msg);
// 					$(this_id).removeAttr("onclick");
// 					$(this_id).addClass("button_disabled");

// 				},
// 				error:function(jqXHR, textStatus, error){
// 					$(this_id).html("Error");
// 				}
// 			});

// return false;
// }


function addFriend(requester_id, requested_id){

	var button_id = '#addFriend'+requested_id.toString();
		$.ajax({
			url:"/request_friend",
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


function approveFriendRequest(this_button, approved, requester_id, requested_id){

		$.ajax({
			url:"/approve_friend",
			type:"POST",
			data:{requester_id: requester_id, 
				requested_id: requested_id ,
				approve: approved
			},
				success:function(data)
				{	
					msg = "";
					if (approved) {
						msg = "Friend Request Approved";
					} else {
						msg = "Friend Request Ignored";
					}
					$(this_button).html(msg);
					$(this_button).removeAttr("onclick");
					$(this_button).addClass("button_disabled");

				},
				error:function(jqXHR, textStatus, error){
					$(this_button).html("Error");
				}
			});

return false;
}

function newPost(){
	var project = $('#post_project').val();
	var path = "/post?pid="+project;
	window.location.href = window.location.hostname+path;
	return true;
}


$('#preview_img').change(function(i, item) {
    var img_height = $(item).height();
    var div_height = $(item).parent().height();
    if(img_height<div_height){
        //IMAGE IS SHORTER THAN CONTAINER HEIGHT - CENTER IT VERTICALLY
        var newMargin = (div_height-img_height)/2+'px';
        $(item).css({'margin-top': newMargin });
    }else if(img_height>div_height){
        //IMAGE IS GREATER THAN CONTAINER HEIGHT - REDUCE HEIGHT TO CONTAINER MAX - SET WIDTH TO AUTO  
        $(item).css({'width': 'auto', 'height': '100%'});
        //CENTER IT HORIZONTALLY
        var img_width = $(item).width();
        var div_width = $(item).parent().width();
        var newMargin = (div_width-img_width)/2+'px';
        $(item).css({'margin-left': newMargin});
    }
});




