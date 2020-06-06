document.querySelector('#submit').addEventListener('click', (evt) =>{
    evt.preventDefault();
    var msg = document.querySelector('#message').value;
    var msgdiv = document.createElement('p');
    msgdiv.innerHtml = msg;
    var messages = document.querySelector('#messages');
    messages.appendChild = msgdiv;
})