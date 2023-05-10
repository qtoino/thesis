import { useSpring, animated } from "@react-spring/three"
import React, { useRef, useState, memo, useContext } from 'react'
import * as THREE from 'three';
import BallPlayer from "./BallPlayer"
import BallContextMenu from "./BallContextMenu"
import useSound from '../hooks/useTone'
import { FftContext } from '../context/fftContext';

const Ball = ({position, color, sound, path, favorite, soundFiles, setSoundFiles, queryClient, onClick}) => {

  const fftNode = useContext(FftContext)

  const [showContextMenu, setShowContextMenu] = useState(false);

  const [colorBall, setColorBall] = useState(color);
  if(colorBall != color){
    setColorBall(color)
  }
  
  let ballplayer
  //console.log(position)
  let [x, y, z] = position
  
  const [clickedPosition, setClickedPosition] = useState(null);

  y = parseInt(y) + 2
  x = parseInt(x) + 0.7

  const positionPlayer = [x, y, z]
  
  // This reference gives us direct access to the THREE.Mesh object
  const ref = useRef()
  // Hold state for hovered and clicked events
  const [hovered, setHover] = useState(false)
  const [active, setActivate] = useState(false)

  const {scale,colore} = useSpring({
    scale: active ? [1.3,1.3,1.3] : [1,1,1],
    colore: hovered ? 'hotpink' : colorBall
  })

  const audiodir = path + sound//path+audio
  //console.log(audiodir)

  const [play, stop, handleVolumeChange, player] = useSound(audiodir, fftNode)

  if(active){
    ballplayer = <BallPlayer audio={sound} path={path} position={positionPlayer} soundFiles={soundFiles} setSoundFiles={setSoundFiles} play={play} stop={stop}></BallPlayer>
  } 

  function onClickBall (event) {
    setShowContextMenu(false);
    setActivate(!active)

    onClick(active, position)
  }

  function handleContextMenu (event) {
    setClickedPosition([event.point.x, event.point.y, event.point.z]);
    
    //console.log(clickedPosition)
    setShowContextMenu(!showContextMenu);
  };

  const handleAdd = () => {
    // Handle add event
    addFavorite(sound)
    //write to database
    setShowContextMenu(false);
  };

  const handleUnfav = () => {
    // Handle add event
    unFavorite(sound)
    //write to database
    setShowContextMenu(false);
  };

  const handleRemove = () => {
    // Handle remove event
    setActivate(false)
    onClick(true, position)
    removeBall(sound, queryClient)
    //remove from database
    setShowContextMenu(false);
  };

  const handleDownload = () => {
    // Handle download event
    //request from database
    setShowContextMenu(false);
  };

  // Return the view, these are regular Threejs elements expressed in JSX
  return (
    <>
    <group>
      <animated.mesh
        position={position}
        ref={ref}
        scale={scale}
        onClick={onClickBall}
        onContextMenu={handleContextMenu} // Listen for right-click
        onPointerOver={(e) => setHover(true)}
        onPointerOut={(e) => setHover(false)}>
        <sphereGeometry />
        <animated.meshStandardMaterial color={colore} />
      </animated.mesh>
      {ballplayer}
      {showContextMenu && (
        <BallContextMenu position={clickedPosition} onAdd={handleAdd} onUnfav={handleUnfav} onRemove={handleRemove} onDownload={handleDownload}/>
      )}
    </group>
    
    </>
  )
}

export default Ball

const removeBall = async (filename, queryClient) => {
  // Send data to the backend via POST
  try{
      const res = await fetch('http://0.0.0.0:8000/remove', {  // Enter your IP address here
          method: 'POST', 
          headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
          },
          mode: 'cors',
          body: JSON.stringify({
              filename:filename,
          }),
      })
      const data = await res.json()
      queryClient.invalidateQueries('id', { refetchActive: true })
      return data;
  } catch (e) {
      return e;
  } 
};

const addFavorite = async (filename) => {
  // Send data to the backend via POST
  try{
      const res = await fetch('http://0.0.0.0:8000/favorite', {  // Enter your IP address here
          method: 'POST', 
          headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
          },
          mode: 'cors',
          body: JSON.stringify({
              filename:filename,
          }),
      })
      const data = res.json()
      return data;
  } catch (e) {
      return e;
  } 
};

const unFavorite = async (filename) => {
  // Send data to the backend via POST
  try{
      const res = await fetch('http://0.0.0.0:8000/unfavorite', {  // Enter your IP address here
          method: 'POST', 
          headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
          },
          mode: 'cors',
          body: JSON.stringify({
              filename:filename,
          }),
      })
      const data = res.json()
      return data;
  } catch (e) {
      return e;
  } 
};