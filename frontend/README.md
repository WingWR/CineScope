# CineScope Frontend

React + TypeScript frontend for the CineScope movie catalog and recommendation interface.

## Stack

- Vite
- React 19
- TypeScript
- React Compiler
- React Router
- lucide-react

## Run

```powershell
npm install
npm run dev
```

## Build Checks

```powershell
npm run lint
npm run build
```

## API Configuration

The frontend does not load local CSV files and does not ship mock movie data.

Set the backend base URL when the API is ready:

```powershell
$env:VITE_API_BASE_URL="http://localhost:8000"
npm run dev
```

Current reserved API modules:

- `src/api/movies.ts`
- `src/api/stats.ts`
- `src/api/recommendations.ts`

When `VITE_API_BASE_URL` is not configured, pages render empty states that reserve space for backend data.
