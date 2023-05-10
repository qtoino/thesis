import { useState, useEffect, useCallback } from 'react'
import Sound from '../utils/Sound'


const useSound = (soundFilePath) => {
    const [sound, setSound] = useState({ play: () => { } })
    const play = useCallback((gainValue, rateValue) => sound.play(gainValue, rateValue), [sound])
    
    useEffect(() => {
        setSound(new Sound( soundFilePath))

    }, [soundFilePath])

    return [play]
}

export default useSound


