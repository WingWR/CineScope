import { useState } from "react";
import { AppShell } from "./layout/AppShell";
import { MovieSearchPage } from "../features/movie-search/MovieSearchPage";
import { RecommendationPage } from "../features/recommendation/RecommendationPage";
import { VisualizationPage } from "../features/visualization/VisualizationPage";

export type AppView = "search" | "recommend" | "atlas";

export function App() {
  const [activeView, setActiveView] = useState<AppView>("search");

  return (
    <AppShell activeView={activeView} onViewChange={setActiveView}>
      {activeView === "search" ? <MovieSearchPage onRecommend={() => setActiveView("recommend")} /> : null}
      {activeView === "recommend" ? <RecommendationPage /> : null}
      {activeView === "atlas" ? <VisualizationPage /> : null}
    </AppShell>
  );
}
