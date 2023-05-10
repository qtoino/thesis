import React, { useContext, memo } from 'react'
import { Context } from '../hooks/useStore'
import Track from './Track'

const TrackList = ({ currentStepID, soundFiles, fftNode}) => {
    
    const { sequence: { trackList, noteCount } } = useContext(Context)
    const content = trackList.map((track, trackID) => {
        const {onNotes, soundFile } = track
        const soundFilePath = soundFiles[soundFile]
        let title = soundFilePath
        title = title.split("/").pop().split(".")[0]


        return (
            <Track
                key={trackID}
                trackID={+trackID}
                currentStepID={currentStepID}
                title={title}
                noteCount={noteCount}
                onNotes={onNotes}
                soundFilePath={soundFilePath}
                fftNode={fftNode}
            />
        )
    })

    return (
        <div className="track-list">
            {content}
        </div>
    )
}

export default memo(TrackList)

