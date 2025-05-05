import { Button } from "../components/ui/button"
import { Link } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { BookOpen, Users, MessageSquare, ArrowRight, Search } from "lucide-react"

export default function HomePage() {
  const featuredCourses = [
    {
      id: 1,
      title: "Advanced Research Methods",
      code: "DLMARM01-01",
      image: "/placeholder.svg?height=200&width=300",
    },
    {
      id: 2,
      title: "Data Query Languages",
      code: "DLMDMDL01",
      image: "/placeholder.svg?height=200&width=300",
    },
    {
      id: 3,
      title: "Data Warehousing & Pipelines",
      code: "DLMDMDWP01",
      image: "/placeholder.svg?height=200&width=300",
    },
    {
      id: 4,
      title: "AI-Enhanced Learning",
      code: "DLMAI01",
      image: "/placeholder.svg?height=200&width=300",
    },
  ]

  const newsItems = [
    {
      title: "Library and Information Services Update",
      date: "05/01/2025",
      description: "We are happy to announce the following changes to our services...",
    },
    {
      title: "Additional exam date announced",
      date: "04/22/2025",
      description: "Register now for the additional exam date on 23 May 2025.",
    },
    {
      title: "Citation guide refined",
      date: "03/31/2025",
      description: "New: parenthetical vs. narrative citation, citing sources in presentation...",
    },
  ]

  return (
    <div className="space-y-8 py-4">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Hi, Student</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Univerity account</span>
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
            U
          </div>
        </div>
      </div>

      {/* Main Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Course Registration */}
        <Card className="md:col-span-2 bg-slate-900 text-white">
          <CardHeader>
            <CardTitle className="text-xl text-white">Course Registration</CardTitle>
            <CardDescription className="text-slate-300">
              Registration and start of your training courses
            </CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="h-16 w-16 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <BookOpen className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        {/* Library Services */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Library and Information Services</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Search and find literature</p>
            <div className="mt-4 flex">
              <Search className="h-5 w-5 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        {/* FAQ */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">FAQ</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Questions and answers about your studies</p>
            <Button variant="link" className="p-0 mt-2">
              View all FAQs
            </Button>
          </CardContent>
        </Card>

        {/* News Section */}
        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">News</CardTitle>
            <Button variant="ghost" size="sm" className="gap-1">
              View all <ArrowRight className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {newsItems.map((item, i) => (
                <div key={i} className="border-b pb-3 last:border-0">
                  <div className="flex justify-between items-start">
                    <h3 className="font-medium">{item.title}</h3>
                    <span className="text-xs text-muted-foreground">{item.date}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Courses Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Courses</h2>
          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-amber-500"></span> 8 active
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-green-500"></span> 2 completed
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {featuredCourses.map((course) => (
            <Card key={course.id} className="overflow-hidden">
              <div className="h-40 bg-slate-200">
                <img
                  src={course.image || "/placeholder.svg"}
                  alt={course.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <CardHeader className="p-4">
                <CardTitle className="text-base">{course.title}</CardTitle>
                <CardDescription>{course.code}</CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="flex items-center text-xs text-muted-foreground">
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>


      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link to="/explore">
          <Card className="hover:bg-slate-50 transition-colors">
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <Users className="h-8 w-8 mb-2 text-primary" />
              <h3 className="font-medium">Find Collaborators</h3>
              <p className="text-xs text-muted-foreground mt-1">Connect with students</p>
            </CardContent>
          </Card>
        </Link>
        <Link to="/courses">
          <Card className="hover:bg-slate-50 transition-colors">
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <BookOpen className="h-8 w-8 mb-2 text-primary" />
              <h3 className="font-medium">Courses</h3>
              <p className="text-xs text-muted-foreground mt-1">Browse available courses</p>
            </CardContent>
          </Card>
        </Link>
        <Link to="/clubs">
          <Card className="hover:bg-slate-50 transition-colors">
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <Users className="h-8 w-8 mb-2 text-primary" />
              <h3 className="font-medium">Clubs</h3>
              <p className="text-xs text-muted-foreground mt-1">Join student organizations</p>
            </CardContent>
          </Card>
        </Link>
        <Link to="/courses?tab=chatbot">
          <Card className="hover:bg-slate-50 transition-colors">
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <MessageSquare className="h-8 w-8 mb-2 text-primary" />
              <h3 className="font-medium">Chatbot</h3>
              <p className="text-xs text-muted-foreground mt-1">Get instant assistance</p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  )
}
