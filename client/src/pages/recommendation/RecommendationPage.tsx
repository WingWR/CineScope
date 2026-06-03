import { Bot, Film, ListFilter, MessageSquareText, Sparkles, UserRound } from "lucide-react";
import { useMemo, useState } from "react";
import type { RecommendationMode, RecommendationRequest } from "../../entities/movie/types";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import {
  controlFieldClass,
  controlLabelClass,
  cx,
  panelClass,
  primaryActionClass,
  screenClass,
  textInputClass,
} from "../../shared/ui/classes";
import { RecommendationCard } from "./components/RecommendationCard";
import { RecommendationRail } from "./components/RecommendationRail";
import { useRecommendations } from "./hooks/useRecommendations";

const modes: Array<{ value: RecommendationMode; label: string; icon: typeof Film }> = [
  { value: "content", label: "Content", icon: Film },
  { value: "collaborative", label: "Collaborative", icon: UserRound },
  { value: "agent-ready", label: "Agent", icon: Bot },
];

export function RecommendationPage() {
  const [mode, setMode] = useState<RecommendationMode>("agent-ready");
  const [prompt, setPrompt] = useState("");
  const [seedMovieName, setSeedMovieName] = useState("");
  const [userId, setUserId] = useState("");
  const [topK, setTopK] = useState(6);
  const [submittedRequest, setSubmittedRequest] = useState<RecommendationRequest | null>(null);

  const draftRequest: RecommendationRequest = useMemo(
    () => ({
      mode,
      prompt: mode === "agent-ready" ? prompt : "",
      seedMovieName,
      userId,
      topK,
    }),
    [mode, prompt, seedMovieName, topK, userId],
  );

  const { items, isLoading, errorMessage } = useRecommendations(submittedRequest);
  const isAgentMode = mode === "agent-ready";

  return (
    <section className={screenClass}>
      <SectionHeader
        title="Recommend"
        description="Use a simple recommendation request. Agent mode adds one natural-language brief; other modes stay parameter based."
      />

      <div className="grid grid-cols-[minmax(0,1fr)_340px] items-start gap-[18px] max-[1180px]:grid-cols-1">
        <div className="grid gap-4">
          <div className={cx(panelClass, "grid gap-4 p-[18px]")}>
            <div className="grid grid-cols-3 gap-2 max-[640px]:grid-cols-1" aria-label="Recommendation mode">
              {modes.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    className={cx(
                      "inline-flex min-h-9 min-w-0 items-center justify-center gap-2 whitespace-nowrap rounded-lg border border-transparent bg-cinema-surface px-2.5 text-[0.9rem] text-cinema-soft transition-[background,color,transform] duration-[220ms] ease-linear hover:bg-[rgba(255,255,255,0.08)] hover:text-cinema-text",
                      mode === item.value &&
                        "border-[rgba(242,177,92,0.32)] bg-[rgba(242,177,92,0.16)] text-cinema-amber-strong hover:text-cinema-amber-strong",
                    )}
                    data-selected={mode === item.value}
                    key={item.value}
                    type="button"
                    onClick={() => setMode(item.value)}
                  >
                    <Icon size={16} />
                    {item.label}
                  </button>
                );
              })}
            </div>

            {isAgentMode ? (
              <div className="grid gap-3 rounded-xl border border-cinema-border bg-[rgba(255,255,255,0.045)] p-3.5">
                <div className="flex items-center gap-2 text-[0.82rem] font-[760] uppercase text-cinema-amber">
                  <MessageSquareText size={18} />
                  <span>Agent brief</span>
                </div>
                <textarea
                  className="min-h-[132px] resize-y rounded-lg border border-cinema-border bg-cinema-surface p-3.5 leading-[1.55] text-cinema-text outline-none focus:border-[rgba(242,177,92,0.48)] focus:shadow-[0_0_0_3px_rgba(242,177,92,0.12)]"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Example: I want a fast-paced sci-fi movie for a weekend night, not too dark, with strong ratings."
                  aria-label="Agent recommendation prompt"
                />
              </div>
            ) : null}

            <div className="grid grid-cols-[1.5fr_0.8fr_0.55fr] gap-3 max-[640px]:grid-cols-1">
              <label className={controlFieldClass}>
                <span className={controlLabelClass}>Seed movie</span>
                <input
                  className={textInputClass}
                  value={seedMovieName}
                  onChange={(event) => setSeedMovieName(event.target.value)}
                  placeholder="Optional seed title"
                />
              </label>

              <label className={controlFieldClass}>
                <span className={controlLabelClass}>User ID</span>
                <input className={textInputClass} value={userId} onChange={(event) => setUserId(event.target.value)} placeholder="Optional user id" />
              </label>

              <label className={controlFieldClass}>
                <span className={controlLabelClass}>Top K</span>
                <input
                  className={textInputClass}
                  type="number"
                  min="1"
                  max="50"
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                />
              </label>
            </div>

            <button
              className={cx(primaryActionClass, "min-w-[220px] justify-self-end max-[640px]:w-full max-[640px]:justify-self-stretch")}
              type="button"
              onClick={() => setSubmittedRequest(draftRequest)}
            >
              Request recommendations
              <Sparkles size={16} />
            </button>
          </div>

          <div className={cx(panelClass, "relative grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 overflow-hidden p-3.5 max-[640px]:grid-cols-1")}>
            <div>
              <span className="text-[0.78rem] font-[760] uppercase text-cinema-amber">Request summary</span>
              <strong className="block truncate text-[1.24rem] text-cinema-text">{draftRequest.prompt || seedMovieName || "No recommendation request yet"}</strong>
              <p className="m-0 leading-[1.55] text-cinema-soft">
                Only real backend responses are rendered. This client does not use local candidate data.
              </p>
            </div>
            <Sparkles size={20} />
          </div>

          <div className="grid gap-3" aria-busy={isLoading}>
            <div className="flex min-h-9 items-center gap-[9px] font-bold text-cinema-soft">
              <ListFilter size={17} />
              <span>{isLoading ? "Waiting for backend response" : `${items.length} recommendations`}</span>
            </div>

            {errorMessage ? (
              <ConnectionNotice
                title="Waiting for recommendation API"
                message={errorMessage}
                actionHint="Suggested endpoint: POST /recommendations with mode, prompt, seedMovieName, userId, and topK."
              />
            ) : null}

            {!errorMessage && !submittedRequest ? (
              <ConnectionNotice
                title="No recommendation request yet"
                message="Choose a mode, fill the minimal request fields, then submit. Agent mode is the only mode with a text brief."
              />
            ) : null}

            {!errorMessage && submittedRequest && items.length === 0 ? (
              <ConnectionNotice
                title="No returned recommendations"
                message="The backend returned an empty list. Results will appear here when the API returns RecommendationItem objects."
              />
            ) : null}

            {items.map((item, index) => (
              <RecommendationCard item={item} index={index} key={item.movie.id} />
            ))}
          </div>
        </div>

        <RecommendationRail
          mode={mode}
          prompt={draftRequest.prompt}
          seedMovieName={seedMovieName}
          items={items}
          submitted={Boolean(submittedRequest)}
        />
      </div>
    </section>
  );
}
