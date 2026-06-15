import { useState } from "react";
import type { Movie } from "../entities/movie/types";
import { AppShell } from "./layout/AppShell";
import { MovieSearchPage } from "../pages/movie-search/MovieSearchPage";
import { RecommendationPage } from "../pages/recommendation/RecommendationPage";
import { RevenuePredictionPage } from "../pages/revenue-prediction/RevenuePredictionPage";
import { VisualizationPage } from "../pages/visualization/VisualizationPage";

export type AppView = "search" | "recommend" | "predict" | "atlas";

export function App() {
  const [activeView, setActiveView] = useState<AppView>("search");
  const [recommendationSeed, setRecommendationSeed] = useState<Movie | null>(null);
  const [predictionSeed, setPredictionSeed] = useState<Movie | null>(null);

  const openRecommendationsForMovie = (movie: Movie) => {
    setRecommendationSeed(movie);
    setActiveView("recommend");
  };

  const openPredictionForMovie = (movie: Movie) => {
    setPredictionSeed(movie);
    setActiveView("predict");
  };

  return (
    <AppShell activeView={activeView} onViewChange={setActiveView}>
      {activeView === "search" ? (
        <MovieSearchPage
          onRecommend={openRecommendationsForMovie}
          onPredict={openPredictionForMovie}
        />
      ) : null}
      {activeView === "recommend" ? <RecommendationPage initialSeedMovie={recommendationSeed} /> : null}
      {activeView === "predict" ? <RevenuePredictionPage initialSeedMovie={predictionSeed} /> : null}
      {activeView === "atlas" ? <VisualizationPage /> : null}
    </AppShell>
  );
}
