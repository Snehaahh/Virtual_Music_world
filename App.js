import React, { useState } from "react";
import { FaSun, FaMoon } from "react-icons/fa"; 
import "./index.css"; 

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle("dark-mode");
  };

  // Function to call the backend when the button is clicked
  const startModel = () => {
    fetch("http://127.0.0.1:5000/start-model")
      .then(response => response.json())
      .then(data => {
        alert(data.message || data.error);
      })
      .catch(error => console.error("Error:", error));
  };

  return (
    <div className={`container ${darkMode ? "dark" : ""}`}>
      {/* Dark Mode Toggle Button */}
      <button className="dark-mode-toggle" onClick={toggleDarkMode}>
        {darkMode ? <FaSun className="icon" /> : <FaMoon className="icon" />}
      </button>

      <h1>Welcome to Virtual Music World</h1>
      <p>Experience a new way of playing music online with our interactive instruments.</p>
      <p>🎹 Choose from multiple instruments</p>
      <p>🎼 Play music using your webcam</p>
      <p>🎧 No downloads required – just play!</p>

      <img src="/images/image.png" alt="3D Music" className="music-image" />
    
      <button id="getStarted" onClick={startModel}>Get Started</button>
    </div>
  );
}

export default App;
