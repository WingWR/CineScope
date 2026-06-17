import {
  BarChart3,
  BrainCircuit,
  DollarSign,
  Film,
  Layers,
  Pencil,
  Search,
  Sparkles,
  Target,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { Movie } from "../../entities/movie/types";
import { useDebouncedValue } from "../../shared/hooks/useDebouncedValue";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { MetricTile } from "../../shared/ui/MetricTile";
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
import { useMovieSearch } from "../movie-search/hooks/useMovieSearch";
import { useRevenuePrediction } from "./hooks/useRevenuePrediction";

type PredictMode = "search" | "custom";

// ── hardcoded fallback genres & languages (when schema fetch fails) ──
const FALLBACK_GENRES = [
  "Action", "Adventure", "Animation", "Children", "Comedy", "Crime",
  "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "IMAX",
  "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
];

const FALLBACK_LANGUAGES = [
  "en", "fr", "de", "es", "it", "ja", "zh", "ko", "ru", "pt", "hi", "ar",
];

const DEFAULT_VALUES: Record<string, number> = {
  budget: 14_000_000,
  movie_year: 2024,
  runtime_minutes: 105,
  tmdb_popularity: 2.7,
  rating_mean: 3.3,
  rating_median: 3.5,
  rating_count: 5,
  tag_count: 0,
};

// ── Props ──
type RevenuePredictionPageProps = {
  initialSeedMovie?: Movie | null;
};

// ── Page ──
export function RevenuePredictionPage({ initialSeedMovie }: RevenuePredictionPageProps) {
  const { schema, result, isLoading, isSchemaLoading, errorMessage, predict } =
    useRevenuePrediction();

  const [mode, setMode] = useState<PredictMode>("search");
  const [movieName, setMovieName] = useState("");
  const [submittedName, setSubmittedName] = useState("");

  // Custom form state
  const [customFields, setCustomFields] = useState<Record<string, string>>(() =>
    Object.fromEntries(
      Object.entries(DEFAULT_VALUES).map(([k, v]) => [k, String(v)]),
    ),
  );
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [genreSearch, setGenreSearch] = useState("");

  // Quick-search for autocomplete
  const debouncedSearch = useDebouncedValue(movieName.length >= 2 ? movieName : "");
  const { movies: suggestions } = useMovieSearch({
    search: debouncedSearch,
    page: 1,
    pageSize: 5,
  });

  const showSuggestions = mode === "search" && movieName.length >= 2 && suggestions.length > 0;

  // Available genres/languages (from schema or fallback)
  const availableGenres = schema?.genres ?? FALLBACK_GENRES;
  const availableLanguages = schema?.languages ?? FALLBACK_LANGUAGES;

  // Filter genres by search
  const filteredGenres = useMemo(() => {
    const q = genreSearch.trim().toLowerCase();
    if (!q) return availableGenres;
    return availableGenres.filter((g) => g.toLowerCase().includes(q));
  }, [availableGenres, genreSearch]);

  // ── Handle seed movie from search page ──
  useEffect(() => {
    if (!initialSeedMovie?.title) return;
    setMode("search");
    setMovieName(initialSeedMovie.title);
    setSubmittedName(initialSeedMovie.title);
    predict({ movieName: initialSeedMovie.title });
  }, [initialSeedMovie?.title]);

  // ── Submit handlers ──
  const handleSearchSubmit = () => {
    const trimmed = movieName.trim();
    if (!trimmed) return;
    setSubmittedName(trimmed);
    predict({ movieName: trimmed });
  };

  const handleCustomSubmit = () => {
    const features: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(customFields)) {
      const num = Number(val);
      features[key] = isNaN(num) ? val : num;
    }
    features.genres = selectedGenres;
    features.original_language = selectedLanguage;
    predict({ features });
  };

  const selectSuggestion = (title: string) => {
    setMovieName(title);
    setSubmittedName(title);
    predict({ movieName: title });
  };

  const toggleGenre = (genre: string) => {
    setSelectedGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre],
    );
  };

  const hasResult = result !== null;
  const hasActualRevenue = hasResult && result.actualRevenue !== null;

  // ── Render ──
  return (
    <section className={screenClass}>
      <SectionHeader
        title="Revenue Prediction"
        description="Predict box-office revenue using the XGBoost + LightGBM ensemble. Search an existing movie or enter custom features."
      />

      <div className="grid grid-cols-[310px_minmax(0,1fr)] items-start gap-[18px] max-[980px]:grid-cols-1">
        {/* ══════ Left Sidebar ══════ */}
        <aside className={cx(panelClass, "sticky top-24 grid gap-4 p-[18px] max-[980px]:static")} aria-label="Prediction controls">
          {/* Mode toggle */}
          <div className="grid grid-cols-2 gap-1.5 rounded-lg border border-cinema-border bg-cinema-surface p-1">
            <button
              className={cx(
                "inline-flex min-h-9 items-center justify-center gap-2 rounded-md text-[0.86rem] transition-colors",
                mode === "search"
                  ? "bg-[rgba(242,177,92,0.18)] text-cinema-amber-strong font-[700]"
                  : "text-cinema-soft hover:text-cinema-text",
              )}
              type="button"
              onClick={() => setMode("search")}
            >
              <Search size={14} /> Search
            </button>
            <button
              className={cx(
                "inline-flex min-h-9 items-center justify-center gap-2 rounded-md text-[0.86rem] transition-colors",
                mode === "custom"
                  ? "bg-[rgba(85,214,194,0.18)] text-cinema-teal font-[700]"
                  : "text-cinema-soft hover:text-cinema-text",
              )}
              type="button"
              onClick={() => setMode("custom")}
            >
              <Pencil size={14} /> Custom
            </button>
          </div>

          {/* ── Search mode form ── */}
          {mode === "search" ? (
            <>
              <label className={controlFieldClass}>
                <span className={controlLabelClass}>Movie name</span>
                <div className="relative">
                  <input
                    className={cx(textInputClass, "pr-10")}
                    value={movieName}
                    onChange={(e) => {
                      setMovieName(e.target.value);
                      setSubmittedName("");
                    }}
                    onKeyDown={(e) => { if (e.key === "Enter") handleSearchSubmit(); }}
                    placeholder="e.g. Toy Story, Inception…"
                    aria-label="Movie name to predict"
                  />
                  <Search size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-cinema-muted" />
                </div>
              </label>

              {showSuggestions ? (
                <div className="-mt-2 rounded-lg border border-cinema-border bg-cinema-surface px-1 py-1">
                  {suggestions.slice(0, 5).map((movie) => (
                    <button
                      key={movie.id}
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-[0.88rem] text-cinema-soft transition-colors hover:bg-[rgba(242,177,92,0.12)] hover:text-cinema-text"
                      type="button"
                      onClick={() => selectSuggestion(movie.title)}
                    >
                      <Film size={14} className="shrink-0 text-cinema-muted" />
                      <span className="min-w-0 truncate">{movie.title}</span>
                      {movie.year ? <span className="shrink-0 text-[0.78rem] text-cinema-muted">{movie.year}</span> : null}
                    </button>
                  ))}
                </div>
              ) : null}

              <button className={cx(primaryActionClass, "min-h-[46px] w-full")} type="button" onClick={handleSearchSubmit} disabled={!movieName.trim() || isLoading}>
                {isLoading ? "Predicting…" : "Predict Revenue"}
                <Sparkles size={16} />
              </button>
            </>
          ) : null}

          {/* ── Custom mode form ── */}
          {mode === "custom" ? (
            <div className="grid gap-3">
              {isSchemaLoading ? (
                <p className="m-0 text-[0.84rem] text-cinema-muted">Loading feature schema…</p>
              ) : null}

              {/* Numeric fields */}
              {[
                { key: "budget", label: "Budget (USD)", placeholder: "14000000" },
                { key: "movie_year", label: "Release Year", placeholder: "2024" },
                { key: "runtime_minutes", label: "Runtime (min)", placeholder: "105" },
                { key: "tmdb_popularity", label: "TMDb Popularity", placeholder: "2.7" },
                { key: "rating_mean", label: "Avg Rating (0–5)", placeholder: "3.3" },
                { key: "rating_median", label: "Median Rating", placeholder: "3.5" },
                { key: "rating_count", label: "Rating Count", placeholder: "5" },
                { key: "tag_count", label: "Tag Count", placeholder: "0" },
              ].map(({ key, label, placeholder }) => {
                const schemaField = schema?.numericFields?.find((f) => f.name === key);
                const tooltip = schemaField?.description ?? "";
                return (
                  <label key={key} className={controlFieldClass} title={tooltip}>
                    <span className={cx(controlLabelClass, "flex items-center justify-between")}>
                      {label}
                      {schemaField ? (
                        <span className="text-[0.7rem] font-normal text-cinema-muted">default {String(schemaField.defaultValue)}</span>
                      ) : null}
                    </span>
                    <input
                      className={textInputClass}
                      type="number"
                      value={customFields[key] ?? ""}
                      onChange={(e) => setCustomFields((prev) => ({ ...prev, [key]: e.target.value }))}
                      placeholder={placeholder}
                    />
                  </label>
                );
              })}

              {/* Language */}
              <label className={controlFieldClass}>
                <span className={controlLabelClass}>Language</span>
                <select
                  className={cx(textInputClass, "cursor-pointer")}
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                >
                  {availableLanguages.map((lang) => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
              </label>

              {/* Genres multi-select */}
              <div className={controlFieldClass}>
                <span className={controlLabelClass}>
                  Genres ({selectedGenres.length} selected)
                </span>
                <input
                  className={textInputClass}
                  value={genreSearch}
                  onChange={(e) => setGenreSearch(e.target.value)}
                  placeholder="Filter genres…"
                />
                <div className="max-h-[180px] overflow-y-auto rounded-lg border border-cinema-border bg-cinema-surface p-2">
                  <div className="flex flex-wrap gap-1.5">
                    {filteredGenres.map((genre) => {
                      const active = selectedGenres.includes(genre);
                      return (
                        <button
                          key={genre}
                          className={cx(
                            "inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[0.76rem] transition-colors",
                            active
                              ? "border-[rgba(242,177,92,0.5)] bg-[rgba(242,177,92,0.18)] text-cinema-amber-strong"
                              : "border-cinema-border text-cinema-soft hover:border-[rgba(255,255,255,0.2)]",
                          )}
                          type="button"
                          onClick={() => toggleGenre(genre)}
                        >
                          {active ? <X size={11} /> : null}
                          {genre}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              <button className={cx(primaryActionClass, "min-h-[46px] w-full")} type="button" onClick={handleCustomSubmit} disabled={isLoading}>
                {isLoading ? "Predicting…" : "Predict Revenue"}
                <Sparkles size={16} />
              </button>
            </div>
          ) : null}

          {/* Model info */}
          <div className="rounded-xl border border-[rgba(85,214,194,0.16)] bg-[rgba(85,214,194,0.05)] p-3.5">
            <div className="mb-2 flex items-center gap-2 text-[0.8rem] font-[760] uppercase text-cinema-teal">
              <Layers size={15} /> Ensemble
            </div>
            <p className="m-0 text-[0.82rem] leading-[1.55] text-cinema-soft">
              XGBoost 88% + LightGBM 12%. Trained on log₁ₚ revenue with {schema?.featureCount ?? 66} features.
            </p>
          </div>

          {/* Quick metrics */}
          {!hasResult && !isLoading && !errorMessage ? (
            <div className="rounded-xl border border-cinema-border bg-cinema-surface p-3.5">
              <div className="mb-2 flex items-center gap-2 text-[0.8rem] font-[760] uppercase text-cinema-muted">
                <BarChart3 size={15} /> Validation
              </div>
              <div className="grid gap-1.5 text-[0.82rem] text-cinema-soft">
                <div className="flex justify-between"><span>RMSE (log)</span><span className="text-cinema-amber">1.27</span></div>
                <div className="flex justify-between"><span>MAE (log)</span><span className="text-cinema-amber">0.86</span></div>
                <div className="flex justify-between"><span>R² (log)</span><span className="text-cinema-amber">0.65</span></div>
                <div className="flex justify-between"><span>Features</span><span className="text-cinema-amber">{schema?.featureCount ?? 66}</span></div>
              </div>
            </div>
          ) : null}
        </aside>

        {/* ══════ Main Content ══════ */}
        <div className="min-w-0">
          {errorMessage ? (
            <ConnectionNotice title="Prediction API unavailable" message={errorMessage} actionHint="POST /revenue/predict with { movieName } or { features }" />
          ) : null}

          {isLoading ? (
            <div className={cx(panelClass, "flex min-h-[380px] items-center justify-center p-8")}>
              <div className="grid justify-items-center gap-4 text-center">
                <div className="flex size-16 items-center justify-center rounded-full border-2 border-cinema-amber bg-[rgba(242,177,92,0.1)]">
                  <Zap size={28} className="animate-pulse text-cinema-amber" />
                </div>
                <div>
                  <p className="m-0 text-[1.05rem] font-[700] text-cinema-text">Running ensemble prediction…</p>
                  <p className="m-0 mt-1 text-[0.86rem] text-cinema-muted">
                    {mode === "search" ? `Processing "${submittedName}"` : "Processing custom features"}
                  </p>
                </div>
              </div>
            </div>
          ) : null}

          {!isLoading && !errorMessage && !hasResult ? (
            <ConnectionNotice
              title={mode === "search" ? "Search for a movie" : "Fill in custom features"}
              message={
                mode === "search"
                  ? "Type a movie title and click Predict Revenue."
                  : "Adjust the feature values in the sidebar and click Predict Revenue."
              }
            />
          ) : null}

          {hasResult ? (
            <div className="grid gap-4">
              {/* Movie identity */}
              <div className={cx(panelClass, "flex flex-wrap items-center gap-4 p-[18px]")}>
                <div className="flex size-14 items-center justify-center rounded-xl border border-[rgba(242,177,92,0.22)] bg-[rgba(242,177,92,0.08)]">
                  {mode === "custom" ? <Pencil size={26} className="text-cinema-teal" /> : <Film size={26} className="text-cinema-amber" />}
                </div>
                <div className="min-w-0 flex-1">
                  <h2 className="m-0 text-[1.35rem] font-[760] leading-[1.15] text-cinema-text">
                    {result.movieName}
                  </h2>
                  <p className="m-0 mt-[3px] text-[0.86rem] text-cinema-muted">
                    {result.movieYear ? `${result.movieYear} · ` : ""}
                    {mode === "custom" ? "Custom input" : `Movie #${result.movieId}`}
                  </p>
                </div>
                <div className="flex items-center gap-2 rounded-lg border border-[rgba(242,177,92,0.16)] bg-[rgba(242,177,92,0.06)] px-3 py-2 text-[0.8rem] text-cinema-amber">
                  <BrainCircuit size={14} /> {result.featureCount} features
                </div>
              </div>

              {/* Ensemble prediction */}
              <div className={cx(panelClass, "relative overflow-hidden p-[clamp(18px,2.4vw,28px)]")}>
                <div className="mb-2 flex items-center gap-2 text-[0.82rem] font-[760] uppercase text-cinema-amber">
                  <TrendingUp size={16} /> Ensemble
                </div>
                <strong className="block text-[clamp(2.6rem,4.8vw,3.8rem)] leading-[1.05] text-cinema-text">
                  {result.predictedRevenueFormatted}
                </strong>
                <p className="m-0 mt-1 text-[0.9rem] text-cinema-muted">
                  XGBoost ({Math.round(result.ensembleWeights.xgboost * 100)}%) + LightGBM (
                  {Math.round(result.ensembleWeights.lightgbm * 100)}%)
                </p>

                {hasActualRevenue ? (
                  <div className="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-[rgba(85,214,194,0.16)] bg-[rgba(85,214,194,0.05)] px-4 py-3">
                    <Target size={18} className="text-cinema-teal" />
                    <span className="text-[0.88rem] text-cinema-soft">
                      Actual: <strong className="text-cinema-teal">{result.actualRevenueFormatted}</strong>
                    </span>
                    <span className="rounded-md bg-[rgba(255,255,255,0.06)] px-2 py-0.5 text-[0.78rem] text-cinema-muted">
                      {result.actualRevenue! > result.predictedRevenue ? "Under-predicted" : "Over-predicted"} by{" "}
                      {formatDiffRatio(result.predictedRevenue, result.actualRevenue!)}
                    </span>
                  </div>
                ) : (
                  <div className="mt-4 flex items-center gap-2 rounded-xl border border-[rgba(242,177,92,0.1)] bg-[rgba(242,177,92,0.03)] px-4 py-2.5 text-[0.82rem] text-cinema-muted">
                    <DollarSign size={14} />
                    {mode === "custom" ? "Custom input — no actual revenue for comparison." : "Actual revenue not available for this film."}
                  </div>
                )}
              </div>

              {/* Individual models */}
              <div className="grid grid-cols-2 gap-3 max-[640px]:grid-cols-1">
                <div className={cx(panelClass, "p-[18px]")}>
                  <div className="mb-1 flex items-center gap-2 text-[0.8rem] font-[760] uppercase text-[#e07b4c]">
                    <Zap size={14} /> XGBoost
                  </div>
                  <strong className="block text-[1.8rem] leading-[1.1] text-cinema-text">{result.xgboostPredictedRevenueFormatted}</strong>
                  <span className="text-[0.8rem] text-cinema-muted">Weight: {Math.round(result.ensembleWeights.xgboost * 100)}%</span>
                </div>
                <div className={cx(panelClass, "p-[18px]")}>
                  <div className="mb-1 flex items-center gap-2 text-[0.8rem] font-[760] uppercase text-[#5eb89e]">
                    <Zap size={14} /> LightGBM
                  </div>
                  <strong className="block text-[1.8rem] leading-[1.1] text-cinema-text">{result.lightgbmPredictedRevenueFormatted}</strong>
                  <span className="text-[0.8rem] text-cinema-muted">Weight: {Math.round(result.ensembleWeights.lightgbm * 100)}%</span>
                </div>
              </div>

              {/* Metrics row */}
              <div className="grid grid-cols-3 gap-3 max-[640px]:grid-cols-1">
                <MetricTile label="RMSE (log)" value={result.modelMetrics.rmseLog.toFixed(3)} tone="amber" />
                <MetricTile label="MAE (log)" value={result.modelMetrics.maeLog.toFixed(3)} tone="teal" />
                <MetricTile label="R² (log)" value={(result.modelMetrics.r2Log * 100).toFixed(1) + "%"} tone="amber" />
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function formatDiffRatio(predicted: number, actual: number): string {
  if (actual === 0) return "—";
  const ratio = Math.abs(predicted - actual) / actual;
  if (ratio < 1) return `${(ratio * 100).toFixed(0)}%`;
  return `${ratio.toFixed(1)}×`;
}
