import React, { useState, useRef, memo } from 'react'
import useSound from '../hooks/useTone'
import Note from './Note'
import './Track.css'
//import { useAudioContext } from '../hooks/useAudioContext';

const Track = ({
    trackID,
    currentStepID,
    title,
    noteCount,
    onNotes,
    soundFilePath,
    fftNode
}) => {
    //const audioContext = useAudioContext();
    //console.log(soundFilePath)
    const [play, stop, handleVolumeChange] = useSound(soundFilePath, fftNode)

    const rangeAudioRef = useRef(null);
    const [rangeAudio, setRangeAudio] = useState(100);

    const notes = [...Array(noteCount)].map((el, i) => {
        const isNoteOn = onNotes.indexOf(i) !== -1
        const isNoteOnCurrentStep = currentStepID === i
        const stepID = i

        return (
            <Note
                key={i}
                trackID={trackID}
                stepID={stepID}
                isNoteOn={isNoteOn}
                isNoteOnCurrentStep={isNoteOnCurrentStep}
                play={play}
                
            />
        )
    })

    function handleSlider(volume){
        setRangeAudio(volume)
        handleVolumeChange(20 * Math.log10(volume / 100));
    }

    return (
        <div className="track">
            <header className="track_title">{title}</header>
            <main className="track_notes">
                {notes}
            </main>
            <input type="range" orient="vertical" min="0" max="200" value={rangeAudio} ref={rangeAudioRef} onChange={() => handleSlider(rangeAudioRef.current.value)}/>
        </div>
    )
}

export default memo(Track)
