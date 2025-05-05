"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import { Button } from "../components/ui/button"
import { Search } from "lucide-react"
import { Input } from "../components/ui/input"

export default function ClubsCoursesPage() {
  const [searchQuery, setSearchQuery] = useState("")

  const courses = [
    {
      id: "cs301",
      title: "Advanced Data Structures",
      department: "Computer Science",
      credits: 3,
      description: "Advanced techniques for designing and analyzing data structures and algorithms.",
    },
    {
      id: "cs405",
      title: "Artificial Intelligence",
      department: "Computer Science",
      credits: 4,
      description: "Introduction to AI concepts, problem-solving methods, and machine learning techniques.",
    },
    {
      id: "cs450",
      title: "Machine Learning",
      department: "Computer Science",
      credits: 4,
      description: "Statistical pattern recognition, supervised and unsupervised learning, neural networks.",
    },
    {
      id: "cs480",
      title: "Web Development",
      department: "Computer Science",
      credits: 3,
      description: "Modern web development techniques, frameworks, and best practices.",
    },
    {
      id: "eng201",
      title: "Electronics Fundamentals",
      department: "Engineering",
      credits: 4,
      description: "Basic principles of electronic circuits, components, and systems.",
    },
    {
      id: "eng305",
      title: "Robotics Design",
      department: "Engineering",
      credits: 3,
      description: "Design and implementation of robotic systems, sensors, and control algorithms.",
    },
    {
      id: "bus220",
      title: "Marketing Fundamentals",
      department: "Business",
      credits: 3,
      description: "Core marketing concepts, consumer behavior, and marketing strategies.",
    },
    {
      id: "bus340",
      title: "Entrepreneurship",
      department: "Business",
      credits: 3,
      description: "Starting and managing new ventures, business models, and innovation.",
    },
  ]

  const clubs = [
    {
      id: "tech-innovators",
      name: "Tech Innovators",
      category: "Technology and Innovation",
      meetingTime: "Tuesdays, 5:00 PM - 7:00 PM",
      location: "Innovation Lab, Building C",
      description: "A club focused on emerging technologies, innovation, and entrepreneurship.",
    },
    {
      id: "data-science",
      name: "Data Science Society",
      category: "Analytics and Machine Learning",
      meetingTime: "Wednesdays, 6:00 PM - 8:00 PM",
      location: "Computing Center, Room 302",
      description: "Explore the world of data science, machine learning, and AI.",
    },
    {
      id: "robotics",
      name: "Robotics Club",
      category: "Building and Programming Robots",
      meetingTime: "Fridays, 4:00 PM - 7:00 PM",
      location: "Engineering Building, Robotics Lab",
      description: "Design, build, and program robots for competitions and exhibitions.",
    },
    {
      id: "entrepreneurship",
      name: "Entrepreneurship Society",
      category: "Business and Startup Development",
      meetingTime: "Thursdays, 5:30 PM - 7:30 PM",
      location: "Business School, Room 105",
      description: "Learn about business development, pitch your ideas, and connect with mentors.",
    },
    {
      id: "art-design",
      name: "Creative Design Collective",
      category: "Art and Digital Design",
      meetingTime: "Mondays, 4:00 PM - 6:00 PM",
      location: "Arts Building, Design Studio",
      description: "Collaborate on creative projects spanning graphic design, UI/UX, and digital art.",
    },
    {
      id: "debate",
      name: "Debate Team",
      category: "Public Speaking",
      meetingTime: "Tuesdays, 6:30 PM - 8:30 PM",
      location: "Humanities Building, Room 204",
      description: "Develop argumentation and public speaking skills through competitive debate.",
    },
  ]

  const recommendedCourses = [
    {
      id: "ai101",
      title: "Introduction to AI",
      department: "Computer Science",
      match: "98% match",
      reason: "Based on your interest in Data Science",
    },
    {
      id: "ds202",
      title: "Data Visualization",
      department: "Information Systems",
      match: "95% match",
      reason: "Complements your Python skills",
    },
    {
      id: "mkt301",
      title: "Digital Marketing",
      department: "Business",
      match: "92% match",
      reason: "Aligns with your Marketing interest",
    },
    {
      id: "eng210",
      title: "IoT Fundamentals",
      department: "Engineering",
      match: "90% match",
      reason: "Related to your Electronics skills",
    },
  ]

  const recommendedClubs = [
    {
      id: "ai-research",
      name: "AI Research Group",
      category: "Artificial Intelligence",
      match: "97% match",
      reason: "Aligns with your AI and Python skills",
    },
    {
      id: "hackathon",
      name: "Hackathon Heroes",
      category: "Competitive Programming",
      match: "94% match",
      reason: "Perfect for your Hackathon interest",
    },
    {
      id: "blockchain",
      name: "Blockchain Innovators",
      category: "Cryptocurrency & Blockchain",
      match: "91% match",
      reason: "Matches your Blockchain skill",
    },
    {
      id: "design-thinking",
      name: "Design Thinking Workshop",
      category: "UX/UI Design",
      match: "89% match",
      reason: "Complements your Design skills",
    },
  ]

  const filteredCourses = courses.filter(
    (course) =>
      course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.description.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const filteredClubs = clubs.filter(
    (club) =>
      club.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      club.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      club.description.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Clubs & Courses</h1>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search courses and clubs..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Tabs defaultValue="courses">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="courses">Available Courses</TabsTrigger>
          <TabsTrigger value="recommended-courses">Course Recommendations</TabsTrigger>
          <TabsTrigger value="clubs">Available Clubs</TabsTrigger>
          <TabsTrigger value="recommended-clubs">Club Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="courses" className="mt-6">
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

        <TabsContent value="recommended-courses" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recommendedCourses.map((course) => (
              <Card key={course.id} className="overflow-hidden">
                <div className="bg-primary/10 p-2 flex justify-between items-center">
                  <span className="text-sm font-medium text-primary">{course.match}</span>
                  <span className="text-xs text-muted-foreground">{course.department}</span>
                </div>
                <CardHeader>
                  <CardTitle>{course.title}</CardTitle>
                  <CardDescription>{course.reason}</CardDescription>
                </CardHeader>
                <CardContent className="flex justify-end">
                  <Button size="sm">View Details</Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="clubs" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredClubs.length === 0 ? (
              <div className="text-center py-10 col-span-2">
                <p className="text-muted-foreground">No clubs found matching your search.</p>
              </div>
            ) : (
              filteredClubs.map((club) => (
                <Card key={club.id}>
                  <CardHeader>
                    <CardTitle>{club.name}</CardTitle>
                    <CardDescription>{club.category}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground mb-4">{club.description}</p>
                    <div className="space-y-2">
                      <div className="flex">
                        <span className="font-medium w-28">Meeting Times:</span>
                        <span className="text-muted-foreground">{club.meetingTime}</span>
                      </div>
                      <div className="flex">
                        <span className="font-medium w-28">Location:</span>
                        <span className="text-muted-foreground">{club.location}</span>
                      </div>
                    </div>
                    <div className="mt-4 flex justify-end">
                      <Button size="sm">Join Club</Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="recommended-clubs" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recommendedClubs.map((club) => (
              <Card key={club.id} className="overflow-hidden">
                <div className="bg-primary/10 p-2 flex justify-between items-center">
                  <span className="text-sm font-medium text-primary">{club.match}</span>
                  <span className="text-xs text-muted-foreground">{club.category}</span>
                </div>
                <CardHeader>
                  <CardTitle>{club.name}</CardTitle>
                  <CardDescription>{club.reason}</CardDescription>
                </CardHeader>
                <CardContent className="flex justify-end">
                  <Button size="sm">View Details</Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}


// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"

// export default function ClubsCoursesPage() {
//   return (
//     <div className="space-y-6">
//       <h1 className="text-3xl font-bold tracking-tight">Clubs, Courses & Classrooms</h1>

//       <Tabs defaultValue="clubs">
//         <TabsList className="grid w-full grid-cols-3">
//           <TabsTrigger value="clubs">Student Clubs</TabsTrigger>
//           <TabsTrigger value="courses">Available Courses</TabsTrigger>
//           <TabsTrigger value="classrooms">Classrooms & Labs</TabsTrigger>
//         </TabsList>

//         <TabsContent value="clubs" className="mt-6">
//           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//             <Card>
//               <CardHeader>
//                 <CardTitle>Tech Innovators</CardTitle>
//                 <CardDescription>Technology and Innovation Club</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   A club focused on emerging technologies, innovation, and entrepreneurship. Members work on
//                   cutting-edge projects and participate in hackathons.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Meeting Times:</span> Tuesdays, 5:00 PM - 7:00 PM
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Location:</span> Innovation Lab, Building C
//                 </div>
//               </CardContent>
//             </Card>

//             <Card>
//               <CardHeader>
//                 <CardTitle>Data Science Society</CardTitle>
//                 <CardDescription>Analytics and Machine Learning</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   Explore the world of data science, machine learning, and AI. Regular workshops, competitions, and
//                   industry speaker events.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Meeting Times:</span> Wednesdays, 6:00 PM - 8:00 PM
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Location:</span> Computing Center, Room 302
//                 </div>
//               </CardContent>
//             </Card>

//             <Card>
//               <CardHeader>
//                 <CardTitle>Robotics Club</CardTitle>
//                 <CardDescription>Building and Programming Robots</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   Design, build, and program robots for competitions and exhibitions. All experience levels welcome.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Meeting Times:</span> Fridays, 4:00 PM - 7:00 PM
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Location:</span> Engineering Building, Robotics Lab
//                 </div>
//               </CardContent>
//             </Card>

//             <Card>
//               <CardHeader>
//                 <CardTitle>Entrepreneurship Society</CardTitle>
//                 <CardDescription>Business and Startup Development</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   Learn about business development, pitch your ideas, and connect with mentors. Regular pitch
//                   competitions and networking events.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Meeting Times:</span> Thursdays, 5:30 PM - 7:30 PM
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Location:</span> Business School, Room 105
//                 </div>
//               </CardContent>
//             </Card>
//           </div>
//         </TabsContent>

//         <TabsContent value="courses" className="mt-6">
//           <div className="space-y-6">
//             <div className="bg-card rounded-lg p-6 shadow-sm">
//               <h3 className="text-xl font-semibold mb-4">Computer Science Department</h3>
//               <ul className="space-y-3">
//                 <li className="flex justify-between items-center">
//                   <span>CS301: Advanced Data Structures</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>CS405: Artificial Intelligence</span>
//                   <span className="text-sm text-muted-foreground">Credits: 4</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>CS450: Machine Learning</span>
//                   <span className="text-sm text-muted-foreground">Credits: 4</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>CS480: Web Development</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//               </ul>
//             </div>

//             <div className="bg-card rounded-lg p-6 shadow-sm">
//               <h3 className="text-xl font-semibold mb-4">Engineering Department</h3>
//               <ul className="space-y-3">
//                 <li className="flex justify-between items-center">
//                   <span>ENG201: Electronics Fundamentals</span>
//                   <span className="text-sm text-muted-foreground">Credits: 4</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>ENG305: Robotics Design</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>ENG410: Advanced Control Systems</span>
//                   <span className="text-sm text-muted-foreground">Credits: 4</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>ENG450: IoT Applications</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//               </ul>
//             </div>

//             <div className="bg-card rounded-lg p-6 shadow-sm">
//               <h3 className="text-xl font-semibold mb-4">Business Department</h3>
//               <ul className="space-y-3">
//                 <li className="flex justify-between items-center">
//                   <span>BUS220: Marketing Fundamentals</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>BUS340: Entrepreneurship</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>BUS380: Project Management</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//                 <li className="flex justify-between items-center">
//                   <span>BUS420: Innovation Management</span>
//                   <span className="text-sm text-muted-foreground">Credits: 3</span>
//                 </li>
//               </ul>
//             </div>
//           </div>
//         </TabsContent>

//         <TabsContent value="classrooms" className="mt-6">
//           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//             <Card>
//               <CardHeader>
//                 <CardTitle>Innovation Lab</CardTitle>
//                 <CardDescription>Building C, Room 101</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   A collaborative workspace equipped with the latest technology for prototyping and innovation. Features
//                   3D printers, VR equipment, and collaborative workstations.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Capacity:</span> 40 students
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Hours:</span> 8:00 AM - 10:00 PM (Mon-Fri)
//                 </div>
//               </CardContent>
//             </Card>

//             <Card>
//               <CardHeader>
//                 <CardTitle>Robotics Laboratory</CardTitle>
//                 <CardDescription>Engineering Building, Room 205</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   Specialized lab for robotics development and testing. Equipped with workbenches, testing areas, and
//                   various robotics components.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Capacity:</span> 25 students
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Hours:</span> 9:00 AM - 8:00 PM (Mon-Fri)
//                 </div>
//               </CardContent>
//             </Card>

//             <Card>
//               <CardHeader>
//                 <CardTitle>Computing Center</CardTitle>
//                 <CardDescription>Technology Building, 3rd Floor</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   Modern computing facility with high-performance workstations, specialized software, and collaborative
//                   spaces for programming and data analysis.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Capacity:</span> 60 students
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Hours:</span> 24/7 Access with Student ID
//                 </div>
//               </CardContent>
//             </Card>

//             <Card>
//               <CardHeader>
//                 <CardTitle>Design Studio</CardTitle>
//                 <CardDescription>Arts Building, Room 150</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground">
//                   Creative space for design thinking and visual projects. Equipped with design software, drawing
//                   tablets, and presentation areas.
//                 </p>
//                 <div className="mt-4">
//                   <span className="font-medium">Capacity:</span> 30 students
//                 </div>
//                 <div className="mt-2">
//                   <span className="font-medium">Hours:</span> 8:00 AM - 9:00 PM (Mon-Fri)
//                 </div>
//               </CardContent>
//             </Card>
//           </div>
//         </TabsContent>
//       </Tabs>
//     </div>
//   )
// }
