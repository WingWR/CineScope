import { Filter, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { MovieFilters, MovieSort } from "../../entities/movie/types";
import { useDebouncedValue } from "../../shared/hooks/useDebouncedValue";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import { MovieDetailPanel } from "./MovieDetailPanel";
import { MovieGrid } from "./MovieGrid";
import { useMovieSearch } from "./useMovieSearch";

const sortOptions: Array<{ label: string; value: MovieSort }> = [
  { label: "Popularity", value: "popularity" },
  { label: "Rating", value: "rating" },
  { label: "Revenue", value: "revenue" },
  { label: "Year", value: "year" },
];

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
    <section className="screen search-screen">
      <SectionHeader
        title="Search movies, genres, tags"
        description="Search controls are ready for real backend data. Until an endpoint responds, this page only shows connection guidance."
      />

      <div className="search-workspace">
        <aside className="filter-rail" aria-label="Movie filters">
          <div className="filter-rail__title">
            <Filter size={17} strokeWidth={2} />
            Filters
          </div>

          <label className="control-field">
            <span>Genre</span>
            <input value={genre} onChange={(event) => setGenre(event.target.value)} placeholder="例如 Drama" />
          </label>

          <label className="control-field">
            <span>Language</span>
            <input value={language} onChange={(event) => setLanguage(event.target.value)} placeholder="例如 en / zh" />
          </label>

          <label className="control-field">
            <span>Minimum rating</span>
            <input
              type="range"
              min="0"
              max="5"
              step="0.1"
              value={minRating}
              onChange={(event) => setMinRating(Number(event.target.value))}
            />
            <strong>{minRating.toFixed(1)}</strong>
          </label>

          <div className="control-field">
            <span>Sort</span>
            <div className="segmented-options">
              {sortOptions.map((item) => (
                <button
                  key={item.value}
                  className="segmented-options__item"
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

        <div className="search-results">
          <div className="search-input-row">
            <Search size={19} strokeWidth={2} aria-hidden="true" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search movies, genres, tags"
              aria-label="Search movies"
            />
            <span>{isLoading ? "Loading" : `${filteredMovies.length} results`}</span>
          </div>

          {errorMessage ? (
            <ConnectionNotice
              title="等待电影搜索接口"
              message={errorMessage}
              actionHint="建议接口：GET /movies?search=&genre=&language=&minRating=&sort="
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
