"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { SendIcon, Bot, User, BookOpen } from "lucide-react"
import { Badge } from "./ui/badge"

type Message = {
  role: "user" | "assistant"
  content: string
  type?: "text" | "course-recommendation" | "course-selection"
  courses?: CourseRecommendation[]
  courseOptions?: CourseOption[]
  selectedCourse?: string
}

type CourseRecommendation = {
  id: string
  title: string
  department: string
  match: string
  skills: string[]
  credits: number
  description: string
}

type CourseOption = {
  id: string
  code: string
  name: string
  department: string
}

export default function ChatbotTab() {
  // Replace with initial state that includes course selection
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your student collaboration assistant. Here are the available courses:",
      type: "course-selection",
      courseOptions: [
        { id: "cs301", code: "CS301", name: "Advanced Data Structures", department: "CS" },
        { id: "cs405", code: "CS405", name: "Artificial Intelligence", department: "CS" },
        { id: "cs450", code: "CS450", name: "Machine Learning", department: "CS" },
        { id: "cs480", code: "CS480", name: "Web Development", department: "CS" },
        { id: "eng201", code: "ENG201", name: "Electronics Fundamentals", department: "ENG" },
        { id: "eng305", code: "ENG305", name: "Robotics Design", department: "ENG" },
      ],
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim()) return

    const userMessage: Message = {
      role: "user",
      content: input,
      type: "text",
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate API call delay
    setTimeout(() => {
      // Check for course recommendation request
      const lowerInput = input.toLowerCase()

      if (lowerInput.includes("recommend") && (lowerInput.includes("course") || lowerInput.includes("class"))) {
        // Send course recommendations
        const courseRecommendations: CourseRecommendation[] = [
          {
            id: "cs405",
            title: "Artificial Intelligence",
            department: "Computer Science",
            match: "98% match",
            skills: ["AI", "Python", "Data Science"],
            credits: 4,
            description: "Introduction to AI concepts, problem-solving methods, and machine learning techniques.",
          },
          {
            id: "cs450",
            title: "Machine Learning",
            department: "Computer Science",
            match: "95% match",
            skills: ["AI", "Data Science", "Python"],
            credits: 4,
            description: "Statistical pattern recognition, supervised and unsupervised learning, neural networks.",
          },
          {
            id: "eng305",
            title: "Robotics Design",
            department: "Engineering",
            match: "92% match",
            skills: ["Electronics", "AI"],
            credits: 3,
            description: "Design and implementation of robotic systems, sensors, and control algorithms.",
          },
          {
            id: "cs301",
            title: "Advanced Data Structures",
            department: "Computer Science",
            match: "87% match",
            skills: ["Data Science", "Python"],
            credits: 3,
            description: "Advanced techniques for designing and analyzing data structures and algorithms.",
          },
        ]

        const assistantMessage: Message = {
          role: "assistant",
          content: "Based on your profile and interests, here are some course recommendations that might interest you:",
          type: "course-recommendation",
          courses: courseRecommendations,
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else if (
        lowerInput.includes("courses") ||
        lowerInput.includes("select") ||
        lowerInput.includes("available") ||
        lowerInput.includes("show") ||
        lowerInput.includes("list")
      ) {
        // Send course selection options
        const courseOptions: CourseOption[] = [
          { id: "cs301", code: "CS301", name: "Advanced Data Structures", department: "CS" },
          { id: "cs405", code: "CS405", name: "Artificial Intelligence", department: "CS" },
          { id: "cs450", code: "CS450", name: "Machine Learning", department: "CS" },
          { id: "cs480", code: "CS480", name: "Web Development", department: "CS" },
          { id: "eng201", code: "ENG201", name: "Electronics Fundamentals", department: "ENG" },
          { id: "eng305", code: "ENG305", name: "Robotics Design", department: "ENG" },
        ]

        const assistantMessage: Message = {
          role: "assistant",
          content: "Here are the available courses. Select one to get started:",
          type: "course-selection",
          courseOptions: courseOptions,
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else {
        // Mock responses based on user input
        let response =
          "I'm not sure how to respond to that. Could you please provide more details about what you're looking for?"

        if (lowerInput.includes("find") || lowerInput.includes("collaborat")) {
          response =
            "To find collaborators, you can use our recommendation system. Just select your skills and interests, and we'll match you with compatible students!"
        } else if (lowerInput.includes("skill") || lowerInput.includes("interest")) {
          response =
            "Our platform supports various skills like Blockchain, Data Science, Design, AI, Marketing, Python, and Electronics. For interests, we have Entrepreneurship, Hackathons, Video Games, Music, Robotics, and Ecology."
        } else if (lowerInput.includes("club")) {
          response =
            "You can explore all available clubs in the 'Clubs' section. There you'll find information about student organizations and how to join them."
        } else if (lowerInput.includes("exam") || lowerInput.includes("test") || lowerInput.includes("quiz")) {
          response =
            "Our platform offers resources to help you prepare for exams. You can find practice questions and study materials in the course sections. Would you like me to show you the available courses?"
        } else if (lowerInput.includes("hello") || lowerInput.includes("hi") || lowerInput.includes("hey")) {
          response =
            "Hello there! How can I assist you with finding collaborators, courses, or navigating our platform today?"
        } else if (lowerInput.includes("thank")) {
          response = "You're welcome! If you have any other questions, feel free to ask."
        }

        const assistantMessage: Message = {
          role: "assistant",
          content: response,
          type: "text",
        }

        setMessages((prev) => [...prev, assistantMessage])
      }

      setIsLoading(false)
    }, 1000)
  }

  // Update the handleCourseSelection function to add a confirmation message
  const handleCourseSelection = (courseId: string, courseName: string) => {
    const userMessage: Message = {
      role: "user",
      content: `I want to learn more about ${courseName}`,
      type: "text",
    }

    // Add a confirmation message
    const confirmationMessage: Message = {
      role: "assistant",
      content: `Got it! Here's information about ${courseName}:`,
      type: "text",
    }

    // Find the selected course from previous messages
    let selectedCourse: CourseRecommendation | undefined

    for (const message of messages) {
      if (message.type === "course-recommendation" && message.courses) {
        selectedCourse = message.courses.find((course) => course.id === courseId)
        if (selectedCourse) break
      }
    }

    // If not found in recommendations, create a default one
    if (!selectedCourse) {
      selectedCourse = {
        id: courseId,
        title: courseName,
        department: courseId.startsWith("cs") ? "Computer Science" : "Engineering",
        match: "",
        skills: [],
        credits: 3,
        description: "This course provides students with knowledge and skills in the subject area.",
      }
    }

    const courseDetailMessage: Message = {
      role: "assistant",
      content: "",
      type: "course-recommendation",
      courses: [selectedCourse],
    }

    setMessages((prev) => [...prev, userMessage, confirmationMessage, courseDetailMessage])
  }

  return (
    <Card className="border shadow-sm">
      <CardHeader className="bg-slate-50 border-b">
        <CardTitle className="text-lg flex items-center">
          <Bot className="h-5 w-5 mr-2 text-primary" />
          Student Collaboration Assistant
        </CardTitle>
      </CardHeader>
      <div className="flex flex-col h-[600px]">
        <CardContent className="flex-1 p-4 overflow-y-auto mb-4">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`flex items-start max-w-[80%] rounded-lg px-4 py-2 ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                    }`}
                >
                  {message.role === "assistant" && <Bot className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />}
                  {message.role === "user" && <User className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />}
                  <div className="w-full">
                    <div>{message.content}</div>

                    {/* Course Recommendations */}
                    {message.type === "course-recommendation" && message.courses && (
                      <div className="mt-3 space-y-2">
                        {message.courses.map((course) => (
                          <div key={course.id} className="bg-background rounded-md p-3 border flex flex-col">
                            <div className="flex justify-between items-start">
                              <div className="flex items-center">
                                <BookOpen className="h-4 w-4 mr-2 text-primary" />
                                <div>
                                  <div className="font-medium">{course.title}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {course.department} • {course.credits} credits
                                  </div>
                                </div>
                              </div>
                              {course.match && <div className="text-xs font-medium text-primary">{course.match}</div>}
                            </div>

                            <div className="mt-2 text-sm">{course.description}</div>

                            {course.skills.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {course.skills.map((skill, i) => (
                                  <Badge key={i} variant="outline" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            )}

                            <div className="mt-3 flex justify-end">
                              <Button size="sm" variant="outline" className="text-xs h-7">
                                View Details
                              </Button>
                              <Button size="sm" className="text-xs h-7 ml-2">
                                Enroll
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Course Selection */}
                    {message.type === "course-selection" && message.courseOptions && (
                      <div className="mt-3">
                        <div className="grid grid-cols-2 gap-2">
                          {message.courseOptions.map((course) => (
                            <Button
                              key={course.id}
                              variant="outline"
                              className="text-sm justify-center border-primary/30 hover:bg-primary/10 h-auto py-2"
                              onClick={() => handleCourseSelection(course.id, course.name)}
                            >
                              <div className="text-left">
                                <div className="font-medium">{course.code}</div>
                                <div className="text-xs text-muted-foreground truncate max-w-[150px]">
                                  {course.name}
                                </div>
                              </div>
                            </Button>
                          ))}
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                          Select a course to view details and resources.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted flex items-center">
                  <Bot className="h-4 w-4 mr-2 flex-shrink-0" />
                  <div className="flex space-x-2">
                    <div
                      className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>

        <div className="border-t p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !input.trim()}>
              <SendIcon className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </form>
          {/* <div className="mt-2 flex flex-wrap gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="text-xs h-7"
              onClick={() => setInput("Show me available courses")}
            >
              Available courses
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-xs h-7"
              onClick={() => setInput("Can you recommend courses for me?")}
            >
              Course recommendations
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-xs h-7"
              onClick={() => setInput("How do I find collaborators?")}
            >
              Find collaborators
            </Button>
          </div> */}
        </div>
      </div>
    </Card>
  )
}
