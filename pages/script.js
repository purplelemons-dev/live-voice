// Check if the browser supports the required APIs
if (!navigator.mediaDevices || !window.MediaRecorder) {
    alert("Your browser does not support the required MediaRecorder API.");
}

let mediaRecorder;
const audioChunks = [];
const script = document.getElementById("script");

// Function to start recording
function startRecording(stream) {
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = async (event) => {
        // When data is available, send it to the server
        if (event.data.size > 0) {
            postDataToServer(await event.data.arrayBuffer());
        }
    };
    mediaRecorder.start(850);
}

// Function to stop recording
document.getElementById("stop").addEventListener("click", () => {
    mediaRecorder.stop();
});

// Function to post data to the server
function postDataToServer(data) {
    fetch("/audiostream", {
        method: "POST",
        body: (data)
    }).then(response => {
        //console.log("Chunk sent to the server", response);
    }).catch(error => {
        console.error("Error sending chunk to server:", error);
    });
}

// Request access to the user's microphone
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        startRecording(stream);
    })
    .catch(error => {
        console.error('Error accessing the microphone:', error);
    });

setTimeout(() => {
    const ev = new EventSource("/stream");
    ev.addEventListener("message", (event) => {
        script.innerText += event.data;
    });
});
