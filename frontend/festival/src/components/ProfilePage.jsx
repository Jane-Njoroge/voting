import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import axios from 'axios';
import addpro from './addpro.webp';
import pro1 from './pro1.jpg';
import grunge from './grunge.jpg'; 

const ProfilePage = () => {
  const navigate = useNavigate();
  const { candidateId } = useParams();
  const { state } = useLocation();

  const [name, setName] = useState(null);
  const [votes, setVotes] = useState(0);
  const [profileImage, setProfileImage] = useState(null);
  const [category, setCategory] = useState(state?.category || "");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const nameProfileResponse = await axios.get(
          `/get_my_profile`,
          { withCredentials: true }
        );
        setName(nameProfileResponse.data.full_name || "Unknown Name");
        setProfileImage(nameProfileResponse.data.profileImage || null);
        // Get category from API response
        setCategory(nameProfileResponse.data.category || "");
      } catch (error) {
        console.error("Error fetching profile data:", error);
        setName("Error loading name");
      }
    };

    const fetchVotes = async () => {
      try {
        const votesResponse = await axios.get(
          `/candidate/${candidateId}/votes`,
          { withCredentials: true }
        );
        setVotes(votesResponse.data.vote_count || 0);
      } catch (error) {
        console.error("Error fetching vote count:", error);
        setVotes(0);
      }
    };

    if (candidateId !== '0') {
      Promise.all([fetchData(), fetchVotes()])
        .then(() => setIsLoading(false))
        .catch(() => setIsLoading(false));
      const intervalId = setInterval(fetchVotes, 5000);
      return () => clearInterval(intervalId);
    } else {
      setIsLoading(false);
    }
  }, [candidateId, state?.category]); // Add category to dependencies

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('profile_image', file);

    try {
      const response = await axios.post(
        `/upload_profile_image/${candidateId}`,
        formData,
        { withCredentials: true }
      );
      setProfileImage(response.data.profileImage);
    } catch (error) {
      console.error("Error uploading image:", error);
    }
  };

  if (isLoading) {
    return <h2>Loading...</h2>;
  }

  return (
    <div style={{
      ...styles.container,
      backgroundImage: `url(${grunge})`, 
    }}>
      <div style={styles.headerSection}>
        <h2 style={styles.name}>Name: {name}</h2>
        <h3 style={styles.category}>Category: {category || "Not selected"}</h3>
      </div>

      <div style={styles.profileIcon} onClick={() => document.getElementById('fileInput').click()}>
        <img 
          src={profileImage ? `/static/${profileImage}` : addpro} 
          alt="Profile" 
          style={styles.profileImage} 
        />
      </div>

      <input
        type="file"
        id="fileInput"
        accept="image/*"
        onChange={handleImageChange}
        style={{ display: 'none' }}
      />

      <p style={styles.votes}>Votes: {votes}</p>

      <div 
        style={styles.accountIcon} 
        onClick={() => navigate(`/verification-form/${candidateId}`)}
      >
        <img src={pro1} alt="Account" style={styles.accountImage} />
      </div>
    </div>
  );
};

const styles = {
  container: {
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    color: 'white',
    textAlign: 'center',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    padding: '20px'
  },
  headerSection: {
    position: 'absolute',
    top: '20px',
    width: '100%',
    padding: '0 20px'
  },
  name: {
    fontSize: '1.8rem',
    margin: '0 0 10px 0',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    maxWidth: '90vw',
  },
  category: {
    fontSize: '1.4rem',
    margin: 0,
    color: '#ffd700',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    maxWidth: '90vw',
  },
  votes: {
    fontSize: '1.4rem',
    position: 'absolute',
    bottom: '30px',
    left: '30px',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: '10px 20px',
    borderRadius: '5px'
  },
  profileIcon: {
    width: '200px',
    height: '200px',
    borderRadius: '50%',
    border: '4px solid white',
    overflow: 'hidden',
    cursor: 'pointer',
    marginTop: '60px'
  },
  profileImage: {
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  },
  accountIcon: {
    position: 'absolute',
    bottom: '30px',
    right: '30px',
    cursor: 'pointer',
    transition: 'transform 0.3s ease',
    ':hover': {
      transform: 'scale(1.1)'
    }
  },
  accountImage: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    border: '2px solid white'
  }
};

export default ProfilePage;