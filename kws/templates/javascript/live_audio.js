let socket = new WebSocket('ws://127.0.0.1:8000/ws/audio_processing/');

// Button elements
let startButton = document.getElementById('startButton');
let stopButton = document.getElementById('stopButton');

// Initially, only Start button is enabled
stopButton.disabled = true;

// Connection opened
socket.addEventListener('open', (event) => {
    console.log("WebSocket is open now.");
    startButton.disabled = false;
    stopButton.style.display = "none";
});

// Button listeners
startButton.addEventListener('click', () => {
    startRecording();
    // After starting recording, disable Start button and enable Stop button
    startButton.disabled = true;
    stopButton.disabled = false;
    stopButton.style.display = "block";
    startButton.style.display = "none";
});

stopButton.addEventListener('click', () => {
    stopRecording();
    // After stopping recording, enable Start button and disable Stop button
    startButton.disabled = false;
    stopButton.disabled = true;
    stopButton.style.display = "none";
    startButton.style.display = "block";
});


// Listen for messages
socket.addEventListener('message', (event) => {
    let data = JSON.parse(event.data);
    console.log('Prediction from server: ', data.prediction);
    document.getElementById('result').innerText = data.prediction; // Display the prediction in the results div
});

// Connection closed
socket.addEventListener('close', (event) => {
    console.log("WebSocket is closed now.");
});

// Connection error
socket.addEventListener('error', (event) => {
    console.log("WebSocket error: ", event);
});


function startRecording() {
    // Record audio data from the microphone
    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
    .then(function(stream) {
        const options = {mimeType: 'audio/webm'};
        mediaRecord = new MediaRecorder(stream, options);
        mediaRecord.start(2000); // timeslice parameter is set to 2000 milliseconds

        // When enough audio data has been recorded, send it to the server
        mediaRecord.ondataavailable = function(event) {
            let reader = new FileReader();
            reader.onloadend = () => {
                if (reader.readyState == FileReader.DONE) {
                    socket.send(reader.result);
                }
            };
            reader.readAsArrayBuffer(event.data);
        };
    })
    .catch(function(err) {
        console.log('MediaDevices.getUserMedia error: ', err);
    });
}


function stopRecording() {
    if (mediaRecord) {
        mediaRecord.stop();
    }
}

