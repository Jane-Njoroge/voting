import { useNavigate } from "react-router-dom";
import addpro from './addpro.webp'
import pro1 from './pro1.jpg'

const ProfilePage = ({ name, votes }) => {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <h2 style={styles.name}>Name: {name}</h2>
     
     <div style={styles.profileIcon}>
      <img 
      src={addpro} 
      alt="addpro" 
      style={styles.profileImage}
       />
       </div>


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
      backgroundColor: "#5c0e0e", // Dark red background
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


      "@media (max-width: 168px)": {
        width: "60px",
        height: "60px",
        left: "50%",
        top: "40%",
      }
    },

    
  };
  

export default ProfilePage;
