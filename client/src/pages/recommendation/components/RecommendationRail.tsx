import { GitBranch, Radar, Route, Sparkle } from "lucide-react";
import type { ReactNode } from "react";
import type { RecommendationItem, RecommendationMode } from "../../../entities/movie/types";
import { cx, panelClass } from "../../../shared/ui/classes";

type RecommendationRailProps = {
  mode: RecommendationMode;
  prompt: string;
  seedMovieName: string;
  items: RecommendationItem[];
  submitted: boolean;
};

export function RecommendationRail({ mode, prompt, seedMovieName, items, submitted }: RecommendationRailProps) {
  const topItem = items[0];

  return (
    <aside className={cx(panelClass, "sticky top-24 grid gap-4 p-[18px] max-[1180px]:static")} aria-label="Recommendation explanation">
      <div className="flex items-start gap-[9px] font-bold text-cinema-text">
        <Radar size={18} />
        <div className="grid gap-[3px]">
          <strong className="text-cinema-text">Recommendation flow</strong>
          <span className="text-[0.78rem] font-[760] uppercase text-cinema-amber">{submitted ? "Request submitted" : "Draft request"}</span>
        </div>
      </div>

      <div className="grid gap-3">
        <PipelineStep icon={<Route size={16} />} title="Mode" body={`${mode} will be sent in the request payload.`} />
        <PipelineStep
          icon={<GitBranch size={16} />}
          title="Input"
          body={prompt || seedMovieName || "No Agent brief or seed movie yet."}
        />
        <PipelineStep
          icon={<Sparkle size={16} />}
          title="Response"
          body={topItem ? `${topItem.movie.title} is the strongest returned candidate.` : "No recommendation response has been received."}
        />
      </div>

      <div className="rounded-xl border border-[rgba(242,177,92,0.2)] bg-[rgba(242,177,92,0.07)] p-3.5">
        <strong className="text-[0.92rem] text-cinema-text">Integration point</strong>
        <p className="m-0 mt-1 text-[0.84rem] leading-[1.55] text-cinema-soft">
          The frontend sends one simple `RecommendationRequest`. Only Agent mode includes a natural-language prompt.
        </p>
      </div>
    </aside>
  );
}

type PipelineStepProps = {
  icon: ReactNode;
  title: string;
  body: string;
};

function PipelineStep({ icon, title, body }: PipelineStepProps) {
  return (
    <div className="grid grid-cols-[34px_1fr] items-start gap-2.5">
      <span className="grid size-[34px] place-items-center rounded-lg border border-[rgba(85,214,194,0.2)] bg-[rgba(85,214,194,0.08)] text-cinema-teal">
        {icon}
      </span>
      <div>
        <strong className="text-[0.92rem] text-cinema-text">{title}</strong>
        <p className="m-0 mt-1 text-[0.84rem] leading-[1.55] text-cinema-soft">{body}</p>
      </div>
    </div>
  );
}
