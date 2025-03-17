const express = require("express");
const AfricasTalking = require("africastalking");
const dotenv = require("dotenv");
const axios = require("axios");

dotenv.config();

const app = express();
app.use(express.urlencoded({ extended: true }));

// Africa's Talking configuration
const africasTalking = AfricasTalking({
  apiKey: process.env.AFRICASTALKING_API_KEY,
  username: process.env.AFRICASTALKING_USERNAME,
});

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:5000";

const categories = [
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

const sessions = new Map();

app.post("/api/ussd", async (req, res) => {
  const { sessionId, phoneNumber, text } = req.body;
  let response = "";

  let normalizedPhone = phoneNumber;
  if (!normalizedPhone.startsWith("+")) {
    normalizedPhone = `+254${phoneNumber.replace(/^0/, "")}`;
  }
  console.log("Raw phoneNumber:", phoneNumber);
  console.log("Normalized phoneNumber:", normalizedPhone);

  let session = sessions.get(sessionId) || {
    phoneNumber: normalizedPhone,
    step: "menu",
  };
  const userInput = text.trim();

  try {
    if (userInput === "") {
      response =
        "CON Welcome to Kalenjin Awards Voting\n1. Vote\n2. Check Results";
      session.step = "menu";
    } else if (session.step === "menu" && userInput === "1") {
      response =
        "CON Select Category:\n" +
        categories.map((cat, i) => `${i + 1}. ${cat}`).join("\n");
      session.step = "select_category";
    } else if (session.step === "select_category") {
      const categoryIndex = parseInt(userInput) - 1;
      if (categoryIndex >= 0 && categoryIndex < categories.length) {
        session.category = categories[categoryIndex];
        try {
          const candidatesResponse = await axios.get(
            `${BACKEND_URL}/list_candidates`,
            {
              params: { category: session.category },
            }
          );
          if (candidatesResponse.status !== 200) {
            console.error(
              "Error fetching candidates:",
              candidatesResponse.statusText
            );
            response = `END Failed to fetch candidates. Status: ${candidatesResponse.status}`;
          } else if (
            !candidatesResponse.data.candidates ||
            candidatesResponse.data.candidates.length === 0
          ) {
            // Fetch signed-up candidates instead
            try {
              const signedUpCandidatesResponse = await axios.get(
                `${BACKEND_URL}/get_signed_up_candidates`
              );
              if (signedUpCandidatesResponse.status === 200) {
                const signedUpCandidates =
                  signedUpCandidatesResponse.data.candidates;
                response =
                  "CON No candidates found for this category. Here are signed-up candidates:\n" +
                  signedUpCandidates
                    .map((candidate, i) => `${i + 1}. ${candidate.full_name}`)
                    .join("\n");
              } else {
                response = "END Failed to fetch signed-up candidates.";
              }
            } catch (error) {
              console.error("Error fetching signed-up candidates:", error);
              response =
                "END An error occurred while fetching signed-up candidates.";
            }
          } else {
            session.candidateIds = candidatesResponse.data.candidates.map(
              (c) => c.id
            );

            // Fetch candidate names from the profile page
            const candidateNames = await Promise.all(
              session.candidateIds.map(async (candidateId) => {
                try {
                  const profileResponse = await axios.get(
                    `${BACKEND_URL}/get_name_profile_image/${candidateId}`
                  );
                  return profileResponse.data.full_name;
                } catch (error) {
                  console.error(
                    `Error fetching name for candidate ${candidateId}:`,
                    error
                  );
                  return `Candidate ${candidateId}`; // Default name in case of error
                }
              })
            );
            session.candidates = candidateNames; // Assign names to session

            response =
              "CON Select Candidate:\n" +
              session.candidates
                .map((name, i) => `${i + 1}. ${name}`)
                .join("\n");
            session.step = "vote";
          }
        } catch (error) {
          console.error("Error fetching candidates:", error);
          response =
            "END An error occurred while fetching candidates. Try again.";
        }
      } else {
        response = "CON Invalid category. Try again.";
      }
    } else if (session.step === "vote") {
      const candidateIndex = parseInt(userInput) - 1;
      if (candidateIndex >= 0 && candidateIndex < session.candidates.length) {
        const candidateId = session.candidateIds[candidateIndex];
        try {
          const voteResponse = await axios.post(`${BACKEND_URL}/vote`, {
            voter_phone: normalizedPhone,
            candidate_id: candidateId,
          });
          if (voteResponse.status === 200) {
            response = "END Vote recorded successfully!";
            session.step = "menu";
          } else {
            response = `END ${voteResponse.data.error || "Voting failed."}`;
          }
        } catch (error) {
          console.error("Error recording vote:", error);
          response =
            "END An error occurred while recording your vote. Try again.";
        }
      } else {
        response = "CON Invalid candidate. Try again.";
      }
    } else if (session.step === "menu" && userInput === "2") {
      try {
        const results = await axios.get(`${BACKEND_URL}/get_verifications`);
        response =
          "END Voting Results:\n" +
          categories
            .map((cat) => {
              const top = results.data.verifications
                .filter((v) => v.category === cat)
                .sort((a, b) => b.vote_count - a.vote_count)[0];
              return top
                ? `${cat}: ${top.vote_count} votes`
                : `${cat}: 0 votes`;
            })
            .join("\n");
      } catch (error) {
        console.error("Error fetching results:", error);
        response = "END An error occurred while fetching results. Try again.";
      }
    } else {
      response = "CON Invalid option.\n1. Vote\n2. Check Results";
      session.step = "menu";
    }
  } catch (error) {
    console.error("General Error:", error);
    response = "END An error occurred. Try again.";
  }

  sessions.set(sessionId, session);
  res.set("Content-Type", "text/plain");
  res.send(response);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`USSD Server running on port ${PORT}`);
});
