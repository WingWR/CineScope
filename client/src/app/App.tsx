import { useState } from "react";
import type { Movie } from "../entities/movie/types";
import { AppShell } from "./layout/AppShell";
import { MovieSearchPage } from "../pages/movie-search/MovieSearchPage";
import { RecommendationPage } from "../pages/recommendation/RecommendationPage";
import { VisualizationPage } from "../pages/visualization/VisualizationPage";

export type AppView = "search" | "recommend" | "atlas";

export function App() {
  const [activeView, setActiveView] = useState<AppView>("search");
  const [recommendationSeed, setRecommendationSeed] = useState<Movie | null>(null);

  const openRecommendationsForMovie = (movie: Movie) => {
    setRecommendationSeed(movie);
    setActiveView("recommend");
  };

  return (
    <AppShell activeView={activeView} onViewChange={setActiveView}>
      {activeView === "search" ? <MovieSearchPage onRecommend={openRecommendationsForMovie} /> : null}
      {activeView === "recommend" ? <RecommendationPage initialSeedMovie={recommendationSeed} /> : null}
      {activeView === "atlas" ? <VisualizationPage /> : null}
    </AppShell>
  );
}
