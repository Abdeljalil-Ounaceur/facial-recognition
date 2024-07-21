var sessionId = generateSessionId(); // Generate a unique session ID
console.log('Session ID: ' + sessionId);
var socket = new SockJS('http://localhost:8080/ws');
var stompClient = Stomp.over(socket);
var video = document.querySelector('#video');
var error_message = document.getElementById('error-message');

var videoCanvas = document.querySelector('#videoCanvas');
var videoCtx = videoCanvas.getContext('2d');
var resultsCanvas = document.querySelector('#resultsCanvas');
var resultsCtx = resultsCanvas.getContext('2d');

var videoButton = document.getElementById('toggleVideoButton');
var processingButton = document.getElementById('toggleProcessingButton');
var isVideoPlaying = false;
var isProcessing = false;



stompClient.connect({'session-id': sessionId}, function(frame) {
    document.getElementById('connectionStatus').innerHTML = 'Connected to WebSocket';

    stompClient.subscribe('/topic/messages/'+sessionId, function(message) {
        var data = JSON.parse(message.body);
        var results = data.results;

        if(results.length > 0){
            videoCanvas.style.display = 'block';
            drawResults(results);
        }
        else{
            error_message.style.display = 'block';
            error_message.innerHTML = 'No faces detected in your image. Please try another image.';
        }

        // Clear the flag to indicate that we're done processing the frame
        isProcessingFrame = false;
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

var video = document.getElementById('video');
var isProcessingFrame = false;


setInterval(function() {
    if (isVideoPlaying && isProcessing) {
        if (!isProcessingFrame && isProcessing) {
            error_message.style.display = 'none';
            videoCtx.drawImage(video, 0, 0, videoCanvas.width, videoCanvas.height);
            var dataUrl = videoCanvas.toDataURL('image/png');
            var base64 = dataUrl.split(',')[1];
            stompClient.send("/app/send", {'session-id': sessionId}, base64);
            isProcessingFrame = true;
        }
    }
}, 200);

function generateSessionId() {
    // Generate a random session ID
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

function drawResults(results) {
    // Clear the canvas
    resultsCtx.clearRect(0, 0, resultsCanvas.width, resultsCanvas.height);

    // Draw squares around the faces and put the names on top
    results.forEach(function(result) {
        var coordinates = result[0];
        var info = result[1];
        var full_name = info[1] + " " + info[2];

        resultsCtx.beginPath();
        resultsCtx.rect(coordinates[0], coordinates[1], coordinates[2], coordinates[3]);
        resultsCtx.lineWidth = 3;
        color = info[0].length > 0 ? 'green' : 'gray'
        resultsCtx.strokeStyle = color;
        resultsCtx.fillStyle = color;
        resultsCtx.stroke();

        textSize = toString(parseInt(20))
        resultsCtx.font = textSize+'px Arial';
        resultsCtx.fillText(full_name, coordinates[0], coordinates[1] > 15 ? coordinates[1] - 5 : 15);
    });
}