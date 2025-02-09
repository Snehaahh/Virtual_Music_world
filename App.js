import React, { useState } from "react";
import { FaSun, FaMoon } from "react-icons/fa"; 
import "./index.css"; 

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle("dark-mode");
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

      {/* Get Started Button */}
      <button onClick={() => alert("Camera will open here!")}>Get Started</button>
    </div>
  );
}

export default App;
