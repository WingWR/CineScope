import { PlugZap } from "lucide-react";

type ConnectionNoticeProps = {
  title: string;
  message: string;
  actionHint?: string;
};

export function ConnectionNotice({ title, message, actionHint }: ConnectionNoticeProps) {
  return (
    <div className="grid min-h-40 grid-cols-[44px_minmax(0,1fr)] items-start gap-3.5 rounded-[18px] border border-[rgba(242,177,92,0.22)] bg-[linear-gradient(135deg,rgba(242,177,92,0.1),rgba(85,214,194,0.06)),rgba(255,255,255,0.045)] p-[22px] text-cinema-soft">
      <span
        className="grid size-11 place-items-center rounded-lg border border-[rgba(242,177,92,0.28)] bg-[rgba(242,177,92,0.12)] text-cinema-amber"
        aria-hidden="true"
      >
        <PlugZap size={22} />
      </span>
      <div>
        <strong className="block text-[1.08rem] text-cinema-text">{title}</strong>
        <p className="m-0 mt-2 leading-[1.65] text-cinema-soft">{message}</p>
        {actionHint ? <small className="mt-3 block text-[0.82rem] leading-normal text-cinema-teal">{actionHint}</small> : null}
      </div>
    </div>
  );
}
