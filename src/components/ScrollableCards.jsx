import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

const cardTexts = [
  "Best Overall Kalenjin Artiste- Secular",
  "Best Overall Kalenjin Artiste - Gospel",
  "Best Male Gospel Artiste",
  "Best Female Gospel Artist",
  "Best Male Secular Artist",
  "Best Female Secular Artist",
  "Best Upcoming Male Gospel Artist",
  "Best Upcoming Female Gospel Artist",
  "Best Upcoming Male Secular Artist",
  "Best Upcoming Female Secular Artist",
  "Best Choir/Group Gospel",
  "Best Band/Group Secular",
  "Gospel Song of the Year",
  "Ceremonial Song of the Year",
  "Secular Song of the Year",
  "Legend Award - Gospel",
  "Legend Award - Secular",
  "MC of the Year",
  "DJ of the Year",
  "Producer of the Year",
  "Comedian of the Year",
  "Social Influencer of the Year",
  "Pencil artiste/writer/videographer/Photographer Influencer of the Year",
  "Female Radio Personality of the Year",
  "Male Radio Personality of the Year",
  "Most Popular Male Radio Caller",
  "Most Popular Female Radio Caller",
  "Most Popular Kalenjin Gospel Radio/TV Show",
  "Most Popular Kalenjin Contemporary Music Radio/TV Show",
  "Posthumous Award",
  "Best Male Content Creator",
  "Best Female Content Creator",
  "Best Video Director",
  "Legend Award Female",
];

const ScrollableCards = () => {
  const navigate = useNavigate();
  const API_BASE_URL = "https://voting-9673.onrender.com";

  const handleCategoryClick = async (category) => {
    const candidateId = Number(sessionStorage.getItem("candidate_id"));
    const token = localStorage.getItem("token");

    if (!candidateId) {
      alert("Candidate ID is missing. Please log in again.");
      console.error("Candidate ID not found in sessionStorage.");
      return;
    }

    console.log("Candidate ID Retrieved:", candidateId);
    console.log("Sending to backend:", { category, candidate_id: candidateId });

    try {
      const response = await axios.post(
        `${API_BASE_URL}/assign_category`,
        { candidate_id: candidateId, category },
        {
          withCredentials: true,
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      console.log("Response from backend:", response.data);

      if (response.data.message === "Category assigned successfully") {
        console.log("Navigating to profile page...");
        navigate(`/profile-page/${candidateId}`, { state: { category } });
      }
    } catch (error) {
      console.error("Error handling category assignment:", error.message);
      alert(error.response?.data?.error || "Failed to assign category.");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.cardsWrapper}>
        {cardTexts.map((text, index) => (
          <div
            key={index}
            style={styles.card}
            onClick={() => handleCategoryClick(text)}
          >
            <span style={styles.link}>{text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    width: "100%",
    maxHeight: "500px", 
    overflowY: "auto", 
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  cardsWrapper: {
    display: "flex",
    flexDirection: "column", 
    gap: "20px",
  },
  card: {
    backgroundColor: "darkred",
    padding: "30px", 
    borderRadius: "15px",
    minWidth: "250px",
    textAlign: "center",
    fontSize: "18px", 
    fontWeight: "bold",
    color: "white",
    cursor: "pointer",
  },
  link: {
    textDecoration: "none",
    color: "white",
  },
};

export default ScrollableCards;