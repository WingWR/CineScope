import type { Movie } from "../../../entities/movie/types";
import { MoviePosterCard } from "./MoviePosterCard";

type MovieGridProps = {
  movies: Movie[];
  selectedMovieId: Movie["id"] | null;
  onSelectMovie: (movieId: Movie["id"]) => void;
};

export function MovieGrid({ movies, selectedMovieId, onSelectMovie }: MovieGridProps) {
  if (movies.length === 0) {
    return (
      <div className="grid min-h-[280px] place-items-center rounded-[18px] border border-cinema-border bg-[rgba(255,255,255,0.045)] p-7 text-center text-cinema-soft">
        <strong className="text-cinema-text">No matching films</strong>
        <span>This appears when the backend returns an empty list. Check the search filters or data source.</span>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(144px,1fr))] gap-4 max-[640px]:grid-cols-2" aria-label="Movie results">
      {movies.map((movie, index) => (
        <MoviePosterCard
          index={index}
          key={movie.id}
          movie={movie}
          selected={movie.id === selectedMovieId}
          onSelect={() => onSelectMovie(movie.id)}
        />
      ))}
    </div>
  );
}
