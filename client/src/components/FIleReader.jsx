import React from "react";
import { message, Button } from 'antd';

export default function FIleReader({ onChange, accept, text }) {
  const ref = React.useRef();
  return (
    <div>
      <input
        ref={ref}
        className={'ant-btn ant-btn-default'}
        type="file"
        accept={accept}
        onInput={() => {
          console.log('oninput')
        }}
        onChange={(e) => {
          if (!e.target.files) return;
          console.log('input file onChange', e.target.files);
          const reader = new FileReader();
          reader.onload = (e) => {
            const content = e.target.result;
            onChange(content);
          };
          reader.readAsText(e.target.files[0]);
        }}
        style={{ display: 'none' }}
      />
      <Button onClick={() => {
        ref.current.click();
      }}>{text}</Button>
    </div>
  );
}
