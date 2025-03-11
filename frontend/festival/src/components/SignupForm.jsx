import React from "react";
import { useNavigate } from "react-router-dom";

function SignupForm() {
  const navigate = useNavigate();

  const styles = {
    container: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      backgroundColor: "#8b0000",
    },
    formContainer: {
      backgroundColor: "#fff",
      padding: "40px",
      borderRadius: "8px",
      boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
      width: "350px",
      textAlign: "center",
    },
    heading: {
      marginBottom: "20px",
      fontSize: "24px",
      fontWeight: "bold",
    },
    inputField: {
      width: "100%",
      padding: "15px",
      marginBottom: "15px",
      borderRadius: "4px",
      border: "none",
      backgroundColor: "#d3a6a6",
      color: "#000",
      fontSize: "16px",
    },
    button: {
      width: "100%",
      padding: "12px",
      backgroundColor: "#8b0000",
      color: "#fff",
      borderRadius: "4px",
      border: "none",
      fontSize: "18px",
      cursor: "pointer",
      marginTop: "10px",
    },
    linkText: {
      marginTop: "15px",
      fontSize: "14px",
    },
    loginButton: {
      color: "#8b0000",
      fontWeight: "bold",
      textDecoration: "none",
      cursor: "pointer",
    },
  };

  const handleLoginClick = () => {
    navigate("/login");
  };

  const handleSignupSubmit = (e) => {
    e.preventDefault();
    navigate("/login");
  };

  return (
    <div style={styles.container}>
      <div style={styles.formContainer}>
        <h2 style={styles.heading}>Signup:</h2>
        <form onSubmit={handleSignupSubmit}>
          <input type="text" placeholder="full-name:" style={styles.inputField} required />
          <input type="email" placeholder="email:" style={styles.inputField} required />
          <input type="password" placeholder="password:" style={styles.inputField} required />
          <button type="submit" style={styles.button}>SignUp</button>
        </form>
        <p style={styles.linkText}>
          Already have an account? <span style={styles.loginButton} onClick={handleLoginClick}>Login</span>
        </p>
      </div>
    </div>
  );
}

export default SignupForm;
