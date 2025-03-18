import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from 'axios';

function SignupForm() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        full_name: "",
        email: "",
        password: "",
    });
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
 
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

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
};

const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
        const response = await axios.post("/signup", formData, {
            headers: {
                "Content-Type": "application/json",
            },
        });
        
        // Store the JWT token in local storage upon successful signup
        const token = response.data.token;
        if (token) {
            localStorage.setItem('token', token);
        }

        alert(response.data.message);
        navigate("/login");
    } catch (error) {
        setLoading(false);
        setErrorMessage(error.response?.data?.error || "Signup failed. Try again!");
    } finally {
        setLoading(false);
    }
};

return (
    <div style={styles.container}>
        <div style={styles.formContainer}>
            <h2 style={styles.heading}>Signup:</h2>
            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
            <form onSubmit={handleSignupSubmit}>
                <input type="text" name="full_name" placeholder="Full Name:" style={styles.inputField} value={formData.full_name} onChange={handleInputChange} required />
                <input type="email" name="email" placeholder="Email:" style={styles.inputField} value={formData.email} onChange={handleInputChange} required />
                <input type="password" name="password" placeholder="Password:" style={styles.inputField} value={formData.password} onChange={handleInputChange} required />
                <button type="submit" style={styles.button} disabled={loading}>
                    {loading ? "Signing up..." : "SignUp"}
                </button>
            </form>
            <p style={styles.linkText}>
                Already have an account? <span style={styles.loginButton} onClick={() => navigate("/login")}>Login</span>
            </p>
        </div>
    </div>
);
}

export default SignupForm;
