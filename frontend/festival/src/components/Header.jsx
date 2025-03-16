import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import logo from "./kalelog.jpeg";

function Header() {
  const navigate = useNavigate();

  useEffect(() => {
    
    const timer = setTimeout(() => {
      navigate("/signup");
    }, 5000);

    
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
    </div>
  );
}

export default Header;
