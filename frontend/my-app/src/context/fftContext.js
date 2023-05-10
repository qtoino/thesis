import { createContext } from 'react';
import * as Tone from 'tone';

export const FftContext = createContext(new Tone.FFT(512));
