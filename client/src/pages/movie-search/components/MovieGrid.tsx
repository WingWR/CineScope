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
      <div className="empty-state">
        <strong>No matching films</strong>
        <span>This appears when the backend returns an empty list. Check the search filters or data source.</span>
      </div>
    );
  }

  return (
    <div className="movie-grid" aria-label="Movie results">
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
