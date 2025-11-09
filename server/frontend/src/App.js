// In frontend/src/App.js - COMPLETE VERSION

import LoginPanel from "./components/Login/Login";
import RegisterPanel from "./components/Register/Register";
import { Routes, Route } from "react-router-dom";

// --- DYNAMIC/DEALERSHIP IMPORTS ---
import Dealers from './components/Dealers/Dealers';
import Dealer from './components/Dealers/Dealer';
import PostReview from './components/Dealers/PostReview';

// --- STATIC PAGE IMPORTS (FIXES BLANK PAGES) ---
// Note: Assumes your files are named AboutUs/AboutUs.js and ContactUs/ContactUs.js
import AboutUs from './components/AboutUs/AboutUs'; 
import ContactUs from './components/ContactUs/ContactUs.js'; 

function App() {
  return (
    <Routes>
      {/* Home page: Shows Dealers List (Task 17) */}
      <Route path="/" element={<Dealers />} />
      
      {/* Authentication Routes */}
      <Route path="/login" element={<LoginPanel />} />
      <Route path="/register" element={<RegisterPanel />} />

      {/* Static Page Routes (FIXES THE BLANK PAGES) */}
      <Route path="/about" element={<AboutUs />} />
      <Route path="/contact" element={<ContactUs />} />
      
      {/* Dynamic Dealer Routes */}
      <Route path="/dealer/:id" element={<Dealer />} />         {/* Task 20 */}
      <Route path="/postreview/:id" element={<PostReview />} />  {/* Task 21 & 22 */}
    </Routes>
  );
}
export default App;