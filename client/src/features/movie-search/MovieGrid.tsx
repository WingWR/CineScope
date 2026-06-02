import type { Movie } from "../../entities/movie/types";
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
        <span>接口返回空数组时会显示这里。请确认后端搜索条件或数据源。</span>
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
