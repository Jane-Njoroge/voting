import React from "react";
import { useNavigate } from "react-router-dom";

const SignupForm = () => {
  const navigate = useNavigate();

  const styles = {
    container: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "60vh",
      backgroundColor: "#f9f9f9",
    },
    form: {
      backgroundColor: "#fff",
      padding: "20px",
      borderRadius: "8px",
      boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
      width: "300px",
      textAlign: "center",
    },
    heading: {
      marginBottom: "20px",
    },
    inputField: {
      width: "100%",
      padding: "10px",
      marginBottom: "15px",
      borderRadius: "4px",
      border: "none",
      backgroundColor: "#e3c5c5",
      color: "#000",
    },
    button: {
      width: "100%",
      padding: "10px",
      backgroundColor: "#8b0000",
      color: "#fff",
      borderRadius: "4px",
      border: "none",
      cursor: "pointer",
    },
    buttonHover: {
      backgroundColor: "#a30000",
    },
    loginButton: {  // Style for the Login Button
      backgroundColor: "transparent", // No background color
      border: "none",               // No border
      color: "#8b0000",             // Dark red color
      cursor: "pointer",            // Change cursor to pointer
      textDecoration: "underline",  // Add underline
      fontSize: "inherit",          // Inherit font size
      fontFamily: "inherit",        // Inherit font family
    },
    loginButtonHover: {
      color: "#a30000",
    },
    linkText: {
      marginTop: "10px",
      textAlign: "center", // Center the content
    },
    linkAnchor: {
      color: "#8b0000",
    },
  };

  const handleLoginClick = () => {
    navigate("/login");  // Function to navigate when Login is clicked
  };

  const handleSignupSubmit = (e) => {
    e.preventDefault();  // Prevent default form submission
    // Add signup logic here (e.g., API call)

    // After successful signup (or immediately for this example), navigate to login
    navigate("/login");
  };

  return (
    <div style={styles.container}>
      <form style={styles.form} onSubmit={handleSignupSubmit}>  {/* Add onSubmit handler to the form */}
        <h2 style={styles.heading}>Signup</h2>
        <input
          type="text"
          placeholder="Full name"
          style={styles.inputField}
          required
        />
        <input
          type="email"
          placeholder="Email"
          style={styles.inputField}
          required
        />
        <input
          type="password"
          placeholder="Password"
          style={styles.inputField}
          required
        />
        <button
          type="submit"
          style={styles.button}
          onMouseOver={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
          onMouseOut={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
        >
          Signup
        </button>
        <p style={styles.linkText}>
          Already have an account?{" "}
          <button
            style={styles.loginButton}
            onClick={handleLoginClick}  // Call handleLoginClick on press
            onMouseOver={(e) => (e.target.style.color = styles.loginButtonHover.color)}
          >
            Login
          </button>
        </p>
      </form>
    </div>
  );
};

export default SignupForm;
