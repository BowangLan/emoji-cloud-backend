import React from "react";
import { Input } from "antd";

export default function EmojiEditor() {
  return (
    <div>
      <Input.TextArea
        placeholder="Enter a Python dictionary here..."
        style={{ height: "8rem" }}
        className="code-textarea"
      />
    </div>
  );
}
