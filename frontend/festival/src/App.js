import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./App.css";
import Header from "./components/Header";
import KalenjinMusicFestival from "./components/KalenjinMusicFestival";
import SignupForm from "./components/SignupForm";
import LoginForm from "./components/LoginForm";
import ScrollableCards from "./components/ScrollableCards"
import AccounForm from"./components/AccountForm.jsx"
import VerificationForm from"./components/VerificationForm.jsx"

function App() {
  return (
    <Router>
      {/* Uncomment if you want to use the header */}
      <Routes>
        <Route path="/" element={<Header/>} />
       <Route path="/" element={< KalenjinMusicFestival/>} />
       <Route path="/signup" element={<SignupForm />} />
       <Route path="/login" element={<LoginForm />} />
       <Route path="/scrollable-cards" element={<ScrollableCards/>}/>
       <Route path="/account-form" element={<AccounForm/>}/>
       <Route path="/verification-form" element={<VerificationForm/>}/>
      </Routes>
    </Router>
  );
}

export default App;
