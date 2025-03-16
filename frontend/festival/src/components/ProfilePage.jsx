import React ,{ useState, useEffect } from "react";
import { useNavigate,useParams } from "react-router-dom";
import addpro from './addpro.webp'
import pro1 from './pro1.jpg'

const ProfilePage = () => {
  const navigate = useNavigate();
  const { candidateId } = useParams();
  const [name, setName] = useState(null);
  const [votes, setVotes] = useState(0);
  const [profileImage, setProfileImage] = useState(null);
  const [candidate, setCandidate] = useState({});
  const [categories, setCategories] = useState([]);

  useEffect(() => {

    if (!candidateId) {
      console.error("Candidate ID is missing!");
      return;
    }


    fetch(`http://localhost:5000/get_name_profile_image/${candidateId}`, { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      console.log("Candidate Data:", data);
      if (!data.error){
        setName(data.full_name);
        setProfileImage(data.profileImage);
      }
    })
    .catch((error) => console.error("Error fetching candidate details:", error));
  


  fetch(`http://localhost:5000/fetch_category/${candidateId}`, { credentials: "include" })
  .then(response => response.json())
  .then(data => {
    console.log("Category Data:", data);
    if (data.candidate && data.categories) {
      setCandidate(data.candidate);
      setCategories(data.categories);
    }
  })
  
  .catch((error) => console.error("Error fetching category:", error));

}, [candidateId]);
 


  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("profile_image", file);
    try{
      const response = await fetch("http://localhost:5000/upload_profile_image",{
        method: "POST",
        body :formData,
        credentials: "include",
      });
      const data = await response.json();
      setProfileImage(data.profileImage);
    } catch (error) {
      console.error("Error uploading image:",error);
    }
    
  };



  return (
    <div style={styles.container}>

{candidate.name && <h2 style={styles.name}>Name: {candidate.name}</h2>}

      
      {categories.length > 0 && <h3>Category: {categories[0]}</h3>}

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
        onClick={() => navigate("/verification-form")}
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
      marginTop:'20%',
      marginLeft:'40%',

      position: "absolute",
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",


      "@media (maxWidth: 168px)": {
        width: "60px",
        height: "60px",
        left: "50%",
        top: "40%",
      }
    },

    
  };
  

export default ProfilePage;
