import { PlugZap } from "lucide-react";

type ConnectionNoticeProps = {
  title: string;
  message: string;
  actionHint?: string;
};

export function ConnectionNotice({ title, message, actionHint }: ConnectionNoticeProps) {
  return (
    <div className="connection-notice">
      <span className="connection-notice__icon" aria-hidden="true">
        <PlugZap size={22} />
      </span>
      <div>
        <strong>{title}</strong>
        <p>{message}</p>
        {actionHint ? <small>{actionHint}</small> : null}
      </div>
    </div>
  );
}
