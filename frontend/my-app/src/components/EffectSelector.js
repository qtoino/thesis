import { useState } from 'react';
import * as Tone from 'tone';
import "./EffectSelector.css"

const effectOptions = [
  { label: 'Reverb', effect: new Tone.JCReverb(0.4) },
  { label: 'Chorus', effect: new Tone.Chorus(4, 2.5, 0.5) },
  { label: 'Distortion', effect: new Tone.Distortion(0.8) },
];

function EffectSelector({ setEffect }) {
  const [selectedEffect, setSelectedEffect] = useState(effectOptions[0]);

  function handleEffectChange(event) {
    const index = event.target.value;
    setSelectedEffect(effectOptions[index]);
  }

  function handleAddEffect() {
    setEffect(selectedEffect.effect);
  }

  return (
    <div>
      <select className='form_element select_sequence selector' value={effectOptions.indexOf(selectedEffect)} onChange={handleEffectChange}>
        {effectOptions.map((option, index) => (
          <option key={option.label} value={index}>
            {option.label}
          </option>
        ))}
      </select>
      <button className='form_element' onClick={handleAddEffect}>Add</button>
    </div>
  );
}

export default EffectSelector
            