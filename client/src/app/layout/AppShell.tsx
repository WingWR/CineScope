import { BarChart3, Clapperboard, Database, HeartHandshake, Search, Wifi } from "lucide-react";
import type { PropsWithChildren } from "react";
import type { AppView } from "../App";

type NavItem = {
  id: AppView;
  label: string;
  icon: typeof Search;
};

const navItems: NavItem[] = [
  { id: "search", label: "Search", icon: Search },
  { id: "recommend", label: "Recommend", icon: HeartHandshake },
  { id: "atlas", label: "Atlas", icon: BarChart3 },
];

type AppShellProps = PropsWithChildren<{
  activeView: AppView;
  onViewChange: (view: AppView) => void;
}>;

export function AppShell({ activeView, onViewChange, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand-mark" type="button" onClick={() => onViewChange("search")} aria-label="Open search">
          <span className="brand-icon" aria-hidden="true">
            <Clapperboard size={20} strokeWidth={2.2} />
          </span>
          <span>
            <strong>CineScope</strong>
          </span>
        </button>

        <nav className="topnav" aria-label="Main navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const selected = activeView === item.id;

            return (
              <button
                className="nav-button"
                data-selected={selected}
                key={item.id}
                type="button"
                onClick={() => onViewChange(item.id)}
                aria-current={selected ? "page" : undefined}
              >
                <Icon size={16} strokeWidth={2.1} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="service-strip" aria-label="Data status">
          <span className="status-pill">
            <Database size={14} strokeWidth={2} />
            API pending
          </span>
          <span className="status-pill status-pill--ready">
            <Wifi size={14} strokeWidth={2} />
            Awaiting backend
          </span>
        </div>
      </header>

      <main className="app-main">{children}</main>
    </div>
  );
}
