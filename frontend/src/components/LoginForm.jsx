import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const LoginForm = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const checkSession = async () => {
            try {
              const token = localStorage.getItem("token");
              console.log("Token from localStorage:", token);

              if(!token){
                console.log("No token found. User not logged in.");
                return;
              }
                const response = await axios.post("http://127.0.0.1:5000/check-session",{
                  withCredentials: true,
                  headers: { 
                    "Authorization": `Bearer ${token}` 
                  }
                  
                });
                console.log("Session Response:", response.data);

                if (response.data.user_id) {
                    console.log("User is already logged in with ID:", response.data.user_id);
                    navigate("/scrollable-cards");
                } 
            } catch (error) {
                console.error("Error checking session:", error.message);
            }
        };

        checkSession();
    }, [navigate]);
  const styles = {
    container: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      backgroundColor: "#8b0000",
    },
    form: {
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
    signupButton: {
      color: "#8b0000",
      fontWeight: "bold",
      textDecoration: "none",
      cursor: "pointer",
    },
  };

  const validate = () => {
    let isValid = true;
    if (!email) {
      setEmailError("Please enter your email");
      isValid = false;
    } else {
      setEmailError("");
    }
    if (!password) {
      setPasswordError("Please enter your password");
      isValid = false;
    } else {
      setPasswordError("");
    }
    return isValid;
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
  
    try {
      const response = await axios.post("/login", 
        { email, password }, 
        { withCredentials: true }
      );
  
      const { token, user } = response.data;
      if (!token) throw new Error("No token received from server");
  
      localStorage.setItem("token", token);
      localStorage.setItem("candidateEmail", email);
      sessionStorage.setItem("candidate_id", user.id);
      console.log("Login response:", response.data);
      console.log("Stored candidate_id:", user.id);
  
      navigate("/scrollable-cards", { state: { candidateId: user.id } }); // Pass candidateId via state
      alert("Login successful!");
    } catch (error) {
      console.error("Login Error:", error);
      alert(error.response?.data?.error || "Login failed. Please check your credentials!");
    }
  };
  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   if (!validate()) return;
  
  //   try {
  //     const response = await axios.post("/login", 
  //       { email, password }, 
  //       { withCredentials: true }
  //     );
  
  //     const { token, user } = response.data; // Destructure token and user
  //     if (!token) throw new Error("No token received from server");
  
  //     localStorage.setItem("token", token);
  //     localStorage.setItem("candidateEmail", email); // Keep this if you need email later
  //     sessionStorage.setItem("candidate_id", user.id); // Store candidate_id
  //     console.log("Login response:", response.data); // Debug response
  //     console.log("Stored candidate_id:", user.id); // Debug storage
  
  //     navigate("/scrollable-cards"); // Keep your route name
  //     alert("Login successful!");
  //   } catch (error) {
  //     console.error("Login Error:", error);
  //     alert(error.response?.data?.error || "Login failed. Please check your credentials!");
  //   }
  // };

  return (
    <div style={styles.container}>
      <form style={styles.form} onSubmit={handleSubmit}>
        <h2 style={styles.heading}>Login</h2>
        <div>
          <input
            type="email"
            placeholder="Email"
            style={styles.inputField}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {emailError && <div style={{ color: "red" }}>{emailError}</div>}
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            style={styles.inputField}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {passwordError && <div style={{ color: "red" }}>{passwordError}</div>}
        </div>
        <button type="submit" style={styles.button}>
          Login
        </button>
        <p style={styles.linkText}>
          Don't have an account?{" "}
          <span style={styles.signupButton} onClick={() => navigate("/signup")}>
            Signup
          </span>
        </p>
      </form>
    </div>
  );
};

export default LoginForm;