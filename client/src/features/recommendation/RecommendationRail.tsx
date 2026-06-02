import { GitBranch, Radar, Route, Sparkle } from "lucide-react";
import type { ReactNode } from "react";
import type { RecommendationItem, RecommendationMode } from "../../entities/movie/types";

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
    <aside className="recommend-rail" aria-label="Recommendation explanation">
      <div className="rail-header">
        <Radar size={18} />
        <div>
          <strong>Recommendation flow</strong>
          <span>{submitted ? "Request submitted" : "Draft request"}</span>
        </div>
      </div>

      <div className="pipeline">
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

      <div className="adapter-note">
        <strong>Integration point</strong>
        <p>The frontend sends one simple `RecommendationRequest`. Only Agent mode includes a natural-language prompt.</p>
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
    <div className="pipeline-step">
      <span>{icon}</span>
      <div>
        <strong>{title}</strong>
        <p>{body}</p>
      </div>
    </div>
  );
}
