import { Bot, Film, ListFilter, MessageSquareText, Sparkles, UserRound } from "lucide-react";
import { useMemo, useState } from "react";
import type { RecommendationMode, RecommendationRequest } from "../../entities/movie/types";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import { RecommendationCard } from "./RecommendationCard";
import { RecommendationRail } from "./RecommendationRail";
import { useRecommendations } from "./useRecommendations";

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
    <section className="screen recommend-screen">
      <SectionHeader
        title="Recommend"
        description="Use a simple recommendation request. Agent mode adds one natural-language brief; other modes stay parameter based."
      />

      <div className="recommend-layout">
        <div className="recommend-main">
          <div className="recommend-controls">
            <div className="mode-switcher" aria-label="Recommendation mode">
              {modes.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    className="mode-switcher__button"
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
              <div className="agent-composer">
                <div className="agent-composer__title">
                  <MessageSquareText size={18} />
                  <span>Agent brief</span>
                </div>
                <textarea
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Example: I want a fast-paced sci-fi movie for a weekend night, not too dark, with strong ratings."
                  aria-label="Agent recommendation prompt"
                />
              </div>
            ) : null}

            <div className="recommend-form">
              <label className="control-field">
                <span>Seed movie</span>
                <input
                  value={seedMovieName}
                  onChange={(event) => setSeedMovieName(event.target.value)}
                  placeholder="Optional seed title"
                />
              </label>

              <label className="control-field">
                <span>User ID</span>
                <input value={userId} onChange={(event) => setUserId(event.target.value)} placeholder="Optional user id" />
              </label>

              <label className="control-field">
                <span>Top K</span>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                />
              </label>
            </div>

            <button className="primary-action recommend-submit" type="button" onClick={() => setSubmittedRequest(draftRequest)}>
              Request recommendations
              <Sparkles size={16} />
            </button>
          </div>

          <div className="seed-strip">
            <div>
              <span>Request summary</span>
              <strong>{draftRequest.prompt || seedMovieName || "No recommendation request yet"}</strong>
              <p>Only real backend responses are rendered. This client does not use local candidate data.</p>
            </div>
            <Sparkles size={20} />
          </div>

          <div className="recommend-results" aria-busy={isLoading}>
            <div className="result-section-title">
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
