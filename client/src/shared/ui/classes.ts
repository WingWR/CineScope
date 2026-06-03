type ClassValue = string | false | null | undefined;

export function cx(...classes: ClassValue[]) {
  return classes.filter(Boolean).join(" ");
}

export const screenClass = "relative isolate mx-auto w-[min(1540px,100%)] animate-screen-in";

export const panelClass =
  "rounded-[18px] border border-cinema-border bg-cinema-panel shadow-cinema backdrop-blur-[18px]";

export const controlFieldClass = "grid gap-[9px] text-[0.86rem] text-cinema-soft";

export const controlLabelClass = "text-[0.77rem] font-bold uppercase text-cinema-muted";

export const textInputClass =
  "min-h-[42px] w-full rounded-lg border border-cinema-border bg-cinema-surface px-3 text-cinema-text outline-none focus:border-[rgba(242,177,92,0.48)] focus:shadow-[0_0_0_3px_rgba(242,177,92,0.12)]";

export const rangeInputClass =
  "min-h-[42px] w-full rounded-lg border border-cinema-border bg-cinema-surface text-cinema-text accent-cinema-amber outline-none focus:border-[rgba(242,177,92,0.48)] focus:shadow-[0_0_0_3px_rgba(242,177,92,0.12)]";

export const primaryActionClass =
  "inline-flex min-h-11 items-center justify-center gap-[9px] rounded-lg border-0 bg-gradient-to-r from-cinema-amber to-[#e18b4a] px-4 font-[760] text-[#17100b] transition-[filter,transform] duration-[220ms] ease-linear hover:-translate-y-0.5 hover:brightness-[1.06]";
