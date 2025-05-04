
"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import { Button } from "../components/ui/button"
import { Search, Loader2 } from "lucide-react"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { MultiSelect } from "../components/multi-select"

export default function ClubsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [skills, setSkills] = useState<string[]>([])
  const [interests, setInterests] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [recommendedClubs, setRecommendedClubs] = useState<any[]>([])
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

  const clubs = [
    {
      id: "tech-innovators",
      name: "Tech Innovators",
      category: "Technology and Innovation",
      meetingTime: "Tuesdays, 5:00 PM - 7:00 PM",
      location: "Innovation Lab, Building C",
      description: "A club focused on emerging technologies, innovation, and entrepreneurship.",
      skills: ["Blockchain", "AI"],
      interests: ["Entrepreneurship", "Hackathons"],
    },
    {
      id: "data-science",
      name: "Data Science Society",
      category: "Analytics and Machine Learning",
      meetingTime: "Wednesdays, 6:00 PM - 8:00 PM",
      location: "Computing Center, Room 302",
      description: "Explore the world of data science, machine learning, and AI.",
      skills: ["Data Science", "Python", "AI"],
      interests: ["Hackathons"],
    },
    {
      id: "robotics",
      name: "Robotics Club",
      category: "Building and Programming Robots",
      meetingTime: "Fridays, 4:00 PM - 7:00 PM",
      location: "Engineering Building, Robotics Lab",
      description: "Design, build, and program robots for competitions and exhibitions.",
      skills: ["Electronics", "AI"],
      interests: ["Robotics", "Hackathons"],
    },
    {
      id: "entrepreneurship",
      name: "Entrepreneurship Society",
      category: "Business and Startup Development",
      meetingTime: "Thursdays, 5:30 PM - 7:30 PM",
      location: "Business School, Room 105",
      description: "Learn about business development, pitch your ideas, and connect with mentors.",
      skills: ["Marketing"],
      interests: ["Entrepreneurship"],
    },
    {
      id: "art-design",
      name: "Creative Design Collective",
      category: "Art and Digital Design",
      meetingTime: "Mondays, 4:00 PM - 6:00 PM",
      location: "Arts Building, Design Studio",
      description: "Collaborate on creative projects spanning graphic design, UI/UX, and digital art.",
      skills: ["Design"],
      interests: ["Music"],
    },
    {
      id: "debate",
      name: "Debate Team",
      category: "Public Speaking",
      meetingTime: "Tuesdays, 6:30 PM - 8:30 PM",
      location: "Humanities Building, Room 204",
      description: "Develop argumentation and public speaking skills through competitive debate.",
      skills: [],
      interests: ["Entrepreneurship"],
    },
  ]

  const filteredClubs = clubs.filter(
    (club) =>
      club.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      club.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      club.description.toLowerCase().includes(searchQuery.toLowerCase()),
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
      const recommendations = clubs.map((club) => {
        // Count matching skills
        const matchingSkills = club.skills.filter((skill) => skills.includes(skill)).length

        // Count matching interests
        const matchingInterests = club.interests.filter((interest) => interests.includes(interest)).length

        // Calculate match percentage (weighted: skills 60%, interests 40%)
        const skillsWeight = skills.length > 0 ? 0.6 : 0
        const interestsWeight = interests.length > 0 ? 0.4 : 0

        const skillsScore = skills.length > 0 ? (matchingSkills / skills.length) * skillsWeight : 0
        const interestsScore = interests.length > 0 ? (matchingInterests / interests.length) * interestsWeight : 0

        // Normalize if only one category is selected
        const totalWeight = skillsWeight + interestsWeight
        const matchScore = totalWeight > 0 ? ((skillsScore + interestsScore) / totalWeight) * 100 : 0

        return {
          ...club,
          matchScore,
          matchingSkills,
          matchingInterests,
          matchPercentage: `${Math.round(matchScore)}%`,
        }
      })

      // Sort by match score and filter out low matches
      const sortedRecommendations = recommendations
        .filter((club) => club.matchScore > 0)
        .sort((a, b) => b.matchScore - a.matchScore)

      setRecommendedClubs(sortedRecommendations)
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Clubs</h1>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search clubs..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Tabs defaultValue="available">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="available">Available Clubs</TabsTrigger>
          <TabsTrigger value="recommended">Club Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="available" className="mt-6">
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
                    <div className="space-y-2 mb-4">
                      <div className="flex">
                        <span className="font-medium w-28">Meeting Times:</span>
                        <span className="text-muted-foreground">{club.meetingTime}</span>
                      </div>
                      <div className="flex">
                        <span className="font-medium w-28">Location:</span>
                        <span className="text-muted-foreground">{club.location}</span>
                      </div>
                    </div>
                    <div className="mt-4">
                      <div className="flex flex-wrap gap-1 mb-2">
                        {club.skills.map((skill, i) => (
                          <span key={i} className="bg-primary/10 text-primary px-2 py-1 rounded-md text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {club.interests.map((interest, i) => (
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
                      <Button size="sm">Join Club</Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
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
                  Finding Clubs...
                </>
              ) : (
                "Get Club Recommendations"
              )}
            </Button>

            {recommendedClubs.length > 0 && (
              <div className="mt-8">
                <h3 className="text-xl font-semibold mb-4">Recommended Clubs</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {recommendedClubs.map((club) => (
                    <Card key={club.id} className="overflow-hidden">
                      <div className="bg-primary/10 p-2 flex justify-between items-center">
                        <span className="text-sm font-medium text-primary">{club.matchPercentage} Match</span>
                        <span className="text-xs text-muted-foreground">{club.category}</span>
                      </div>
                      <CardHeader>
                        <CardTitle>{club.name}</CardTitle>
                        <CardDescription>
                          {club.matchingSkills > 0 && `${club.matchingSkills} matching skills`}
                          {club.matchingSkills > 0 && club.matchingInterests > 0 && " • "}
                          {club.matchingInterests > 0 && `${club.matchingInterests} matching interests`}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">{club.description}</p>
                        <div className="space-y-2 mb-4">
                          <div className="flex">
                            <span className="font-medium w-28">Meeting Times:</span>
                            <span className="text-muted-foreground">{club.meetingTime}</span>
                          </div>
                          <div className="flex">
                            <span className="font-medium w-28">Location:</span>
                            <span className="text-muted-foreground">{club.location}</span>
                          </div>
                        </div>
                        <div className="mt-4">
                          <div className="flex flex-wrap gap-1 mb-2">
                            {club.skills.map((skill: any, i: any) => (
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
                            {club.interests.map((interest: any, i: any) => (
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
                          <Button size="sm">Join Club</Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {recommendedClubs.length === 0 && !loading && (skills.length > 0 || interests.length > 0) && (
              <div className="text-center py-10">
                <p className="text-muted-foreground">
                  No matching clubs found. Try selecting different skills or interests.
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}


// "use client"

// import { useState } from "react"
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
// import { Button } from "../components/ui/button"
// import { Search, Loader2 } from "lucide-react"
// import { Input } from "../components/ui/input"
// import { Label } from "../components/ui/label"
// import { MultiSelect } from "../components/multi-select"

// export default function ClubsPage() {
//  const [searchQuery, setSearchQuery] = useState("")
//  const [skills, setSkills] = useState<string[]>([])
//  const [interests, setInterests] = useState<string[]>([])
//  const [loading, setLoading] = useState(false)
//  const [recommendedClubs, setRecommendedClubs] = useState<any[]>([])
//  const [availableSkills, setAvailableSkills] = useState<string[]>([
//   "Blockchain",
//   "Data Science",
//   "Design",
//   "AI",
//   "Marketing",
//   "Python",
//   "Electronics",
//  ])
//  const [availableInterests, setAvailableInterests] = useState<string[]>([
//   "Entrepreneurship",
//   "Hackathons",
//   "Video Games",
//   "Music",
//   "Robotics",
//   "Ecology",
//  ])

//  const clubs = [
//   {
//    id: "tech-innovators",
//    name: "Tech Innovators",
//    category: "Technology and Innovation",
//    meetingTime: "Tuesdays, 5:00 PM - 7:00 PM",
//    location: "Innovation Lab, Building C",
//    description: "A club focused on emerging technologies, innovation, and entrepreneurship.",
//    skills: ["Blockchain", "AI"],
//    interests: ["Entrepreneurship", "Hackathons"],
//   },
//   {
//    id: "data-science",
//    name: "Data Science Society",
//    category: "Analytics and Machine Learning",
//    meetingTime: "Wednesdays, 6:00 PM - 8:00 PM",
//    location: "Computing Center, Room 302",
//    description: "Explore the world of data science, machine learning, and AI.",
//    skills: ["Data Science", "Python", "AI"],
//    interests: ["Hackathons"],
//   },
//   {
//    id: "robotics",
//    name: "Robotics Club",
//    category: "Building and Programming Robots",
//    meetingTime: "Fridays, 4:00 PM - 7:00 PM",
//    location: "Engineering Building, Robotics Lab",
//    description: "Design, build, and program robots for competitions and exhibitions.",
//    skills: ["Electronics", "AI"],
//    interests: ["Robotics", "Hackathons"],
//   },
//   {
//    id: "entrepreneurship",
//    name: "Entrepreneurship Society",
//    category: "Business and Startup Development",
//    meetingTime: "Thursdays, 5:30 PM - 7:30 PM",
//    location: "Business School, Room 105",
//    description: "Learn about business development, pitch your ideas, and connect with mentors.",
//    skills: ["Marketing"],
//    interests: ["Entrepreneurship"],
//   },
//   {
//    id: "art-design",
//    name: "Creative Design Collective",
//    category: "Art and Digital Design",
//    meetingTime: "Mondays, 4:00 PM - 6:00 PM",
//    location: "Arts Building, Design Studio",
//    description: "Collaborate on creative projects spanning graphic design, UI/UX, and digital art.",
//    skills: ["Design"],
//    interests: ["Music"],
//   },
//   {
//    id: "debate",
//    name: "Debate Team",
//    category: "Public Speaking",
//    meetingTime: "Tuesdays, 6:30 PM - 8:30 PM",
//    location: "Humanities Building, Room 204",
//    description: "Develop argumentation and public speaking skills through competitive debate.",
//    skills: [],
//    interests: ["Entrepreneurship"],
//   },
//  ]

//  const filteredClubs = clubs.filter(
//   (club) =>
//    club.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
//    club.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
//    club.description.toLowerCase().includes(searchQuery.toLowerCase()),
//  )

//  const handleGetRecommendations = () => {
//   if (skills.length === 0 && interests.length === 0) {
//    alert("Please select at least one skill or interest")
//    return
//   }

//   setLoading(true)

//   // Simulate API call with a timeout
//   setTimeout(() => {
//    // Calculate recommendations based on skills and interests match
//    const recommendations = clubs.map((club) => {
//     // Count matching skills
//     const matchingSkills = club.skills.filter((skill) => skills.includes(skill)).length

//     // Count matching interests
//     const matchingInterests = club.interests.filter((interest) => interests.includes(interest)).length

//     // Calculate match percentage (weighted: skills 60%, interests 40%)
//     const skillsWeight = skills.length > 0 ? 0.6 : 0
//     const interestsWeight = interests.length > 0 ? 0.4 : 0

//     const skillsScore = skills.length > 0 ? (matchingSkills / skills.length) * skillsWeight : 0
//     const interestsScore = interests.length > 0 ? (matchingInterests / interests.length) * interestsWeight : 0

//     // Normalize if only one category is selected
//     const totalWeight = skillsWeight + interestsWeight
//     const matchScore = totalWeight > 0 ? ((skillsScore + interestsScore) / totalWeight) * 100 : 0

//     return {
//      ...club,
//      matchScore,
//      matchingSkills,
//      matchingInterests,
//      matchPercentage: `${Math.round(matchScore)}%`,
//     }
//    })

//    // Sort by match score and filter out low matches
//    const sortedRecommendations = recommendations
//     .filter((club) => club.matchScore > 0)
//     .sort((a, b) => b.matchScore - a.matchScore)

//    setRecommendedClubs(sortedRecommendations)
//    setLoading(false)
//   }, 1000)
//  }

//  return (
//   <div className="space-y-6">
//    <h1 className="text-3xl font-bold tracking-tight">Clubs</h1>

//    <div className="relative">
//     <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
//     <Input
//      placeholder="Search clubs..."
//      className="pl-10"
//      value={searchQuery}
//      onChange={(e) => setSearchQuery(e.target.value)}
//     />
//    </div>

//    <Tabs defaultValue="available">
//     <TabsList className="grid w-full grid-cols-2">
//      <TabsTrigger value="available">Available Clubs</TabsTrigger>
//      <TabsTrigger value="recommended">Club Recommendations</TabsTrigger>
//     </TabsList>

//     <TabsContent value="available" className="mt-6">
//      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//       {filteredClubs.length === 0 ? (
//        <div className="text-center py-10 col-span-2">
//         <p className="text-muted-foreground">No clubs found matching your search.</p>
//        </div>
//       ) : (
//        filteredClubs.map((club) => (
//         <Card key={club.id}>
//          <CardHeader>
//           <CardTitle>{club.name}</CardTitle>
//           <CardDescription>{club.category}</CardDescription>
//          </CardHeader>
//          <CardContent>
//           <p className="text-muted-foreground mb-4">{club.description}</p>
//           <div className="space-y-2 mb-4">
//            <div className="flex">
//             <span className="font-medium w-28">Meeting Times:</span>
//             <span className="text-muted-foreground">{club.meetingTime}</span>
//            </div>
//            <div className="flex">
//             <span className="font-medium w-28">Location:</span>
//             <span className="text-muted-foreground">{club.location}</span>
//            </div>
//           </div>
//           <div className="mt-4">
//            <div className="flex flex-wrap gap-1 mb-2">
//             {club.skills.map((skill, i) => (
//              <span key={i} className="bg-primary/10 text-primary px-2 py-1 rounded-md text-xs">
//               {skill}
//              </span>
//             ))}
//            </div>
//            <div className="flex flex-wrap gap-1">
//             {club.interests.map((interest, i) => (
//              <span
//               key={i}
//               className="bg-secondary/10 text-secondary-foreground px-2 py-1 rounded-md text-xs"
//              >
//               {interest}
//              </span>
//             ))}
//            </div>
//           </div>
//           <div className="mt-4 flex justify-end">
//            <Button size="sm">Join Club</Button>
//           </div>
//          </CardContent>
//         </Card>
//        ))
//       )}
//      </div>
//     </TabsContent>

//     <TabsContent value="recommended" className="mt-6">
//      <div className="space-y-6">
//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
//        <div className="space-y-4">
//         <Label htmlFor="skills">Your Skills</Label>
//         <MultiSelect
//          options={(availableSkills || []).map((skill) => ({ label: skill, value: skill }))}
//          selected={(skills || []).map((skill) => ({ label: skill, value: skill }))}
//          onChange={(selected) => setSkills((selected || []).map((item) => item.value))}
//          placeholder="Select skills..."
//         />
//        </div>

//        <div className="space-y-4">
//         <Label htmlFor="interests">Your Interests</Label>
//         <MultiSelect
//          options={(availableInterests || []).map((interest) => ({ label: interest, value: interest }))}
//          selected={(interests || []).map((interest) => ({ label: interest, value: interest }))}
//          onChange={(selected) => setInterests((selected || []).map((item) => item.value))}
//          placeholder="Select interests..."
//         />
//        </div>
//       </div>

//       <Button onClick={handleGetRecommendations} disabled={loading}>
//        {loading ? (
//         <>
//          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
//          Finding Clubs...
//         </>
//        ) : (
//         "Get Club Recommendations"
//        )}
//       </Button>

//       {recommendedClubs.length > 0 && (
//        <div className="mt-8">
//         <h3 className="text-xl font-semibold mb-4">Recommended Clubs</h3>
//         <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//          {recommendedClubs.map((club) => (
//           <Card key={club.id} className="overflow-hidden">
//            <div className="bg-primary/10 p-2 flex justify-between items-center">
//             <span className="text-sm font-medium text-primary">{club.matchPercentage} Match</span>
//             <span className="text-xs text-muted-foreground">{club.category}</span>
//            </div>
//            <CardHeader>
//             <CardTitle>{club.name}</CardTitle>
//             <CardDescription>
//              {club.matchingSkills > 0 && `${club.matchingSkills} matching skills`}
//              {club.matchingSkills > 0 && club.matchingInterests > 0 && " • "}
//              {club.matchingInterests > 0 && `${club.matchingInterests} matching interests`}
//             </CardDescription>
//            </CardHeader>
//            <CardContent>
//             <p className="text-sm text-muted-foreground mb-4">{club.description}</p>
//             <div className="space-y-2 mb-4">
//              <div className="flex">
//               <span className="font-medium w-28">Meeting Times:</span>
//               <span className="text-muted-foreground">{club.meetingTime}</span>
//              </div>
//              <div className="flex">
//               <span className="font-medium w-28">Location:</span>
//               <span className="text-muted-foreground">{club.location}</span>
//              </div>
//             </div>
//             <div className="mt-4">
//              <div className="flex flex-wrap gap-1 mb-2">
//               {club.skills.map((skill: any, i: any) => (
//                <span
//                 key={i}
//                 className={`px-2 py-1 rounded-md text-xs ${skills.includes(skill)
//                  ? "bg-primary text-primary-foreground"
//                  : "bg-primary/10 text-primary"
//                  }`}
//                >
//                 {skill}
//                </span>
//               ))}
//              </div>
//              <div className="flex flex-wrap gap-1">
//               {club.interests.map((interest: any, i: any) => (
//                <span
//                 key={i}
//                 className={`px-2 py-1 rounded-md text-xs ${interests.includes(interest)
//                  ? "bg-secondary text-secondary-foreground"
//                  : "bg-secondary/10 text-secondary-foreground"
//                  }`}
//                >
//                 {interest}
//                </span>
//               ))}
//              </div>
//             </div>
//             <div className="mt-4 flex justify-end">
//              <Button size="sm">Join Club</Button>
//             </div>
//            </CardContent>
//           </Card>
//          ))}
//         </div>
//        </div>
//       )}

//       {recommendedClubs.length === 0 && !loading && (skills.length > 0 || interests.length > 0) && (
//        <div className="text-center py-10">
//         <p className="text-muted-foreground">
//          No matching clubs found. Try selecting different skills or interests.
//         </p>
//        </div>
//       )}
//      </div>
//     </TabsContent>
//    </Tabs>
//   </div>
//  )
// }
