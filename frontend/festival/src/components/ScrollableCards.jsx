import React from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import pro1 from './pro1.jpg'; // Import the icon image

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

  const handleIconClick = (category) => {
    const candidateId = Number(sessionStorage.getItem("candidate_id")) || 0; // Fallback to 0 if not logged in

    // Attempt to assign category in the background (best effort)
    if (candidateId) {
      try {
        axios.post(
          "http://127.0.0.1:5000/assign_category",
          { candidate_id: candidateId, category },
          { withCredentials: true }
        ).then(response => {
          console.log("Category assignment response:", response.data);
        }).catch(error => {
          console.error("Error assigning category:", error.response?.data || error.message);
        });
      } catch (error) {
        console.error("Error in category assignment:", error);
      }
    } else {
      console.log("No candidateId found, proceeding without assignment.");
    }

    // Navigate to ProfilePage with candidateId and category
    navigate(`/account-form/${candidateId}`, { state: { category } });
  };

  return (
    <div style={styles.container}>
      <div style={styles.cardsWrapper}>
        {cardTexts.map((text, index) => (
          <div key={index} style={styles.card}>
            <span style={styles.link}>{text}</span>
            <img
              src={pro1}
              alt="Profile Icon"
              style={styles.icon}
              onClick={() => handleIconClick(text)}
            />
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
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    position: "relative",
  },
  link: {
    textDecoration: "none",
    color: "white",
    flexGrow: 1,
  },
  icon: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    cursor: "pointer",
    marginLeft: "10px",
  },
};

export default ScrollableCards;