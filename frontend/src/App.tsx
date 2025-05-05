import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { ThemeProvider } from "./components/theme-provider"
import Navbar from "./components/navbar"
import HomePage from "./pages/HomePage"
import ExplorePage from "./pages/ExplorePage"
import CoursesPage from "./pages/CoursesPage"
import ClubsPage from "./pages/ClubsPage"
import "./App.css"

function App() {
  return (
    <ThemeProvider defaultTheme="light">
      <Router>
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/explore" element={<ExplorePage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/clubs" element={<ClubsPage />} />
          </Routes>
        </main>
      </Router>
    </ThemeProvider>
  )
}

export default App
