import React from "react";

const VerificationPage = () => {
  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Verify Your Documents</h2>
      <div style={styles.box}>
        <label style={styles.label}>National Identification Card/ID:</label>
        <input type="text" style={styles.input} placeholder="Enter your ID number" />
        
        <label style={styles.label}>Phone Number:</label>
        <input type="text" style={styles.input} placeholder="+254" />
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    backgroundColor: "#f8f9fa",
  },
  heading: {
    fontSize: "24px",
    fontWeight: "bold",
    marginBottom: "20px",
    color:"darkred"
  },
  box: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    display: "flex",
    flexDirection: "column",
    width: "300px",
  },
  label: {
    fontSize: "16px",
    marginBottom: "5px",
    fontWeight: "bold",
  },
  input: {
    width: "100%",
    padding: "8px",
    marginBottom: "15px",
    border: "1px solid #ccc",
    borderRadius: "4px",
  },
};

export default VerificationPage;
