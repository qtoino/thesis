import { useState, useEffect, useCallback, useRef} from 'react'
import {getDestination, Player } from "tone"

const useSound = (soundFilePath, fftNode) => {
    const [player, setPlayer] = useState(false)

    const play = useCallback(() => {
        if (player.loaded) {
            player.start()
        }
    }, [player]);

    const stop = useCallback(() => {
        if (player.loaded) {
            player.stop()
        }
    }, [player]);
    
    useEffect(() => {
        const player = new Player(soundFilePath).toDestination()
        setPlayer(player)
        //play()
    }, [soundFilePath])

    useEffect(() => {
      if(player){
        player.connect(fftNode).toDestination()
      }
    }, [player])

    const handleVolumeChange = useCallback((value) => {
        player.volume.value = value;
    }, [player]);
    

    return [play, stop, handleVolumeChange, player]
}

export default useSound
