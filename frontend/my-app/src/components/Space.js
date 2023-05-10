import * as THREE from 'three'
import React, {useState, useEffect, useRef, memo} from 'react'
import { useFrame, Canvas } from '@react-three/fiber'
import { OrbitControls, Stats, CameraControls } from '@react-three/drei';
import { Html } from '@react-three/drei';
import { useControls, button, buttonGroup, folder } from 'leva'
import Ball from './Ball'
import InterpolationLine from './InterpolationLine'
import AddBall from './AddBall'
import FilterButton from './FilterButton'

const { DEG2RAD } = THREE.MathUtils

const Space = ({soundFiles, setSoundFiles, status, data, queryClient}) => {
    console.log("and again")
    const cameraControlsRef = useRef()

    const [balls, setBalls] = useState(null)
    const mapBalls = useRef()
    
    const [ballsSelected, setballsSelected] = useState([])
    
    const allBalls = useRef([])
    
    const classes = useRef(["favorites"])

    useEffect(() => {
      if (status === 'loading'){
        console.log("Loading")
      }
      else if (status === 'error'){
        console.log("error")
      }
      else{
        console.log("reloaded")
        const mappedBalls = data.audio_data.map(function(object){
            if (!object.x) {
              return null; // skip if x is not defined
            }
            allBalls.current = [...allBalls.current, [object.x, object.y, object.z]] // add the position array to allBalls
            // push the color to the classes array only if it hasn't been added already
            if (!classes.current.includes(object.color)) {
              classes.current = [...classes.current, object.color];
            }
            return <Ball position={[object.x, object.y, object.z]} color={object.color} sound={object.name} path={object.path} favorite={object.favorite} soundFiles={soundFiles} setSoundFiles={setSoundFiles} key={object.id} queryClient={queryClient} onClick={handleClick}/>;
        }).filter(Boolean);

        setBalls(mappedBalls);
        mapBalls.current = mappedBalls;
      }
    }, [data]);
    
    async function handleFilter(color) {
      if(color === "favorites"){
        const favBalls = await loadFavSoundFiles()
        console.log(favBalls.audio_data[0][0])
        const filteredBalls = balls.filter(ball => favBalls.audio_data.some(audio => audio[0] === ball.props.sound));

      
        setBalls(filteredBalls);
      }
      else{
        const filteredBalls = balls.filter(ball => ball.props.color === color)
        setBalls(filteredBalls);
      }
    }

    function handleClearFilters() {
      console.log(mapBalls)
      setBalls(mapBalls.current)
    }

    function handleClick(state, position) {

      if(!state){
        if(allBalls.current.some(ball => ball[0] === position[0] && ball[1] === position[1] && ball[2] === position[2])){
          setballsSelected((prevState) => [...prevState, position]);
        }
      }
      else{
        setballsSelected((prevState) =>
          prevState.filter((pos) =>
            pos[0] !== position[0] || pos[1] !== position[1] || pos[2] !== position[2]
          )
        )
      } 
    }

    const { } = useControls({
      thetaGrp: buttonGroup({
        label: 'rotate theta',
        opts: {
          '+45º': () => cameraControlsRef.current?.rotate(45 * DEG2RAD, 0, true),
          '-45º': () => cameraControlsRef.current?.rotate(-45 * DEG2RAD, 0, true),
        }
      }),
      phiGrp: buttonGroup({
        label: 'rotate phi',
        opts: {
          '+45º': () => cameraControlsRef.current?.rotate(0, 45 * DEG2RAD, true),
          '-45º': () => cameraControlsRef.current?.rotate(0, -45 * DEG2RAD, true)
        }
      }),
      truckGrp: buttonGroup({
        label: 'truck',
        opts: {
          '(1,0)': () => cameraControlsRef.current?.truck(1, 0, true),
          '(0,1)': () => cameraControlsRef.current?.truck(0, 1, true),
          '(-1,-1)': () => cameraControlsRef.current?.truck(-1, -1, true)
        }
      }),
      dollyGrp: buttonGroup({
        label: 'dolly',
        opts: {
          '1': () => cameraControlsRef.current?.dolly(1, true),
          '-1': () => cameraControlsRef.current?.dolly(-1, true)
        }
      }),
      moveTo: folder(
        {
          vec1: { value: [0, 0, 0], label: 'vec' },
          'moveTo(…vec)': button((get) => cameraControlsRef.current?.moveTo(...get('moveTo.vec1'), true))
        },
        { collapsed: true }
      ),
      setPosition: folder(
        {
          vec2: { value: [3, 3, 3], label: 'vec' },
          'setPosition(…vec)': button((get) => cameraControlsRef.current?.setPosition(...get('setPosition.vec2'), true))
        },
        { collapsed: true }
      ),
      saveState: button(() => cameraControlsRef.current?.saveState()),
      reset: button(() => cameraControlsRef.current?.reset(true)),
    })
    
    return (
      <>
      <Canvas>
        <ambientLight intensity={0.8} />
        <directionalLight />
        <pointLight position={[20, 20, 20]} />
        <OrbitControls />
        <CameraControls
          ref={cameraControlsRef}
        />
        {balls}
        <InterpolationLine ballsSelected={ballsSelected} allBalls={allBalls} soundFiles={soundFiles} setSoundFiles={setSoundFiles} path={"random"} queryClient={queryClient} handleClick={handleClick}/>
        <Stats />
      </Canvas>
      <AddBall allBalls={allBalls} queryClient={queryClient}/>
      <FilterButton onClick={handleFilter} clearFilters={handleClearFilters} classes={classes.current}/>
      </>
    )
}

export default Space

const loadFavSoundFiles = async () => {
  // Send data to the backend via POST
  const res = await fetch('http://0.0.0.0:8000/favorite-audio-files', {  // Enter your IP address here
      method: 'GET', 
      mode: 'cors',
  })
  const data =  await res.json()
  return data
};
