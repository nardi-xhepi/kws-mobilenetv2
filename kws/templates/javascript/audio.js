let mediaRecorder;
let chunks = [];
const startBtn = document.getElementById("start");
const download = document.getElementById("download");
const downloading = document.getElementById("downloading");
const timer = document.getElementById("stop");
const BASE_URL = "http://127.0.0.1:8000";

function updateTimer() {
    timer.textContent = `${timeout} secondes ...`;
}


let timeout = 30;

updateTimer();

startBtn.addEventListener("click", () => {
    startBtn.disabled = true;

    const timerInterval = setInterval(function() {

        timeout--;

        if (timeout <= 0) {
            startBtn.style.display = 'block';
            clearInterval(timerInterval);
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                startBtn.disabled = false;
                timeout = 30;
                mediaRecorder.stop();
            }
        }else{
            updateTimer();
        }
      }, 1000);

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            timer.style.display = "block";
            startBtn.style.display = "none";
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunks.push(event.data);
                }
            };

            timeout--;
            updateTimer();

            mediaRecorder.onstop = () => {
                const blob = new Blob(chunks, { type: "audio/wav; codecs=0" });
                const formData = new FormData();
                formData.append('audio', blob, 'audio.wav');

                chunks = [];

                fetch(BASE_URL + '/kws/sendAudio', {
                    method: 'POST',
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    let task_id = data.task_id;
                    downloading.style.display = "block";

                    let interval = setInterval(() => {

                        fetch(BASE_URL + '/kws/checkTaskStatus?task_id=' + task_id)
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'complete') {
                                clearInterval(interval);
                                // fetch the model file
                                fetchModelFile();
                            }
                        });
                    }, 5000); // poll every 5 seconds
                })
                .catch(error => console.error(error));
            
                timer.style.display = "none";
                startBtn.style.display = "block";
            };

            mediaRecorder.start();
    });
});


function fetchModelFile() {
    fetch(BASE_URL + '/kws/sendFile')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            // Create an object URL for the blob
            var url = URL.createObjectURL(blob);
            // Create a new anchor element
            var a = document.createElement('a');
            a.href = url;
            a.download = 'model.h5';
            download.style.display = "block";
            downloading.style.display = "none";
            download.addEventListener('click', () => {
                a.click(); // This will download the trained model file automatically
            });
        })
        .catch(error => console.error(error));
}




