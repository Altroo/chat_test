let currentRecipient = '';
let chatInput = $('#chat-input');
let chatButton = $('#btn-send');
let attachmentButton = $("#attachment_button")
let userList = $('#user-list');
let messageList = $('#messages');

function updateUserList() {
    $.getJSON('altroochat/api/v1/user/', function (data) {
        userList.children('.user').remove();
        for (let i = 0; i < data.length; i++) {
	    let btn_class = "btn btn-danger btn-sm"
	    let status = "Offline"
	    if(data[i]['online']){
		btn_class = "btn btn-success btn-sm";
		status = "Online";
	    }
            const userItem = `<a class="list-group-item user" data-userid="${data[i]['id']}">${data[i]['username']}
		  <button
	    type="button"
	    id="user_${data[i]['id']}"
	    class="${btn_class}"
	    style="float:right;">${status}</button>
		</a>`;
            $(userItem).appendTo('#user-list');
        }
        $('.user').click(function () {
            userList.children('.active').removeClass('active');
            let selected = event.target;
            $(selected).addClass('active');
            setCurrentRecipient(selected.getAttribute("data-userid"));
        });
    });
}

function drawMessage(message) {
    // draw the messages in the forntend
    // using JS
    
    let position = 'left';
    const date = new Date(message.created);
    const seen = message.viewed;
    const attachment = message.attachment;
    if (Number(message.user) === Number(currentUser)) position = 'right';
    const messageItem = `
          <li class="message ${position}" id="message_${message.id}" data-initiator="${message.user}">
          <div class="avatar">${message.initiator}</div>
          <div class="text_wrapper">
          <div class="text">${message.body}<br>
          <span class="small">${date}</span>
	  ${seen === true ? `<span class="small" data-seen=true id="seen_${message.id}" style="color:red">Seen</span>`: `<span class="small" data-seen=false id="seen_${message.id}" style="color:red;">unseen</span>`}
    </div>
	${attachment !== null ?`<img src="${message.attachment}" alt="chat image" class="img-thumbnail" />`:`<span></span>`}
        </div>
        </li>`;
    $(messageItem).appendTo('#messages');
}

function getConversation(recipient) {
    // message used to get the last messages
    // of the user in the conversation. it depends
    // upon the settings file's MESSAGES_TO_LOAD variable
    // by default it is 15. it means only last 15 messages will be displayed
    
    $.getJSON(`altroochat/api/v1/message/?target=${recipient}`, function (data) {
        messageList.children('.message').remove();
        for (let i = data['results'].length - 1; i >= 0; i--) {
            drawMessage(data['results'][i]);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });

}

function renderSingleMessage(data){
    // funciton used to render the single
    // Message recieved after Success Post
    // request or when message is fetched
    // after getting a message ID using web
    // socket.
    if (Number(data.user) === Number(currentRecipient) ||
        (Number(data.recipient) === Number(currentRecipient) && Number(data.user) == Number(currentUser))) {
        drawMessage(data);
    }
    messageList.animate({scrollTop: messageList.prop('scrollHeight')});
}

function getMessageById(message_id) {
    // funcition used to fetch the message
    // from the backend databaes using an ID
    // which is received using webhook.
    let id = message_id
    $.getJSON(`altroochat/api/v1/message/${id}/`, function (data) {
        renderSingleMessage(data)
    });
}

function sendMessage(recipient, body) {
    // funciton used to send
    // message to the database using post
    // request.
    let data = new FormData();
    if($("#attachment_input")[0].files[0]){
	// if we have file attached then
	// only we will send the file
	// with data otherwise we
	// will not add this key 
	data.append('attachment', $("#attachment_input")[0].files[0])
    }
    
    data.append("recipient", recipient)
    data.append("body", body)
    
    $.ajax({url:'altroochat/api/v1/message/',
	    headers: {'Authorization': "Token " + localStorage.getItem('token')},
	    method: "post",
	    data:data,
	    contentType: false,
	    processData: false,
	    success:function(data){
		renderSingleMessage(data);
		document.getElementById("attachment_input").value = null;
		document.getElementById("currentInputImageCol").hidden = true;
	    },
	    error:function (xhr) {
		$.alert({title: "Error in API call", content: "check your console for more information"})
		console.log(xhr);
	    }
	   });
}

function setCurrentRecipient(username) {
    currentRecipient = username;
    getConversation(currentRecipient);
    enableInput();
}


function enableInput() {
    // whenever user select any user
    // to chat we need to enable input and input buttons
    chatInput.prop('disabled', false);
    chatButton.prop('disabled', false);
    attachmentButton.prop("disabled", false)
    chatInput.focus();
}

function disableInput() {
    // whenever user need to move out of chat windows
    // we need to disable all input fields and buttons
    chatInput.prop('disabled', true);
    chatButton.prop('disabled', true);
    attachmentButton.prop('disabled', true)
}

function updateOnlineOfflineStatus(user_id, status){
    if(status == "online"){
	try{
	    let user_anchor_element = document.getElementById(`user_${user_id}`)
	}
	catch(e){
	    // pass
	}
    }
}


function markLatestMessageSeen(event){
    // Method used for marking latest message as seen
    
    let lastMessageLiElement = $("#messages").children("li").last()
    if(lastMessageLiElement.attr('data-initiator') != currentUser && lastMessageLiElement && ! eval(lastMessageLiElement.find("span").last().attr("data-seen"))){
	try{
	    let messageId = lastMessageLiElement.attr('id').split('_')[1];
	    $.ajax({url: `altroochat/api/v1/message/${messageId}/`,
		    method: "patch",
		    headers: {'Authorization': "Token " + localStorage.getItem('token')},
		    data: JSON.stringify({'viewed': true}),
		    contentType: "application/json; charset:utf-8",
		    success: function(data){
			// pass do nothing
		    },
		    error: function(xhr){
			$.alert({title: "Error in API call", content: "check your console for more information"})
			console.log(xhr);
		    }
		   });
	}
	catch(e){
	    if(e instanceof TypeError){
		// it means users don't have any messages before
		// so we don't need to make any message as seen.a
	    }
	    else{
		throw(e)
	    }
	}
    }
    else{
	// passing as last message is alredy seen
    }
}

function showCurrentInputFileTag(){
    document.getElementById("currentInputImageCol").hidden = false;
    
}

function connectWebSocket(){
    // method used to connect
    // to the websocket backend.
    
    var socket = new WebSocket('ws://' + window.location.host + `/altroochatws`)
    
    socket.onmessage = function (e) {
	// we receive the ID of the message
	// using socket. after that we will call
	// the API to fetch the content of the message
	// and display it in the message window.
	let data = JSON.parse(e.data)
	if(data.message.type == "message"){
	    // message itself has been received
	    if(Number(currentUser) != data.message.initiator && Number(data.message.initiator) != Number(currentRecipient)){
		$.alert({
		    title: 'Notification',
		    content: `New Message from ${data.message.initiator_name}`,
		});
	    }
	    getMessageById(data.message.id);
	}
	else if(data.message.type == "status"){
	    // online offline status of the
	    // user is received
	    if(data.message.type="status"){
		if(data.message.online){
		    status_button = document.getElementById(`user_${data.message.user_id}`);
		    status_button.innerText = "Online";
		    status_button.classList.remove("btn-danger");
		    status_button.classList.add("btn-success");
		}
		else{
		    status_button = document.getElementById(`user_${data.message.user_id}`);
		    status_button.innerText = "Offline";
		    status_button.classList.remove("btn-success");
		    status_button.classList.add("btn-danger");
		}
	    }
	    
	}
	else if(data.message.type == "seen"){
	    // seen information of the message
	    // is received
	    let seenElement = document.getElementById(`seen_${data.message.id}`)
	    if(seenElement.getAttribute("data-seen") === true){
		//pass
	    }
	    else{
		
		seenElement.setAttribute("data-seen", true);
		seenElement.innerText = "Seen";
	    }
	}
    }
    
    socket.onclose = function(){
	// connection closed, discard old websocket
	// and create a new one in 5s
	socket = null
	setTimeout(connectWebSocket, 5000)
    }
}


function fillCurrentInputImage(input) {
    // whenever user select an image to be
    // attached with message this function
    // will be use to give him a real preview of the
    // inputed image.
    
    if (input.files && input.files[0]) {
	var reader = new FileReader();
	reader.onload = function (e) {
	    $('#currentInputImage').attr('src', e.target.result);
	}

	reader.readAsDataURL(input.files[0]);
	showCurrentInputFileTag()
    }
}

function getUserInformation(){
    // method used to get the token information
    // of the user

        $.getJSON(`altroochat/api/v1/message-login/`, function (data) {
	    localStorage.setItem('token', data.token)
	    connectWebSocket();
    });
}
$("#attachment_input").change(function(){
    // trigger fired when ever attached inpute field
    // is filled with som image. ie: user try to attach an image
    // with the message
    fillCurrentInputImage(this);
});


$(document).ready(function () {
    // enable attach button functionality
    attachmentButton.click(function(){
	$('#attachment_input').trigger('click');
    });
    updateUserList();
    disableInput();
    getUserInformation();
    //connectWebSocket();
    chatInput.keypress(function (e) {
        if (e.keyCode == 13)
            chatButton.click();
    });

    chatButton.click(function () {
	// when ever send button is clicked
	// if the user have typed anyting with
	// length > 0 we will send it. otherwise
	// noting will happend at all.
        if (chatInput.val().length > 0 || $("#attachment_input").val()) {
            sendMessage(currentRecipient, chatInput.val());
            chatInput.val('');
        }
    }) ;
    
});
