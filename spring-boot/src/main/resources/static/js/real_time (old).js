var sessionId = generateSessionId(); // Generate a unique session ID
console.log('Session ID: ' + sessionId);
var socket = new SockJS('http://localhost:8080/ws');
var stompClient = Stomp.over(socket);
var video = document.querySelector('#video');
var canvas = document.querySelector('#canvas');
var context = canvas.getContext('2d');
var videoButton = document.getElementById('toggleVideoButton');
var processingButton = document.getElementById('toggleProcessingButton');
var isVideoPlaying = false;
var isProcessing = false;



stompClient.connect({'session-id': sessionId}, function(frame) {
    document.getElementById('connectionStatus').innerHTML = 'Connected to WebSocket';

    stompClient.subscribe('/topic/messages/'+sessionId, function(message) {
        // Assuming the image is base64 encoded
        document.getElementById('image').src = 'data:image/png;base64,' + message.body;
    });
}, function(error) {
    document.getElementById('connectionStatus').innerHTML = 'Failed to connect to WebSocket';
});

videoButton.addEventListener('click', function() {
    isVideoPlaying = !isVideoPlaying;
    this.textContent = isVideoPlaying ? 'Pause Video Recording' : 'Start Video Recording';

    if (isVideoPlaying) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
                processingButton.disabled = false; // Enable the "Start Processing" button
                isProcessing = true;
                processingButton.textContent = 'Pause Processing';
            })
            .catch(function(error) {
                console.error('Failed to get user media', error);
            });
    } else {
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        if (isProcessing) {
            isProcessing = false;
            processingButton.textContent = 'Start Processing';
        }
        processingButton.disabled = true; // Disable the "Start Processing" button
    }
});

processingButton.addEventListener('click', function() {
    if (!isVideoPlaying) {
        return; // Don't do anything if the video is not playing
    }
    isProcessing = !isProcessing;
    this.textContent = isProcessing ? 'Pause Processing' : 'Start Processing';
});

setInterval(function() {
    if (isVideoPlaying && isProcessing) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        var dataUrl = canvas.toDataURL('image/jpeg',0.5);
        var base64 = dataUrl.split(',')[1];
        stompClient.send("/app/send", {'session-id': sessionId}, base64);
    }
}, 200);

function generateSessionId() {
    // Generate a random session ID
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}