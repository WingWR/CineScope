import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cx } from "./classes";

type IconButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  icon: ReactNode;
  label: string;
};

export function IconButton({ icon, label, className = "", ...props }: IconButtonProps) {
  return (
    <button
      className={cx(
        "inline-grid size-10 place-items-center rounded-lg border border-cinema-border bg-cinema-surface text-cinema-soft transition-colors duration-[220ms] ease-linear hover:bg-[rgba(255,255,255,0.08)] hover:text-cinema-text",
        className,
      )}
      type="button"
      aria-label={label}
      title={label}
      {...props}
    >
      {icon}
    </button>
  );
}
