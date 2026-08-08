import { useState } from "react";

export default function CustomerReply({ reply }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(reply);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="customer-reply">
      <h4>Generated Customer Response</h4>
      <div className="reply-box">{reply}</div>
      <button className="copy-btn" onClick={handleCopy}>
        {copied ? "Copied!" : "Copy Reply"}
      </button>
    </div>
  );
}