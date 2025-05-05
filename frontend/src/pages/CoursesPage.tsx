"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import { Button } from "../components/ui/button"
import { Search, Loader2 } from "lucide-react"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import ChatbotTab from "../components/chatbot-tab"
import { MultiSelect } from "../components/multi-select"
import ChatbotTabCourses from "@/components/chatbot-tab-courses"

export default function CoursesPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [skills, setSkills] = useState<string[]>([])
  const [interests, setInterests] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [recommendedCourses, setRecommendedCourses] = useState<any[]>([])
  const [availableSkills, setAvailableSkills] = useState<string[]>([
    "Blockchain",
    "Data Science",
    "Design",
    "AI",
    "Marketing",
    "Python",
    "Electronics",
  ])
  const [availableInterests, setAvailableInterests] = useState<string[]>([
    "Entrepreneurship",
    "Hackathons",
    "Video Games",
    "Music",
    "Robotics",
    "Ecology",
  ])

  const courses = [
    {
      id: "cs301",
      title: "Advanced Data Structures",
      department: "Computer Science",
      credits: 3,
      description: "Advanced techniques for designing and analyzing data structures and algorithms.",
      skills: ["Data Science", "Python"],
      interests: ["Hackathons"],
    },
    {
      id: "cs405",
      title: "Artificial Intelligence",
      department: "Computer Science",
      credits: 4,
      description: "Introduction to AI concepts, problem-solving methods, and machine learning techniques.",
      skills: ["AI", "Python", "Data Science"],
      interests: ["Robotics"],
    },
    {
      id: "cs450",
      title: "Machine Learning",
      department: "Computer Science",
      credits: 4,
      description: "Statistical pattern recognition, supervised and unsupervised learning, neural networks.",
      skills: ["AI", "Data Science", "Python"],
      interests: ["Hackathons", "Robotics"],
    },
    {
      id: "cs480",
      title: "Web Development",
      department: "Computer Science",
      credits: 3,
      description: "Modern web development techniques, frameworks, and best practices.",
      skills: ["Design"],
      interests: ["Entrepreneurship"],
    },
    {
      id: "eng201",
      title: "Electronics Fundamentals",
      department: "Engineering",
      credits: 4,
      description: "Basic principles of electronic circuits, components, and systems.",
      skills: ["Electronics"],
      interests: ["Robotics"],
    },
    {
      id: "eng305",
      title: "Robotics Design",
      department: "Engineering",
      credits: 3,
      description: "Design and implementation of robotic systems, sensors, and control algorithms.",
      skills: ["Electronics", "AI"],
      interests: ["Robotics"],
    },
    {
      id: "bus220",
      title: "Marketing Fundamentals",
      department: "Business",
      credits: 3,
      description: "Core marketing concepts, consumer behavior, and marketing strategies.",
      skills: ["Marketing"],
      interests: ["Entrepreneurship"],
    },
    {
      id: "bus340",
      title: "Entrepreneurship",
      department: "Business",
      credits: 3,
      description: "Starting and managing new ventures, business models, and innovation.",
      skills: ["Marketing"],
      interests: ["Entrepreneurship"],
    },
  ]

  const filteredCourses = courses.filter(
    (course) =>
      course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.description.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleGetRecommendations = () => {
    if (skills.length === 0 && interests.length === 0) {
      alert("Please select at least one skill or interest")
      return
    }

    setLoading(true)

    // Simulate API call with a timeout
    setTimeout(() => {
      // Calculate recommendations based on skills and interests match
      const recommendations = courses.map((course) => {
        // Count matching skills
        const matchingSkills = course.skills.filter((skill) => skills.includes(skill)).length

        // Count matching interests
        const matchingInterests = course.interests.filter((interest) => interests.includes(interest)).length

        // Calculate match percentage (weighted: skills 60%, interests 40%)
        const skillsWeight = skills.length > 0 ? 0.6 : 0
        const interestsWeight = interests.length > 0 ? 0.4 : 0

        const skillsScore = skills.length > 0 ? (matchingSkills / skills.length) * skillsWeight : 0
        const interestsScore = interests.length > 0 ? (matchingInterests / interests.length) * interestsWeight : 0

        // Normalize if only one category is selected
        const totalWeight = skillsWeight + interestsWeight
        const matchScore = totalWeight > 0 ? ((skillsScore + interestsScore) / totalWeight) * 100 : 0

        return {
          ...course,
          matchScore,
          matchingSkills,
          matchingInterests,
          matchPercentage: `${Math.round(matchScore)}%`,
        }
      })

      // Sort by match score and filter out low matches
      const sortedRecommendations = recommendations
        .filter((course) => course.matchScore > 0)
        .sort((a, b) => b.matchScore - a.matchScore)

      setRecommendedCourses(sortedRecommendations)
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Courses</h1>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search courses..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Tabs defaultValue="available">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="available">Available Courses</TabsTrigger>
          <TabsTrigger value="chatbot">Chatbot</TabsTrigger>
          <TabsTrigger value="recommended">Course Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="available" className="mt-6">
          <div className="space-y-6">
            {filteredCourses.length === 0 ? (
              <div className="text-center py-10">
                <p className="text-muted-foreground">No courses found matching your search.</p>
              </div>
            ) : (
              Object.entries(
                filteredCourses.reduce(
                  (acc, course) => {
                    if (!acc[course.department]) {
                      acc[course.department] = []
                    }
                    acc[course.department].push(course)
                    return acc
                  },
                  {} as Record<string, typeof courses>,
                ),
              ).map(([department, departmentCourses]) => (
                <div key={department} className="bg-card rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-semibold mb-4">{department} Department</h3>
                  <div className="grid gap-4">
                    {departmentCourses.map((course) => (
                      <Card key={course.id}>
                        <CardHeader className="p-4">
                          <div className="flex justify-between">
                            <div>
                              <CardTitle className="text-lg">{course.title}</CardTitle>
                              <CardDescription>{course.id}</CardDescription>
                            </div>
                            <div className="text-sm text-muted-foreground">Credits: {course.credits}</div>
                          </div>
                        </CardHeader>
                        <CardContent className="p-4 pt-0">
                          <p className="text-sm text-muted-foreground">{course.description}</p>
                          <div className="mt-4">
                            <div className="flex flex-wrap gap-1 mb-2">
                              {course.skills.map((skill, i) => (
                                <span key={i} className="bg-primary/10 text-primary px-2 py-1 rounded-md text-xs">
                                  {skill}
                                </span>
                              ))}
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {course.interests.map((interest, i) => (
                                <span
                                  key={i}
                                  className="bg-secondary/10 text-secondary-foreground px-2 py-1 rounded-md text-xs"
                                >
                                  {interest}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="mt-4 flex justify-end">
                            <Button size="sm">Enroll</Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="chatbot" className="mt-6">
          <ChatbotTabCourses />
        </TabsContent>

        <TabsContent value="recommended" className="mt-6">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label htmlFor="skills">Your Skills</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSkills([])}
                    disabled={skills.length === 0}
                    className="h-8 text-xs"
                  >
                    Reset
                  </Button>
                </div>
                <MultiSelect
                  options={(availableSkills || []).map((skill) => ({ label: skill, value: skill }))}
                  selected={(skills || []).map((skill) => ({ label: skill, value: skill }))}
                  onChange={(selected) => setSkills((selected || []).map((item) => item.value))}
                  placeholder="Select skills..."
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label htmlFor="interests">Your Interests</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setInterests([])}
                    disabled={interests.length === 0}
                    className="h-8 text-xs"
                  >
                    Reset
                  </Button>
                </div>
                <MultiSelect
                  options={(availableInterests || []).map((interest) => ({ label: interest, value: interest }))}
                  selected={(interests || []).map((interest) => ({ label: interest, value: interest }))}
                  onChange={(selected) => setInterests((selected || []).map((item) => item.value))}
                  placeholder="Select interests..."
                />
              </div>
            </div>

            <Button onClick={handleGetRecommendations} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Finding Courses...
                </>
              ) : (
                "Get Course Recommendations"
              )}
            </Button>

            {recommendedCourses.length > 0 && (
              <div className="mt-8">
                <h3 className="text-xl font-semibold mb-4">Recommended Courses</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {recommendedCourses.map((course) => (
                    <Card key={course.id} className="overflow-hidden">
                      <div className="bg-primary/10 p-2 flex justify-between items-center">
                        <span className="text-sm font-medium text-primary">{course.matchPercentage} Match</span>
                        <span className="text-xs text-muted-foreground">{course.department}</span>
                      </div>
                      <CardHeader>
                        <CardTitle>{course.title}</CardTitle>
                        <CardDescription>
                          {course.matchingSkills > 0 && `${course.matchingSkills} matching skills`}
                          {course.matchingSkills > 0 && course.matchingInterests > 0 && " • "}
                          {course.matchingInterests > 0 && `${course.matchingInterests} matching interests`}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">{course.description}</p>
                        <div className="mt-4">
                          <div className="flex flex-wrap gap-1 mb-2">
                            {course.skills.map((skill: any, i: any) => (
                              <span
                                key={i}
                                className={`px-2 py-1 rounded-md text-xs ${skills.includes(skill)
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-primary/10 text-primary"
                                  }`}
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {course.interests.map((interest: any, i: any) => (
                              <span
                                key={i}
                                className={`px-2 py-1 rounded-md text-xs ${interests.includes(interest)
                                  ? "bg-secondary text-secondary-foreground"
                                  : "bg-secondary/10 text-secondary-foreground"
                                  }`}
                              >
                                {interest}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="mt-4 flex justify-end">
                          <Button size="sm">Enroll</Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {recommendedCourses.length === 0 && !loading && (skills.length > 0 || interests.length > 0) && (
              <div className="text-center py-10">
                <p className="text-muted-foreground">
                  No matching courses found. Try selecting different skills or interests.
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

