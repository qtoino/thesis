import React, { useState, createContext } from 'react';

const AudioContext = createContext(null);

const AudioContextProvider = ({ children }) => {
  const [audioContext] = useState(() => new (window.AudioContext || window.webkitAudioContext || window.MozAudioContext)());

  return (
    <AudioContext.Provider value={audioContext}>
      {children}
    </AudioContext.Provider>
  );
};

export { AudioContextProvider, AudioContext };

