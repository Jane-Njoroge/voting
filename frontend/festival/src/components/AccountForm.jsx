import { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import addpro from './addpro.webp';
import pro1 from './pro1.jpg';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { candidateId } = useParams();  // Get ID from URL
  const location = useLocation();
  const selectedCategory = location.state?.category || "No category selected";  // Keep category from location
  const [name, setName] = useState("");
  const [votes, setVotes] = useState(0);
  const [profileImage, setProfileImage] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Fetch candidate data
        const response = await fetch(`http://127.0.0.1:5000/candidates/${candidateId}`, {
          method: "GET",
          credentials: "include",
        });
        if (!response.ok) throw new Error("Failed to fetch candidate data");
        const data = await response.json();
        console.log("Candidate data:", data);
        setName(data.full_name);

        // Fetch verification data for votes and image
        const verificationResponse = await fetch(`http://127.0.0.1:5000/get_single_verification/${candidateId}`, {
          method: "GET",
          credentials: "include",
        });
        if (verificationResponse.ok) {
          const verificationData = await verificationResponse.json();
          console.log("Verification data:", verificationData);
          setVotes(verificationData.vote_count || 0);
          setProfileImage(verificationData.profile_image || addpro);
        } else {
          console.warn("No verification data found, using defaults");
          setVotes(0);
          setProfileImage(addpro);
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
      }
    };
    fetchProfile();
  }, [candidateId]);

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("profile_image", file);
    formData.append("candidate_id", candidateId);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload_profile_image", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to upload image");
      const data = await response.json();
      console.log("Image upload response:", data);
      setProfileImage(data.image_url);
    } catch (error) {
      console.error("Error uploading image:", error);
    }
  };

  return (
    <div style={styles.container}>
      <p>Selected Category: {selectedCategory}</p>
      <h2 style={styles.name}>Name: {name}</h2>
      
      <div style={styles.profileIcon} onClick={() => document.getElementById("fileInput").click()}>
        <img 
          src={profileImage || addpro} 
          alt="addpro" 
          style={styles.profileImage}
        />
      </div>
      <input
        type="file"
        id="fileInput"
        accept="image/*"
        onChange={handleImageChange}
        style={{ display: "none" }}
      />

      <p style={styles.votes}>Votes: {votes}</p>
      
      <div 
        style={styles.profileIcon}
        onClick={() => navigate("/verification-form")}  // Adjust this route as needed
      >
        <img 
          src={pro1} 
          alt="pro1"
          style={styles.accountImage}
        />
      </div>
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: "#5c0e0e",
    color: "white",
    textAlign: "center",
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  name: {
    fontSize: "1.5rem",
    marginBottom: "10px",
    position: "absolute",
    top: "20px",
  },
  votes: {
    fontSize: "1.2rem",
    position: "absolute",
    bottom: "20px",
    left: "20px",
  },
  profileIcon: {
    width: "150px",
    height: "150px",
    backgroundColor: "transparent",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  profileImage: {
    width: "100%",
    height: "100%",
    borderRadius: "50%",
  },
  accountIcon: {
    position: "absolute",
    bottom: "20px",
    right: "20px",
    width: "50px",
    height: "50px",
    cursor: "pointer",
  },
  accountImage: {
    width: "80px",
    height: "80px",
    borderRadius: "50%",
    marginTop: '20%',
    marginLeft: '40%',
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    "@media (max-width: 168px)": {
      width: "60px",
      height: "60px",
      left: "50%",
      top: "40%",
    }
  },
};

export default ProfilePage;