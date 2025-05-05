"use client"

import { Link, useLocation } from "react-router-dom"
import { cn } from "../lib/utils"
import { Button } from "./ui/button"
import { MoonIcon, SunIcon, BookOpen, Users, Home, UserPlus } from "lucide-react"
import { useTheme } from "./theme-provider"

export default function Navbar() {
  const location = useLocation()
  const { setTheme, theme } = useTheme()

  const navItems = [
    { name: "Home", path: "/", icon: <Home className="h-4 w-4 mr-2" /> },
    { name: "Explore", path: "/explore", icon: <Users className="h-4 w-4 mr-2" /> },
    { name: "Courses", path: "/courses", icon: <BookOpen className="h-4 w-4 mr-2" /> },
    { name: "Clubs", path: "/clubs", icon: <UserPlus className="h-4 w-4 mr-2" /> },
  ]

  return (
    <nav className="border-b">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-1">
          <span className="text-xs text-muted-foreground hidden md:inline-block ml-2">
            University of Sciences
          </span>
        </div>

        <div className="flex items-center space-x-6">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary flex items-center",
                location.pathname === item.path ? "text-primary font-semibold" : "text-muted-foreground",
              )}
            >
              {item.icon}
              {item.name}
            </Link>
          ))}

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
          >
            <SunIcon className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <MoonIcon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>
        </div>
      </div>
    </nav>
  )
}
