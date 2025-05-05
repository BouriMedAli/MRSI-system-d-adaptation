"use client"

import { useEffect, useState } from "react"
import axios from "axios"
import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { Label } from "./ui/label"
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs"
import { MultiSelect } from "./multi-select"
import { Loader2 } from "lucide-react"
import { useRecommenderStore } from "@/stores/recommander.store"

type Recommendation = {
  student_id: number
  skills: string[]
  interests: string[]
}

export default function RecommenderTab() {
  const [topN, setTopN] = useState(5)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    activeTab,
    setActiveTab,
    availableSkills,
    availableInterests,
    setAvailableSkills,
    setAvailableInterests,
    getForm,
    updateForm,
  } = useRecommenderStore()

  const { skills, interests, projectSkills = [] } = getForm()

  const handleTabChange = (tab: "similarity" | "complementarity") => {
    // Save current values first
    updateForm({ skills, interests, projectSkills })
    // Then switch tab
    setActiveTab(tab)
    setRecommendations([]) // Clear results on switch
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (skills.length === 0 || interests.length === 0) {
      alert("Please select at least one skill and one interest")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const endpoint = `http://localhost:8000/recommend/${activeTab}`
      const payload = {
        student_id: 0,
        skills,
        interests,
        top_n: topN,
        ...(activeTab === "complementarity" && { project_skills: projectSkills }),
      }

      const res = await axios.post(endpoint, payload)
      setRecommendations(res.data.recommendations || [])
    } catch (err) {
      console.error("Recommendation error:", err)
      setError("Failed to get recommendations.")
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (availableSkills.length && availableInterests.length) return
    const fetchData = async () => {
      try {
        const [skillsRes, interestsRes] = await Promise.all([
          axios.get("http://localhost:8000/skills"),
          axios.get("http://localhost:8000/interests"),
        ])
        setAvailableSkills(skillsRes.data.skills || [])
        setAvailableInterests(interestsRes.data.interests || [])
      } catch (err) {
        console.error("Failed to load available options", err)
        setError("Could not load skills or interests.")
      }
    }
    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      {error && <div className="bg-destructive/10 text-destructive p-4 rounded">{error}</div>}

      <Tabs value={activeTab} onValueChange={(val) => handleTabChange(val as any)}>
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="similarity">🔁 Similarity</TabsTrigger>
          <TabsTrigger value="complementarity">🧩 Complementarity</TabsTrigger>
        </TabsList>
      </Tabs>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Label>Your Skills</Label>
            <MultiSelect
              options={availableSkills.map((s) => ({ label: s, value: s }))}
              selected={skills.map((s) => ({ label: s, value: s }))}
              onChange={(selected) => updateForm({ skills: selected.map((i) => i.value) })}
              placeholder="Select skills..."
            />
          </div>

          <div className="space-y-4">
            <Label>Your Interests</Label>
            <MultiSelect
              options={availableInterests.map((i) => ({ label: i, value: i }))}
              selected={interests.map((i) => ({ label: i, value: i }))}
              onChange={(selected) => updateForm({ interests: selected.map((i) => i.value) })}
              placeholder="Select interests..."
            />
          </div>
        </div>

        {activeTab === "complementarity" && (
          <div className="space-y-4">
            <Label>Project Skills Needed</Label>
            <MultiSelect
              options={availableSkills.map((s) => ({ label: s, value: s }))}
              selected={projectSkills.map((s) => ({ label: s, value: s }))}
              onChange={(selected) => updateForm({ projectSkills: selected.map((i) => i.value) })}
              placeholder="Select project skills..."
            />
          </div>
        )}

        <div className="max-w-xs space-y-2">
          <Label>Number of Results</Label>
          <Input
            type="number"
            min={1}
            max={20}
            value={topN}
            onChange={(e) => setTopN(parseInt(e.target.value) || 5)}
          />
        </div>

        <Button type="submit" disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Getting Recommendations...
            </>
          ) : (
            "Get Recommendations"
          )}
        </Button>
      </form>

      {recommendations.length > 0 && (
        <div className="mt-8 space-y-4">
          <h3 className="text-xl font-semibold">Recommendations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((rec, idx) => (
              <Card key={idx}>
                <CardHeader>
                  <CardTitle>Student #{rec.student_id}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div>
                    <strong>Skills:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {rec.skills.map((s, i) => (
                        <span key={i} className="bg-primary/10 text-primary px-2 py-1 rounded text-sm">{s}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <strong>Interests:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {rec.interests.map((i, j) => (
                        <span key={j} className="bg-secondary/10 text-primary px-2 py-1 rounded text-sm">{i}</span>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

