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
          `/get_my_profile/${candidateId}`,
          { withCredentials: true }
        );
        setName(nameProfileResponse.data.full_name || "Unknown Name");
        setProfileImage(nameProfileResponse.data.profileImage || null);
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
  }, [candidateId]);

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
      // Update the profile image state here
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
      // backgroundColor: 'maroon' 
    }}>
      <h2 style={styles.name}>Name: {name}</h2>
      {category && <h3 style={styles.category}>Category: {category}</h3>}
      <div style={styles.profileIcon} onClick={() => document.getElementById('fileInput').click()}>
        <img src={profileImage ? `/static/${profileImage}` : addpro} alt="Profile" style={styles.profileImage} />
      </div>
      <input
        type="file"
        id="fileInput"
        accept="image/*"
        onChange={handleImageChange}
        style={{ display: 'none' }}
      />
      <p style={styles.votes}>Votes: {votes}</p>
      <div style={styles.profileIcon} onClick={() => navigate(`/verification-form/${candidateId}`)}>
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
    position: 'relative'
  },
  name: {
    fontSize: '1.5rem',
    marginBottom: '10px',
    position: 'absolute',
    top: '20px'
  },
  category: {
    fontSize: '1.2rem',
    marginBottom: '20px',
    position: 'absolute',
    top: '60px'
  },
  votes: {
    fontSize: '1.2rem',
    position: 'absolute',
    bottom: '20px',
    left: '20px'
  },
  profileIcon: {
    width: '150px',
    height: '150px',
    backgroundColor: 'transparent',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  profileImage: {
    width: '100%',
    height: '100%',
    borderRadius: '50%'
  },
  accountImage: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    cursor: 'pointer'
  }
};

export default ProfilePage;
