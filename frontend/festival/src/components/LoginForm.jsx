import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const LoginForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/check-session", {
      withCredentials: true,
    })
      .then(response => {
        console.log("Session Data:", response.data);
        if (response.data.user_id) {
          console.log("User is already logged in with ID:", response.data.user_id);
          navigate("/scrollable-cards");
        }
      })
      .catch(error => {
        console.error("Error checking session:", error.message);
      });
  }, []);

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
      const response = await axios.post("http://127.0.0.1:5000/login", {
        email,
        password,
      }, {
        withCredentials: true,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = response.data;
      console.log("Full Response Data:", result);
      console.log("Candidate ID received from backend:", result.candidate_id);

      if (result.candidate_id) {
        sessionStorage.setItem("candidate_id", result.candidate_id);
        console.log("Stored Candidate ID:", result.candidate_id);
      } else {
        console.error("Candidate ID is missing in response.");
      }

      localStorage.setItem("candidateEmail", email);

      navigate("/scrollable-cards");
    } catch (error) {
      console.error("Login Error:", error.message);
      alert("Login failed. Please check your credentials and try again!");
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
            style={styles.inputField}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {emailError && <div style={{ color: "red", fontSize: "0.8em", textAlign: "left" }}>{emailError}</div>}
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            style={styles.inputField}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {passwordError && <div style={{ color: "red", fontSize: "0.8em", textAlign: "left" }}>{passwordError}</div>}
        </div>
        <button type="submit" style={styles.button}>Login</button>
        <p style={styles.linkText}>
          Don't have an account? {" "}
          <span style={styles.signupButton} onClick={() => navigate("/signup")}>
            Signup
          </span>
        </p>
      </form>
    </div>
  );
};

export default LoginForm;



// import React, { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";

// const LoginForm = () => {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [emailError, setEmailError] = useState("");
//   const [passwordError, setPasswordError] = useState("");
//   const navigate = useNavigate();

//   useEffect(() => {
//     axios.get("http://127.0.0.1:5000/check-session", {
//       withCredentials: true,
//     })
//       .then(response => {
//         console.log("Session Data:", response.data);
//         if (response.data.user_id) {
//           console.log("User is already logged in with ID:", response.data.user_id);
//           navigate("/scrollable-cards");
//         }
//       })
//       .catch(error => {
//         console.error("Error checking session:", error.message);
//       });
//   }, []);
//   // useEffect(() => {
//   //   fetch("http://127.0.0.1:5000/check-session", {
//   //     method: "GET",
//   //     credentials: "include",
//   //   })
//   //     .then(response => response.json())
//   //     .then(data => {
//   //       console.log("Session Data:", data);
//   //       if (data.user_id) {
//   //         console.log("User is already logged in with ID:", data.user_id);
//   //         navigate("/scrollable-cards"); 
//   //       }
//   //     })
//   //     .catch(error => console.error("Error checking session:", error));
//   // }, []);



//   const styles = {
//     container: {
//       display: "flex",
//       justifyContent: "center",
//       alignItems: "center",
//       height: "100vh",
//       backgroundColor: "#8b0000",
//     },
//     form: {
//       backgroundColor: "#fff",
//       padding: "40px",
//       borderRadius: "8px",
//       boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
//       width: "350px",
//       textAlign: "center",
//     },
//     heading: {
//       marginBottom: "20px",
//       fontSize: "24px",
//       fontWeight: "bold",
//     },
//     inputField: {
//       width: "100%",
//       padding: "15px",
//       marginBottom: "15px",
//       borderRadius: "4px",
//       border: "none",
//       backgroundColor: "#d3a6a6",
//       color: "#000",
//       fontSize: "16px",
//     },
//     button: {
//       width: "100%",
//       padding: "12px",
//       backgroundColor: "#8b0000",
//       color: "#fff",
//       borderRadius: "4px",
//       border: "none",
//       fontSize: "18px",
//       cursor: "pointer",
//       marginTop: "10px",
//     },
//     linkText: {
//       marginTop: "15px",
//       fontSize: "14px",
//     },
//     signupButton: {
//       color: "#8b0000",
//       fontWeight: "bold",
//       textDecoration: "none",
//       cursor: "pointer",
//     },
//   };

//   const validate = () => {
//     let isValid = true;
//     if (!email) {
//       setEmailError("Please enter your email");
//       isValid = false;
//     } else {
//       setEmailError("");
//     }
//     if (!password) {
//       setPasswordError("Please enter your password");
//       isValid = false;
//     } else {
//       setPasswordError("");
//     }
//     return isValid;
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!validate()) return;
//     try {
//         const response = await fetch("login", {
//           method:"POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ email, password }),
//         credentials: "include",

//         }); 

//         const result = await response.json()
//         console.log("Full Response Data:", result);
//         console.log("Candidate ID received from backend:", result.candidate_id);

//         if (result.candidate_id) {
//           sessionStorage.setItem("candidate_id", result.candidate_id);
//           console.log("Stored Candidate ID:", result.candidate_id);
//         } else {
//           console.error("Candidate ID is missing in response.");
//         }

//         localStorage.setItem("candidateEmail", email);

//         navigate("/scrollable-cards");


//     } catch (error) {
//       console.error("Login Error:", error);
//         alert("Login failed. Please check your credentials and try again!");
//     }
//   };

//   return (
//     <div style={styles.container}>
//       <form style={styles.form} onSubmit={handleSubmit}>
//         <h2 style={styles.heading}>Login</h2>
//         <div>
//           <input
//             type="email"
//             placeholder="Email"
//             style={styles.inputField}
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//           />
//           {emailError && <div style={{ color: "red", fontSize: "0.8em", textAlign: "left" }}>{emailError}</div>}
//         </div>
//         <div>
//           <input
//             type="password"
//             placeholder="Password"
//             style={styles.inputField}
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//           />
//           {passwordError && <div style={{ color: "red", fontSize: "0.8em", textAlign: "left" }}>{passwordError}</div>}
//         </div>
//         <button type="submit" style={styles.button}>Login</button>
//         <p style={styles.linkText}>
//           Don't have an account? {" "}
//           <span style={styles.signupButton} onClick={() => navigate("/signup")}>
//             Signup
//           </span>
//         </p>
//       </form>
//     </div>
//   );
// };

// export default LoginForm;