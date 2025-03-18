import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./App.css";
import Header from "./components/Header";
import KalenjinMusicFestival from "./components/KalenjinMusicFestival";
import SignupForm from "./components/SignupForm";
import LoginForm from "./components/LoginForm";
import ScrollableCards from "./components/ScrollableCards";
import ProfilePage from "./components/ProfilePage.jsx";
import VerificationForm from "./components/VerificationForm.jsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <>
              <Header />
              <KalenjinMusicFestival />
            </>
          }
        />
        <Route path="/signup" element={<SignupForm />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/scrollable-cards" element={<ScrollableCards />} />
        <Route path="/profile-page/:candidateId" element={<ProfilePage />} />
        <Route
          path="/verification-form/:candidateId"
          element={<VerificationForm />}
        />
      </Routes>
    </Router>
  );
}

export default App;
