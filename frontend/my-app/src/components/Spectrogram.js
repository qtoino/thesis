import React, { useState, useEffect, useRef, memo, useContext } from 'react';
import './Spectrogram.css'
import { FftContext } from '../context/fftContext';

const Spectrogram = ({ }) => {
    
    const fftNode = useContext(FftContext)
    const canvasRef = useRef();
    const [ctx, setCtx] = useState()

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return
        setCtx(canvas.getContext("2d", { willReadFrequently: true }))        
    });

    useEffect(() => {
        if (!ctx) return
        const W = 250 
        const H = 150

        ctx.fillStyle = 'hsl(280, 100%, 10%)';
        ctx.fillRect(0, 0, W, H);   
        
        const render = () => {
            const DATA = new Uint8Array(fftNode.getValue());
            const h = H / DATA.length;
            const x = W - 1;
            
            let imgData = ctx.getImageData(1, 0, W - 1, H);
            ctx.putImageData(imgData, 0, 0);

            for (let i = 0; i < DATA.length; i++) {
                let rat = DATA[i] / 255;
                let hue = Math.round((rat * 120) + 280 % 360);
                
                let sat = '100%';
                let lit = 10 + (70 * rat) + '%';
                ctx.beginPath();
                ctx.strokeStyle = `hsl(${hue}, ${sat}, ${lit})`;
                ctx.moveTo(x, H - (i * h));
                ctx.lineTo(x, H - (i * h + h));
                ctx.stroke();
            }
            
            requestAnimationFrame(render);
        };
        render();
    }, [ctx]);

    
    return (
        <canvas ref={canvasRef}/>
	)
};

export default memo(Spectrogram);

