import { Bot, Film, Layers3, ListFilter, MessageSquareText, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { Movie, RecommendationMode, RecommendationRequest } from "../../entities/movie/types";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import {
  controlFieldClass,
  controlLabelClass,
  cx,
  panelClass,
  primaryActionClass,
  screenClass,
  textInputClass,
} from "../../shared/ui/classes";
import { MovieDetailPanel } from "../movie-search/components/MovieDetailPanel";
import { RecommendationCard } from "./components/RecommendationCard";
import { useRecommendations } from "./hooks/useRecommendations";

const modes: Array<{ value: RecommendationMode; label: string; icon: typeof Film }> = [
  { value: "content", label: "Content", icon: Film },
  { value: "collaborative", label: "Collaborative", icon: Layers3 },
  { value: "agent-ready", label: "Agent", icon: Bot },
];

const DEFAULT_RECOMMENDATION_USER_ID = "1";
const DEFAULT_RECOMMENDATION_TOP_K = 6;

type RecommendationPageProps = {
  initialSeedMovie?: Movie | null;
};

export function RecommendationPage({ initialSeedMovie }: RecommendationPageProps) {
  const [mode, setMode] = useState<RecommendationMode>("agent-ready");
  const [prompt, setPrompt] = useState("");
  const [seedMovieName, setSeedMovieName] = useState("");
  const [topK, setTopK] = useState(DEFAULT_RECOMMENDATION_TOP_K);
  const [submittedRequest, setSubmittedRequest] = useState<RecommendationRequest | null>(null);
  const [selectedMovieId, setSelectedMovieId] = useState<number | string | null>(null);

  const draftRequest: RecommendationRequest = useMemo(
    () => ({
      mode,
      prompt: mode === "agent-ready" ? prompt : "",
      seedMovieName,
      userId: DEFAULT_RECOMMENDATION_USER_ID,
      topK,
    }),
    [mode, prompt, seedMovieName, topK],
  );

  const { items, isLoading, errorMessage } = useRecommendations(submittedRequest);
  const isAgentMode = mode === "agent-ready";
  const selectedMovie = items.find((item) => item.movie.id === selectedMovieId)?.movie;

  useEffect(() => {
    if (!initialSeedMovie) {
      return;
    }

    const seedRequest: RecommendationRequest = {
      mode: "content",
      prompt: "",
      seedMovieName: initialSeedMovie.title,
      userId: DEFAULT_RECOMMENDATION_USER_ID,
      topK: DEFAULT_RECOMMENDATION_TOP_K,
    };

    setMode("content");
    setPrompt("");
    setSeedMovieName(initialSeedMovie.title);
    setTopK(DEFAULT_RECOMMENDATION_TOP_K);
    setSubmittedRequest(seedRequest);
    setSelectedMovieId(initialSeedMovie.id);
  }, [initialSeedMovie?.id, initialSeedMovie?.title]);

  useEffect(() => {
    if (items.length === 0) {
      setSelectedMovieId(null);
      return;
    }

    if (!items.some((item) => item.movie.id === selectedMovieId)) {
      setSelectedMovieId(items[0].movie.id);
    }
  }, [items, selectedMovieId]);

  const requestRecommendations = (request: RecommendationRequest) => {
    setSubmittedRequest(request);
    setSelectedMovieId(null);
  };

  const recommendFromMovie = (movie: Movie) => {
    const seedRequest: RecommendationRequest = {
      mode: "content",
      prompt: "",
      seedMovieName: movie.title,
      userId: DEFAULT_RECOMMENDATION_USER_ID,
      topK,
    };

    setMode("content");
    setPrompt("");
    setSeedMovieName(movie.title);
    setSubmittedRequest(seedRequest);
    setSelectedMovieId(movie.id);
  };

  return (
    <section className={screenClass}>
      <SectionHeader
        title="Recommend"
        description="Use a simple recommendation request. Agent mode adds one natural-language brief; other modes stay parameter based."
      />

      <div className="grid grid-cols-[minmax(0,1fr)_minmax(320px,400px)] items-start gap-[18px] max-[1180px]:grid-cols-1">
        <div className="grid gap-4">
          <div className={cx(panelClass, "grid gap-4 p-[18px]")}>
            <div className="grid grid-cols-3 gap-2 max-[640px]:grid-cols-1" aria-label="Recommendation mode">
              {modes.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    className={cx(
                      "inline-flex min-h-9 min-w-0 items-center justify-center gap-2 whitespace-nowrap rounded-lg border border-[rgba(244,239,228,0.14)] bg-cinema-surface px-2.5 text-[0.9rem] text-cinema-soft transition-[background,border-color,box-shadow,color,transform] duration-[220ms] ease-linear hover:border-[rgba(190,132,54,0.62)] hover:text-cinema-text",
                      mode === item.value &&
                        "border-[rgba(190,132,54,0.9)] bg-[rgba(190,132,54,0.24)] text-cinema-amber-strong shadow-[0_0_0_1px_rgba(190,132,54,0.28),0_10px_26px_rgba(190,132,54,0.14)] hover:border-[rgba(190,132,54,0.9)] hover:text-cinema-amber-strong",
                    )}
                    data-selected={mode === item.value}
                    key={item.value}
                    type="button"
                    onClick={() => setMode(item.value)}
                  >
                    <Icon size={16} />
                    {item.label}
                  </button>
                );
              })}
            </div>

            {isAgentMode ? (
              <div className="grid gap-3 rounded-xl border border-cinema-border bg-[rgba(255,255,255,0.045)] p-3.5">
                <div className="flex items-center gap-2 text-[0.82rem] font-[760] uppercase text-cinema-amber">
                  <MessageSquareText size={18} />
                  <span>Agent brief</span>
                </div>
                <textarea
                  className="min-h-[132px] resize-y rounded-lg border border-cinema-border bg-cinema-surface p-3.5 leading-[1.55] text-cinema-text outline-none focus:border-[rgba(242,177,92,0.48)] focus:shadow-[0_0_0_3px_rgba(242,177,92,0.12)]"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Example: I want a fast-paced sci-fi movie for a weekend night, not too dark, with strong ratings."
                  aria-label="Agent recommendation prompt"
                />
              </div>
            ) : null}

            <div className="grid grid-cols-[minmax(0,1fr)_minmax(140px,0.28fr)] gap-3 max-[640px]:grid-cols-1">
              <label className={controlFieldClass}>
                <span className={controlLabelClass}>Seed movie</span>
                <input
                  className={textInputClass}
                  value={seedMovieName}
                  onChange={(event) => setSeedMovieName(event.target.value)}
                  placeholder="Optional seed title"
                />
              </label>

              <label className={controlFieldClass}>
                <span className={controlLabelClass}>Top K</span>
                <input
                  className={textInputClass}
                  type="number"
                  min="1"
                  max="50"
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                />
              </label>
            </div>

            <button
              className={cx(primaryActionClass, "min-w-[220px] justify-self-end max-[640px]:w-full max-[640px]:justify-self-stretch")}
              type="button"
              onClick={() => requestRecommendations(draftRequest)}
            >
              Request recommendations
              <Sparkles size={16} />
            </button>
          </div>

          <div className="grid gap-3" aria-busy={isLoading}>
            <div className="flex min-h-9 items-center gap-[9px] font-bold text-cinema-soft">
              <ListFilter size={17} />
              <span>{isLoading ? "Waiting for backend response" : `${items.length} recommendations`}</span>
            </div>

            {errorMessage ? (
              <ConnectionNotice
                title="Waiting for recommendation API"
                message={errorMessage}
                actionHint="Suggested endpoint: POST /recommendations with the recommendation payload."
              />
            ) : null}

            {!errorMessage && !submittedRequest ? (
              <ConnectionNotice
                title="No recommendation request yet"
                message="Choose a mode, fill the minimal request fields, then submit. Agent mode is the only mode with a text brief."
              />
            ) : null}

            {!errorMessage && submittedRequest && items.length === 0 ? (
              <ConnectionNotice
                title="No returned recommendations"
                message="The backend returned an empty list. Results will appear here when the API returns RecommendationItem objects."
              />
            ) : null}

            {items.map((item, index) => (
              <RecommendationCard
                item={item}
                index={index}
                key={item.movie.id}
                selected={item.movie.id === selectedMovie?.id}
                onSelect={() => setSelectedMovieId(item.movie.id)}
              />
            ))}
          </div>
        </div>

        <MovieDetailPanel movie={selectedMovie} onRecommend={recommendFromMovie} showEmptyActionHint={false} />
      </div>
    </section>
  );
}
