import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function KalenjinMusicFestival() {
  const navigate = useNavigate();

  const containerStyle = {
    backgroundColor: '#B31B1B',
    color: 'white',
    textAlign: 'center',
    height: '90vh',
    width: '55vw',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    fontFamily: 'Arial, sans-serif',
    position: 'relative',
    overflow: 'hidden',
  };

  const titleStyle = {
    fontSize: '4em',
    fontWeight: 'bold',
    marginBottom: '5px',
    letterSpacing: '1px',
  };

  const subtitleStyle = {
    fontSize: '1.5em',
    fontWeight: 'normal',
    opacity: 0.8,
  };

  const arrowContainerStyle = {
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    cursor: 'pointer',
    transition: 'transform 0.3s ease-in-out',
  };

  const arrowStyle = {
    fontSize: '3em',
    color: 'white',
  };

  const [arrowHovered, setArrowHovered] = useState(false);

  const handleArrowClick = () => {
    navigate('/signup'); 
  };

  const arrowTransform = arrowHovered ? 'translateX(5px)' : 'translateX(0)';

  return (
    <div style={containerStyle}>
      <h1 style={titleStyle}>
        <span style={{ color: '#FFDA63' }}>&#9835;</span> Kalenjin
      </h1>
      <p style={subtitleStyle}>Music Festivals</p>

      <div
        style={{
          ...arrowContainerStyle,
          transform: arrowTransform,
        }}
        onClick={handleArrowClick}
        onMouseEnter={() => setArrowHovered(true)}
        onMouseLeave={() => setArrowHovered(false)}
      >
        <span style={arrowStyle}>&rarr;</span>
      </div>
    </div>
  );
}

export default KalenjinMusicFestival;