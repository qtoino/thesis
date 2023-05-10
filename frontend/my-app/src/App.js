import React, { useState, useEffect, useRef, useContext } from 'react'
import { useQuery, useQueryClient } from 'react-query';
import ToolBar from './components/Toolbar'
import TrackList from './components/TrackList'
import PlayHead from './components/PlayHead'
import Spectrogram from './components/Spectrogram'
import { Provider } from './hooks/useStore'
import useTimer from './hooks/useTimer'
import useStyles from './hooks/useStyles'
import {FftContext} from './context/fftContext'
import './App.css';

import Space from './components/Space'

function App() {

  const baseBPMPerOneSecond = 60
  const stepsPerBar = 16
  const beatsPerBar = 4
  const barsPerSequence = 1
  const totalSteps = stepsPerBar * barsPerSequence
  const totalBeats = beatsPerBar * barsPerSequence

  const [BPM, setBPM] = useState(128)
  const [startTime, setStartTime] = useState(null)
  const [pastLapsedTime, setPastLapse] = useState(0)
  const [currentStepID, setCurrentStep] = useState(null)
  const [getNotesAreaWidthInPixels] = useStyles(totalSteps)
  const [showTrack, setShowTrack] = useState(true);

  const notesAreaWidthInPixels = getNotesAreaWidthInPixels(totalSteps)
  const timePerSequence = baseBPMPerOneSecond / BPM * 1000 * totalBeats
  const timePerStep = timePerSequence / totalSteps
  const isSequencePlaying = startTime !== null
  const playerTime = useTimer(isSequencePlaying)
  const lapsedTime = isSequencePlaying ? Math.max(0, playerTime - startTime) : 0
  const totalLapsedTime = pastLapsedTime + lapsedTime

  const [soundFiles, setSoundFiles] = useState({
    '1': './audio/kick.wav',
    '2': './audio/snare.wav',
    '3': './audio/hh_open.wav',
    '4': './audio/hh_closed.wav'
  });

  const fftNode = useContext(FftContext)

  const queryClient = useQueryClient()
    //read from database
  const {data, status} = useQuery('id', loadSoundFiles)
  
  useEffect(() => {
      if (isSequencePlaying) {
          setCurrentStep(Math.floor(totalLapsedTime / timePerStep) % totalSteps)
      } else {
          setCurrentStep(null)
      }
  }, [isSequencePlaying, timePerStep, totalLapsedTime, totalSteps])

  const toolBarProps = {
      setStartTime,
      setPastLapse,
      setBPM,
      isSequencePlaying,
      startTime,
      BPM
  }

  const playHeadProps = {
      notesAreaWidthInPixels,
      timePerSequence,
      totalLapsedTime
  }

  const trackListProps = {
      currentStepID,
      soundFiles,
      fftNode
  }

  const spaceProps = {
      soundFiles,
      setSoundFiles,
      status,
      data,
      queryClient
  }

  return (
    
    <FftContext.Provider value={fftNode}>
      <Provider>
          <div id = "wrapper">
            <div className="space">
                <Space {...spaceProps} />
            </div>
            <main className="app track">
            
                <Spectrogram />
                <div className="app_content">
                    <PlayHead {...playHeadProps} />
                    <TrackList {...trackListProps} />
                </div>
                <div className="app_controls">
                    <ToolBar {...toolBarProps} />
                </div>
                    
            </main >
          </div>
      </Provider>
    </FftContext.Provider>
  )
}

export default App

const loadSoundFiles = async () => {
    // Send data to the backend via POST
    const res = await fetch('http://0.0.0.0:8000/all-audio-files', {  // Enter your IP address here
        method: 'GET', 
        mode: 'cors',
    })
    return res.json()
};
  