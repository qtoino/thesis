import React, {memo, useState, useRef} from 'react';
import { Line } from '@react-three/drei';
import * as THREE from 'three';
import Ball from './Ball'

const InterpolationLine = ({ ballsSelected, allBalls, soundFiles, setSoundFiles, path, queryClient, handleClick}) => {
    
    const [newBallPosition, setNewBallPosition] = useState(null);
    const [sound, setSound] = useState("null");
    const [color, setColor] = useState("black")

    const radius = 1.4

    function onClick (event) {

        const clickedPosition = [event.point.x, event.point.y, event.point.z];
        
        const distances = allBalls.current.map(p => event.point.distanceTo(new THREE.Vector3(...p)));
        const closestIndex = distances.indexOf(Math.min(...distances));
        const closestDistance = distances[closestIndex];
        
        // Check if the closest ball is in front of the line
        if (closestDistance < radius) {
            console.log('Ball is in front of line, not creating new ball');
            return;
        }
        else {
            if(newBallPosition){
                if(clickedPosition[0] < newBallPosition[0] - radius ||
                    clickedPosition[0] > newBallPosition[0] + radius ||
                    clickedPosition[1] < newBallPosition[1] - radius ||
                    clickedPosition[1] > newBallPosition[1] + radius ||
                    clickedPosition[2] < newBallPosition[2] - radius ||
                    clickedPosition[2] > newBallPosition[2] + radius){
                    setSound("null")
                    setColor("black")
                    const data = generateNewSound(clickedPosition, queryClient)
                    console.log(data)
                    setNewBallPosition(clickedPosition);
                }
                console.log(sound)
            }
            else{
                setSound("null")
                setColor("black")
                const data = generateNewSound(clickedPosition, queryClient)
                console.log(data)
                setNewBallPosition(clickedPosition);
                
            }

        }
        
    }
    
    const ball_inter = newBallPosition ? (
        <Ball
            position={newBallPosition}
            color={color}
            sound={sound}
            path={path}
            soundFiles={soundFiles}
            setSoundFiles={setSoundFiles}
            queryClient={queryClient} 
            onClick={handleClick}
        />
    ) : null;
    
  return (
    <>
        {ballsSelected.length >= 2 && <Line
            points={ballsSelected.map(p => new THREE.Vector3(...p))}
            color="burlywood"
            lineWidth={100}
            onClick={onClick}
            transparent={true}
        />}
        {ball_inter}
    </>
  );
};

export default memo(InterpolationLine);

const generateNewSound = async (clickedPosition, queryClient) => {
    // Send data to the backend via POST
    try{
        const res = await fetch('http://0.0.0.0:8000/addnew', {  // Enter your IP address here
            method: 'POST', 
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            body: JSON.stringify({
                x:clickedPosition[0],
                y:clickedPosition[1],
                z:clickedPosition[2]
            }),
        })
        const data = await res.json();
        queryClient.invalidateQueries('id', { refetchActive: true })
        return data;
    } catch (e) {
        return e;
    } 
};
  