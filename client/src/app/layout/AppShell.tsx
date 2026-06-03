import { BarChart3, Clapperboard, Database, HeartHandshake, Search, Wifi } from "lucide-react";
import type { PropsWithChildren } from "react";
import { cx } from "../../shared/ui/classes";
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
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 grid min-h-[74px] grid-cols-[minmax(160px,1fr)_auto_minmax(180px,1fr)] items-center gap-[18px] border-b border-[rgba(244,239,228,0.1)] bg-[rgba(14,13,11,0.78)] px-[clamp(18px,3vw,40px)] py-3.5 backdrop-blur-[22px] max-[900px]:grid-cols-1 max-[900px]:gap-2.5">
        <button
          className="inline-flex min-h-[42px] items-center justify-self-start gap-2.5 border-0 bg-transparent p-0 text-cinema-text tracking-normal max-[900px]:justify-self-center"
          type="button"
          onClick={() => onViewChange("search")}
          aria-label="Open search"
        >
          <span
            className="grid size-10 place-items-center rounded-lg border border-[rgba(242,177,92,0.36)] bg-[linear-gradient(160deg,rgba(242,177,92,0.3),rgba(242,177,92,0.08))] text-cinema-amber"
            aria-hidden="true"
          >
            <Clapperboard size={20} strokeWidth={2.2} />
          </span>
          <span>
            <strong className="text-base font-[720]">CineScope</strong>
          </span>
        </button>

        <nav
          className="inline-flex gap-1.5 rounded-xl border border-cinema-border bg-[rgba(255,255,255,0.045)] p-[5px] max-[900px]:justify-self-center max-[640px]:w-full"
          aria-label="Main navigation"
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const selected = activeView === item.id;

            return (
              <button
                className={cx(
                  "inline-flex min-h-9 items-center justify-center gap-2 rounded-lg border-0 bg-transparent px-3.5 text-[0.9rem] text-cinema-soft transition-[background,color,transform] duration-[220ms] ease-linear hover:bg-[rgba(255,255,255,0.08)] hover:text-cinema-text max-[640px]:flex-1 max-[640px]:px-2",
                  selected && "bg-[rgba(242,177,92,0.16)] text-cinema-amber-strong hover:text-cinema-amber-strong",
                )}
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

        <div className="inline-flex justify-end gap-2 max-[900px]:justify-self-center max-[640px]:w-full" aria-label="Data status">
          <span className="inline-flex min-h-[34px] items-center gap-[7px] whitespace-nowrap rounded-lg border border-cinema-border bg-[rgba(255,255,255,0.045)] px-[11px] text-[0.82rem] text-cinema-soft max-[640px]:flex-1 max-[640px]:justify-center">
            <Database size={14} strokeWidth={2} />
            API pending
          </span>
          <span className="inline-flex min-h-[34px] items-center gap-[7px] whitespace-nowrap rounded-lg border border-[rgba(85,214,194,0.26)] bg-[rgba(255,255,255,0.045)] px-[11px] text-[0.82rem] text-cinema-teal max-[640px]:flex-1 max-[640px]:justify-center">
            <Wifi size={14} strokeWidth={2} />
            Awaiting backend
          </span>
        </div>
      </header>

      <main className="p-[clamp(18px,2.4vw,34px)] max-[640px]:p-3.5">{children}</main>
    </div>
  );
}
