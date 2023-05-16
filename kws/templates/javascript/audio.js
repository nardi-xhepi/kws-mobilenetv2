let mediaRecorder;
let chunks = [];
const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const BASE_URL = "http://127.0.0.1:8000";

startBtn.addEventListener("click", () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            startBtn.style.display = "none";
            stopBtn.style.display = "block";
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                chunks.push(event.data);
                }
            };

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
                    .then(data => console.log(data))
                    .catch(error => console.error(error));
            };

            mediaRecorder.start();
    });
});

stopBtn.addEventListener("click", () => {
    startBtn.style.display = "block";
    stopBtn.style.display = "none";
    mediaRecorder.stop();
});