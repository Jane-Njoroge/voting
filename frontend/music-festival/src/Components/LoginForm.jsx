import React, { useState } from "react";

const LoginForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");

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
    linkText: {
      marginTop: "10px",
    },
    error: {
      color: "beige",  // Changed color to beige
      fontSize: "0.8em",
      marginTop: "-10px",
      marginBottom: "10px",
      textAlign: "left",
    },
      inputFieldError: { // Style for required inputs
          width: "100%",
          padding: "10px",
          marginBottom: "15px",
          borderRadius: "4px",
          border: "1px solid red", // Red border to indicate error
          backgroundColor: "#e3c5c5",
          color: "#000",
      },
    forgotPassword: {
      color: "#8b0000",
      textDecoration: "none",
      fontSize: "0.9em",
    }
  };

    const validate = () => {
        let isEmailValid = true;
        let isPasswordValid = true;

        if (!email) {
            setEmailError("Please fill out this field"); // Changed error message
            isEmailValid = false;
        } else {
            setEmailError("");
        }

        if (!password) {
            setPasswordError("Please fill out this field"); // Changed error message
            isPasswordValid = false;
        } else {
            setPasswordError("");
        }

        return isEmailValid && isPasswordValid;
    };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      // Add your login logic here (e.g., API call)
      alert("Login successful!"); // Replace with actual login logic
    }
  };

  return (
    <div style={styles.container}>
      <form style={styles.form} onSubmit={handleSubmit}>
        <h2 style={styles.heading}>Login</h2>
        <div>
          <input
            type="email"
            placeholder="Email"
            style={emailError ? styles.inputFieldError : styles.inputField} // Apply error style conditionally
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {emailError && <div style={styles.error}>{emailError}</div>}
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            style={passwordError ? styles.inputFieldError : styles.inputField} // Apply error style conditionally
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {passwordError && <div style={styles.error}>{passwordError}</div>}
        </div>
        <a href="#" style={styles.forgotPassword}>Forgot password?</a>
        <button type="submit" style={styles.button}>
          Login
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
