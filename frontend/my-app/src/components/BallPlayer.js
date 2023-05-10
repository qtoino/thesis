import React, { useState, useEffect, memo } from 'react';
import { Html } from '@react-three/drei'
import BallPlayerCtrl from "./BallPlayerCtrl"
import './BallPlayer.css'

const BallPlayer = ({ audio, path, position, soundFiles, setSoundFiles, play, stop}) => {
	// Statw
    const [isPlaying, setIsPlaying] = useState(true);

    //console.log(soundFiles.current)

	const audioSrc = "./audio/ESC50/" + audio;

    const buttons = [1, 2, 3, 4].map(i => (
        <button className='buttonChannel' onClick={() => handleClick(i)} key={i}>{i}</button>
    ));

    function handleClick(i){
        let sounds = soundFiles
        sounds[i] = audioSrc.slice()
        setSoundFiles(sounds)
    }

    function onPlayPauseClick(state){
        setIsPlaying(state)
    }
    
    useEffect(() => {
        if (isPlaying) {
          play()
        } else {
          stop()
        }
    }, [isPlaying]);

    return (
            <Html
            // 3D-transform contents
            distanceFactor={10}
            // Hide contents "behind" other meshes
            
            position = {position}>
                <div className="audio-player">
                    <div className="track-info">
                        <h2 className="title">{audio}</h2>
                        {buttons}
                        <h2>[{(position[0]-0.7).toFixed(1)} {(position[1]-2).toFixed(1)} {(position[2]-0).toFixed(1)}]</h2>
                    </div>
                    <BallPlayerCtrl isPlaying={isPlaying} onPlayPauseClick={onPlayPauseClick}/>
                </div>
            </Html>
	);
}

export default memo(BallPlayer);

