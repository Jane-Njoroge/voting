import React from "react";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Header from './Components/Header';
import KalenjinMusicFestival from './Components/KalenjinMusicFestival';
import SignupForm from './Components/SignupForm';
import LoginForm from "./Components/LoginForm";

function App() {
  return (
    <Router>
      <div>
        {/* <Header /> */}
        <Routes>
          <Route path="/" element={<KalenjinMusicFestival />} />
          <Route path="/signup" element={<SignupForm />} />
          <Route path="/login" element={<LoginForm/>}/>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
