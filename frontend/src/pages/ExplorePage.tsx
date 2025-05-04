import { useState } from "react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs"
import RecommenderTab from "../components/recommender-tab"
import ChatbotTab from "../components/chatbot-tab"

export default function ExplorePage() {
  const [activeTab, setActiveTab] = useState("recommender")

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Explore Collaborations</h1>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="recommender">Collaborator Recommender</TabsTrigger>
          <TabsTrigger value="chatbot">Chatbot</TabsTrigger>
        </TabsList>

        <TabsContent value="recommender" className="mt-6">
          <RecommenderTab />
        </TabsContent>

        <TabsContent value="chatbot" className="mt-6">
          <ChatbotTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
