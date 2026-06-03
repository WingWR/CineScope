import type { ReactNode } from "react";

type SectionHeaderProps = {
  title: string;
  description?: string;
  action?: ReactNode;
};

export function SectionHeader({ title, description, action }: SectionHeaderProps) {
  return (
    <div className="mb-[22px] mt-2.5 flex items-end justify-between gap-[22px] max-[640px]:mt-1.5">
      <div>
        <h1 className="m-0 max-w-[780px] text-[clamp(2rem,4.4vw,4.7rem)] font-[760] leading-[0.95] tracking-normal text-cinema-text max-[640px]:text-4xl">
          {title}
        </h1>
        {description ? (
          <p className="m-0 mt-3.5 max-w-[720px] text-[clamp(0.94rem,1.1vw,1.06rem)] leading-[1.7] text-cinema-soft">
            {description}
          </p>
        ) : null}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
