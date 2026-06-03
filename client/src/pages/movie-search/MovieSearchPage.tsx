import { Filter, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { MovieFilters, MovieSort } from "../../entities/movie/types";
import { useDebouncedValue } from "../../shared/hooks/useDebouncedValue";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import {
  controlFieldClass,
  controlLabelClass,
  cx,
  panelClass,
  rangeInputClass,
  screenClass,
  textInputClass,
} from "../../shared/ui/classes";
import { MovieDetailPanel } from "./components/MovieDetailPanel";
import { MovieGrid } from "./components/MovieGrid";
import { useMovieSearch } from "./hooks/useMovieSearch";

const sortOptions: Array<{ label: string; value: MovieSort }> = [
  { label: "Popularity", value: "popularity" },
  { label: "Rating", value: "rating" },
  { label: "Revenue", value: "revenue" },
  { label: "Year", value: "year" },
];

const searchScreenBackdropClass =
  "before:fixed before:inset-[74px_0_0] before:z-[-2] before:bg-[radial-gradient(circle_at_76%_18%,rgba(85,214,194,0.13),transparent_28%),linear-gradient(90deg,rgba(14,13,11,0.96),rgba(25,20,14,0.78),rgba(14,13,11,0.98))] before:bg-cover before:bg-center before:opacity-[0.74] before:saturate-[0.85] before:content-[''] after:pointer-events-none after:fixed after:inset-[74px_0_0] after:z-[-1] after:bg-[linear-gradient(180deg,transparent,rgba(14,13,11,0.72)_42%,rgba(14,13,11,1)_92%),repeating-linear-gradient(90deg,rgba(255,255,255,0.03)_0_1px,transparent_1px_52px)] after:content-['']";

type MovieSearchPageProps = {
  onRecommend: () => void;
};

export function MovieSearchPage({ onRecommend }: MovieSearchPageProps) {
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [language, setLanguage] = useState("");
  const [minRating, setMinRating] = useState(3.4);
  const [sort, setSort] = useState<MovieSort>("popularity");
  const [selectedMovieId, setSelectedMovieId] = useState<number | string | null>(null);
  const debouncedSearch = useDebouncedValue(search);

  const filters: MovieFilters = useMemo(
    () => ({
      search: debouncedSearch,
      genre,
      language,
      minRating,
      sort,
    }),
    [debouncedSearch, genre, language, minRating, sort],
  );

  const { movies: filteredMovies, isLoading, errorMessage } = useMovieSearch(filters);

  const selectedMovie = filteredMovies.find((movie) => movie.id === selectedMovieId) ?? filteredMovies[0];

  useEffect(() => {
    if (filteredMovies.length > 0 && !filteredMovies.some((movie) => movie.id === selectedMovieId)) {
      setSelectedMovieId(filteredMovies[0].id);
    }
  }, [filteredMovies, selectedMovieId]);

  return (
    <section className={cx(screenClass, searchScreenBackdropClass)}>
      <SectionHeader
        title="Search movies, genres, tags"
        description="Search controls are ready for real backend data. Until an endpoint responds, this page only shows connection guidance."
      />

      <div className="grid grid-cols-[250px_minmax(0,1fr)_minmax(320px,400px)] items-start gap-[18px] max-[1180px]:grid-cols-[220px_minmax(0,1fr)] max-[900px]:grid-cols-1">
        <aside
          className={cx(
            panelClass,
            "sticky top-24 grid gap-[18px] p-[18px] max-[900px]:static max-[900px]:grid-cols-2 max-[640px]:grid-cols-1",
          )}
          aria-label="Movie filters"
        >
          <div className="flex items-center gap-[9px] font-bold text-cinema-text max-[900px]:col-span-full">
            <Filter size={17} strokeWidth={2} />
            Filters
          </div>

          <label className={controlFieldClass}>
            <span className={controlLabelClass}>Genre</span>
            <input className={textInputClass} value={genre} onChange={(event) => setGenre(event.target.value)} placeholder="Example: Drama" />
          </label>

          <label className={controlFieldClass}>
            <span className={controlLabelClass}>Language</span>
            <input
              className={textInputClass}
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              placeholder="Example: en / zh"
            />
          </label>

          <label className={controlFieldClass}>
            <span className={controlLabelClass}>Minimum rating</span>
            <input
              className={rangeInputClass}
              type="range"
              min="0"
              max="5"
              step="0.1"
              value={minRating}
              onChange={(event) => setMinRating(Number(event.target.value))}
            />
            <strong className="text-[0.9rem] text-cinema-amber">{minRating.toFixed(1)}</strong>
          </label>

          <div className={controlFieldClass}>
            <span className={controlLabelClass}>Sort</span>
            <div className="grid grid-cols-2 gap-[7px]">
              {sortOptions.map((item) => (
                <button
                  key={item.value}
                  className={cx(
                    "min-h-9 rounded-lg border-0 bg-cinema-surface text-[0.8rem] text-cinema-soft transition-colors duration-[220ms] ease-linear",
                    sort === item.value && "bg-[rgba(242,177,92,0.18)] text-cinema-amber",
                  )}
                  data-selected={sort === item.value}
                  type="button"
                  onClick={() => setSort(item.value)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <div className="min-w-0">
          <div className="mb-[18px] grid min-h-[62px] grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-[18px] border border-[rgba(244,239,228,0.18)] bg-[rgba(255,255,255,0.075)] px-[18px] shadow-[0_18px_80px_rgba(0,0,0,0.24)] backdrop-blur-[18px] max-[640px]:grid-cols-[auto_minmax(0,1fr)]">
            <Search size={19} strokeWidth={2} aria-hidden="true" />
            <input
              className="min-w-0 border-0 bg-transparent text-[clamp(1rem,1.4vw,1.28rem)] text-cinema-text outline-none"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search movies, genres, tags"
              aria-label="Search movies"
            />
            <span className="whitespace-nowrap text-[0.85rem] text-cinema-muted max-[640px]:col-span-full max-[640px]:pb-3">
              {isLoading ? "Loading" : `${filteredMovies.length} results`}
            </span>
          </div>

          {errorMessage ? (
            <ConnectionNotice
              title="Waiting for movie search API"
              message={errorMessage}
              actionHint="Suggested endpoint: GET /movies?search=&genre=&language=&minRating=&sort="
            />
          ) : (
            <MovieGrid movies={filteredMovies} selectedMovieId={selectedMovie?.id ?? null} onSelectMovie={setSelectedMovieId} />
          )}
        </div>

        <MovieDetailPanel movie={selectedMovie} onRecommend={onRecommend} />
      </div>
    </section>
  );
}
