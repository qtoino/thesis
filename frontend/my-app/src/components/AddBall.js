import React, { useState, memo } from "react";
import * as THREE from 'three';
import Ball from './Ball'
import "./AddBall.css"

function AddBall({allBalls, queryClient}) {
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [z, setZ] = useState(0);

  function handleXChange(event) {
    setX(parseFloat(event.target.value));
  }

  function handleYChange(event) {
    setY(parseFloat(event.target.value));
  }

  function handleZChange(event) {
    setZ(parseFloat(event.target.value));
  }

  function handleAddBall(){

    const radius = 1.4

    const point = new THREE.Vector3(...[x, y, z])
    const newPosition = [x, y, z];
    
    const distances = allBalls.current.map(p => point.distanceTo(new THREE.Vector3(...p)));
    const closestIndex = distances.indexOf(Math.min(...distances));
    const closestDistance = distances[closestIndex];
    
    // Check if the closest ball is in front of the line
    if (closestDistance < radius) {
        console.log('Ball is in front of line, not creating new ball');
        return;
    }
    else {
        const data = generateNewSound(newPosition, queryClient)
        console.log(data)
    }
  }

  return (
    <>
        <div className="coordinates">
          <div className="inputs">
            <input type="number" id="x" name="x" step="any" value={x} onChange={handleXChange} required />

            <input type="number" id="y" name="y" step="any" value={y} onChange={handleYChange} required />

            <input type="number" id="z" name="z" step="any" value={z} onChange={handleZChange} required />
          </div>  
          <button className="buttonAdd" onClick={handleAddBall}>Add</button>
        </div>
    </>
  );
}

export default memo(AddBall);

const generateNewSound = async (newPosition, queryClient) => {
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
              x:newPosition[0],
              y:newPosition[1],
              z:newPosition[2]
          }),
      })
      const data = await res.json();
      queryClient.invalidateQueries('id', { refetchActive: true })
      return data;
  } catch (e) {
      return e;
  } 
};
