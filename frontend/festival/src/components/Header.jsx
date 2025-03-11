import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import logo from "./kalelog.jpeg";

function Header() {
  const navigate = useNavigate();

  useEffect(() => {
    // Wait for 5 seconds, then navigate to SignupForm
    const timer = setTimeout(() => {
      navigate("/signup");
    }, 5000);

    // Cleanup function to clear the timer if the component unmounts
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div
      style={{
        backgroundImage: `url(${logo})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        textShadow: "2px 2px 4px rgba(0, 0, 0, 0.5)",
      }}
    >
      <h1>My Music Festival App</h1>
    </div>
  );
}

export default Header;
