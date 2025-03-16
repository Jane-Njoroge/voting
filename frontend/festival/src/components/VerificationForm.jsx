import React, { useState } from "react";
import { useParams,useNavigate } from "react-router-dom";
import axios from "axios";

const VerificationPage = () => {
  const { candidateId } = useParams();
  const navigate = useNavigate();
  const [idNumber, setIdNumber] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [enteredOTP, setEnteredOTP] = useState("");

  const sendOTP = async () => {
    if (!idNumber || !phoneNumber) {
      alert("Please enter your ID number and phone number.");
      return;
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/verify_and_send_otp",
        { candidate_id: candidateId, national_id: idNumber, phone_number: phoneNumber },
        { withCredentials: true }
      );

      if (response.data.message) {
        setOtpSent(true);
        alert("OTP sent!");
      }
    } catch (error) {
      alert(error.response?.data?.error || "Failed to send OTP.");
    }
  };

  const verifyOTP = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/verify_otp",
        { phone_number: phoneNumber, otp: enteredOTP },
        { withCredentials: true }
      );

      if (response.data.message) {
        alert("Phone number verified!");
        navigate(`/account-form/${candidateId}`);
      }
    } catch (error) {
      alert(error.response?.data?.error || "Invalid OTP.");
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Verify Your Documents</h2>
      <div style={styles.box}>
        {!otpSent ? (
          <>
            <label style={styles.label}>National ID:</label>
            <input
              type="text"
              style={styles.input}
              placeholder="Enter your ID number"
              value={idNumber}
              onChange={(e) => setIdNumber(e.target.value)}
            />
            <label style={styles.label}>Phone Number:</label>
            <input
              type="text"
              style={styles.input}
              placeholder="+254"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
            />
            <button style={styles.button} onClick={sendOTP}>
              Send OTP
            </button>
          </>
        ) : (
          <>
            <label style={styles.label}>Enter OTP:</label>
            <input
              type="text"
              style={styles.input}
              placeholder="Enter OTP"
              value={enteredOTP}
              onChange={(e) => setEnteredOTP(e.target.value)}
            />
            <button style={styles.button} onClick={verifyOTP}>
              Verify OTP
            </button>
          </>
        )}
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
    color: "darkred",
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
  button: {
    backgroundColor: "darkred",
    color: "#fff",
    padding: "10px",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};

export default VerificationPage;