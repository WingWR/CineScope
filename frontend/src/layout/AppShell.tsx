import {
  BarChart3,
  Clapperboard,
  Compass,
  Film,
  Library,
  Search,
  Sparkles,
  Tags,
} from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Overview', icon: BarChart3 },
  { to: '/movies', label: 'Movies', icon: Film },
  { to: '/genres', label: 'Genres', icon: Tags },
  { to: '/recommendations', label: 'Recommendations', icon: Sparkles },
  { to: '/about-data', label: 'Data', icon: Library },
]

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" className="brand" aria-label="CineScope overview">
          <span className="brand__mark" aria-hidden="true">
            <Clapperboard size={24} strokeWidth={2.4} />
          </span>
          <span>
            <strong>CineScope</strong>
            <small>Movie Intelligence</small>
          </span>
        </NavLink>

        <nav className="nav" aria-label="Primary navigation">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav__item${isActive ? ' nav__item--active' : ''}`}
            >
              <Icon size={18} strokeWidth={2.2} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar__status">
          <Compass size={18} aria-hidden="true" />
          <span>API Standby</span>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div className="topbar__search" aria-hidden="true">
            <Search size={18} />
            <span>Search API pending</span>
          </div>
          <div className="topbar__status">Service standby</div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
