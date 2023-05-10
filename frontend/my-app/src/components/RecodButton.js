import React, { useState } from "react";
import { ReactComponent as MicIcon } from '../assets/microphone.svg';
import "./RecordButton.css"

function RecordButton() {

  const iconStyle = {
    width: '20px',
    height: '20px',
  };

  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.addEventListener("dataavailable", (event) => {
      setAudioChunks((chunks) => [...chunks, event.data]);
    });
    mediaRecorder.start();
    setMediaRecorder(mediaRecorder);
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.stop();
    setRecording(false);
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });

    // Get the audio data from the first 4 seconds
    const audioStart = 0;
    const audioEnd = Math.min(4, audioBlob.size);
    const audioBlob4s = audioBlob.slice(audioStart, audioEnd, { type: "audio/wav" });

    const audioFile = new File([audioBlob4s], "my-recording.wav", {type: "audio/wav"});
    console.log(audioFile); // Do whatever you want with the audio URL
    setAudioChunks([]);
    //write to database

    fetch('http://0.0.0.0:8000/input', {  // Enter your IP address here
        method: 'POST', 
        mode: 'cors',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            audio: "my-recording.wav"
        }),
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
  };

  return (
    <div>
      {recording ? (
        <button className={"record-button recording"} onClick={stopRecording}>
            <MicIcon style={iconStyle}/>
        </button>
      ) : (
        <button className={"record-button"} onClick={startRecording}>
            <MicIcon style={iconStyle}/>
        </button>
      )}
    </div>
  );
}

export default RecordButton;