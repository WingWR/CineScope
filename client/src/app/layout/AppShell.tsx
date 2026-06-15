import { BarChart3, HeartHandshake, Search, TrendingUp } from "lucide-react";
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
  { id: "predict", label: "Predict", icon: TrendingUp },
  { id: "atlas", label: "Atlas", icon: BarChart3 },
];

type AppShellProps = PropsWithChildren<{
  activeView: AppView;
  onViewChange: (view: AppView) => void;
}>;

export function AppShell({ activeView, onViewChange, children }: AppShellProps) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 grid min-h-[70px] grid-cols-[minmax(140px,1fr)_auto_minmax(140px,1fr)] items-center gap-4 border-b border-[rgba(244,239,228,0.1)] bg-[rgba(14,13,11,0.78)] px-[clamp(18px,3vw,40px)] py-3 backdrop-blur-[22px] max-[900px]:grid-cols-1 max-[900px]:gap-2.5">
        <button
          className="inline-flex min-h-10 items-center justify-self-start border-0 bg-transparent p-0 text-cinema-text tracking-normal max-[900px]:justify-self-center"
          type="button"
          onClick={() => onViewChange("search")}
          aria-label="Open search"
        >
          <span>
            <strong className="text-[1.18rem] font-[760] leading-none">CineScope</strong>
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
                  "relative inline-flex min-h-9 items-center justify-center gap-2 overflow-hidden rounded-lg border border-transparent bg-transparent px-3.5 text-[0.9rem] text-cinema-soft transition-[background,border-color,box-shadow,color,transform] duration-[220ms] ease-linear after:absolute after:bottom-0 after:left-3 after:right-3 after:h-0.5 after:origin-center after:scale-x-0 after:rounded-full after:bg-cinema-amber after:transition-transform after:duration-[220ms] after:ease-linear hover:bg-[rgba(255,255,255,0.08)] hover:text-cinema-text max-[640px]:flex-1 max-[640px]:px-2",
                  selected &&
                    "border-[rgba(242,177,92,0.46)] bg-[rgba(242,177,92,0.18)] text-cinema-amber-strong shadow-[0_0_0_1px_rgba(242,177,92,0.08),0_12px_30px_rgba(242,177,92,0.12)] after:scale-x-100 hover:text-cinema-amber-strong",
                )}
                data-selected={selected}
                key={item.id}
                type="button"
                onClick={() => onViewChange(item.id)}
                aria-current={selected ? "page" : undefined}
              >
                <Icon size={16} strokeWidth={2.1} />
                {selected ? <span className="size-1.5 rounded-full bg-cinema-amber shadow-[0_0_14px_rgba(242,177,92,0.85)]" aria-hidden="true" /> : null}
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

      </header>

      <main className="p-[clamp(18px,2.4vw,34px)] max-[640px]:p-3.5">{children}</main>
    </div>
  );
}
