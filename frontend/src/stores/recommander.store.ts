import { create } from "zustand"

type Option = string

interface RecommenderFormState {
 skills: Option[]
 interests: Option[]
 projectSkills?: Option[] // optional for similarity
}

interface RecommenderState {
 similarity: RecommenderFormState
 complementarity: RecommenderFormState
 activeTab: "similarity" | "complementarity"

 availableSkills: Option[]
 availableInterests: Option[]

 setAvailableSkills: (skills: Option[]) => void
 setAvailableInterests: (interests: Option[]) => void
 setActiveTab: (tab: "similarity" | "complementarity") => void

 updateForm: (data: Partial<RecommenderFormState>) => void
 getForm: () => RecommenderFormState
}

export const useRecommenderStore = create<RecommenderState>((set, get) => ({
 similarity: { skills: [], interests: [] },
 complementarity: { skills: [], interests: [], projectSkills: [] },
 activeTab: "similarity",

 availableSkills: [],
 availableInterests: [],

 setAvailableSkills: (availableSkills) => set({ availableSkills }),
 setAvailableInterests: (availableInterests) => set({ availableInterests }),

 setActiveTab: (tab) => set({ activeTab: tab }),

 updateForm: (data) => {
  const { activeTab } = get()
  set((state) => ({
   [activeTab]: { ...state[activeTab], ...data }
  }))
 },

 getForm: () => {
  const { activeTab, similarity, complementarity } = get()
  return activeTab === "similarity" ? similarity : complementarity
 },
}))
