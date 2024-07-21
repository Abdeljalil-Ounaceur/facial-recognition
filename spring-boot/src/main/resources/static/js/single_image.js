var sessionId = generateSessionId(); // Generate a unique session ID
console.log('Session ID: ' + sessionId);

var socket = new SockJS('http://localhost:8080/ws');
var stompClient = Stomp.over(socket);
var image = document.getElementById('image');
var videoCanvas = document.getElementById('canvas');
videoCanvas.style.display = 'none';
videoCanvas.width = 320;
videoCanvas.height = 240;
var ctx = videoCanvas.getContext('2d');
var error_message = document.getElementById('error-message');
var reserved = new Image();

stompClient.connect({'session-id': sessionId}, function(frame) {
    document.getElementById('connectionStatus').innerHTML = 'Connected to WebSocket';

    stompClient.subscribe('/topic/messages/'+sessionId, function(message) {
        var data = JSON.parse(message.body);
        var results = data.results;
        image.style.display = 'none';

        if(results.length > 0){
            videoCanvas.style.display = 'block';
            drawResults(results);
        }
        else{
            error_message.style.display = 'block';
            error_message.innerHTML = 'No faces detected in your image. Please try another image.';
        }
    });
}, function(error) {
    document.getElementById('connectionStatus').innerHTML = 'Failed to connect to WebSocket';
});

var input = document.getElementById('fileInput');
input.onchange = function() {
    var file = input.files[0];
    var reader = new FileReader();
    reader.onload = function() {
        var dataUrl = reader.result;
        base64Image = dataUrl.split(',')[1];
        image.style.display = 'block';
        image.src = 'media/loading.gif';
        videoCanvas.style.display = 'none';
        error_message.style.display = 'none';
        reserved.src = dataUrl;
        stompClient.send("/app/send", {'session-id': sessionId}, base64Image);
    };
    reader.readAsDataURL(file);
};

function generateSessionId() {
    // Generate a random session ID
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

function drawResults(results) {

    // Clear the canvas
    ctx.clearRect(0, 0, videoCanvas.width, videoCanvas.height);

    // Calculate the scale factor
    var scaleFactorW = videoCanvas.width / reserved.naturalWidth;
    var scaleFactorH = videoCanvas.height / reserved.naturalHeight;
    var scaleFactor = Math.min(scaleFactorW, scaleFactorH);

    var newWidth = parseInt(reserved.naturalWidth * scaleFactor);
    var newHeight = parseInt(reserved.naturalHeight * scaleFactor);
    var image_position_x = parseInt(videoCanvas.width/2) - parseInt(newWidth/2);

    // Draw the image onto the canvas
    ctx.drawImage(reserved, image_position_x, 0, newWidth, newHeight);


    // Draw squares around the faces and put the names on top
    results.forEach(function(result) {
        var coordinates = result[0];
        var info = result[1];
        var full_name = info[1] + " " + info[2];

        // Scale the coordinates
        var scaled_coords = coordinates.map(function(coordinate) {
            return parseInt(coordinate * scaleFactor);
        });

        ctx.beginPath();
        ctx.rect(image_position_x + scaled_coords[0], scaled_coords[1], scaled_coords[2], scaled_coords[3]);
        console.log('scaledCoordinates:', scaled_coords);
        ctx.lineWidth = 3;
        ctx.strokeStyle = 'green';
        ctx.fillStyle = 'green';
        ctx.stroke();

        textSize = toString(parseInt(20*scaleFactor))
        ctx.font = textSize+'px Arial';
        ctx.fillText(full_name, image_position_x + scaled_coords[0], scaled_coords[1] > 15 ? scaled_coords[1] - 5 : 15);
    });
}