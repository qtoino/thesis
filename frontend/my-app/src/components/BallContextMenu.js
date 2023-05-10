import React from 'react';
import { Html } from '@react-three/drei';
import { ReactComponent as AddIcon } from '../assets/add.svg';
import { ReactComponent as MinusIcon } from '../assets/minus.svg';
import { ReactComponent as RemoveIcon } from '../assets/delete.svg';
import { ReactComponent as DownloadIcon } from '../assets/download.svg';
import './BallContextMenu.css'

const BallContextMenu = ({ position, onAdd, onUnfav, onRemove, onDownload }) => {
  
  const iconStyle = {
    width: '20px',
    height: '20px',
    marginRight: '10px',
  };

  const minusiconStyle = {
    width: '17px',
    height: '17px',
  };
  
  //const divProps = {
  //  className: 'ball-info'
  //}

  return (
    <Html position = {position}>
        <div className='ball-info'>
        <button className='button add' onClick={onAdd}>
            <AddIcon style={iconStyle} />
            Favorite
        </button>
        <button className='button add' onClick={onUnfav}>
            <MinusIcon style={minusiconStyle} />
        </button>
        <button className='button remove' onClick={onRemove}>
            <RemoveIcon style={iconStyle} />
            Remove
        </button>
        <button className='button download' onClick={onDownload}>
            <DownloadIcon style={iconStyle} />
            Download
        </button>
        </div>
    </Html>
  );
};

export default BallContextMenu;
