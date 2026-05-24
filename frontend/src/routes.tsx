import { createBrowserRouter } from 'react-router-dom'
import { AppShell } from './layout/AppShell'
import { DashboardPage } from './pages/DashboardPage'
import { DataAboutPage } from './pages/DataAboutPage'
import { GenresPage } from './pages/GenresPage'
import { MovieDetailPage } from './pages/MovieDetailPage'
import { MoviesPage } from './pages/MoviesPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { RecommendationsPage } from './pages/RecommendationsPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'movies', element: <MoviesPage /> },
      { path: 'movies/:movieId', element: <MovieDetailPage /> },
      { path: 'genres', element: <GenresPage /> },
      { path: 'recommendations', element: <RecommendationsPage /> },
      { path: 'about-data', element: <DataAboutPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
