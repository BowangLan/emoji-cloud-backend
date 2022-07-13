import { Layout } from 'antd';
import React from 'react';

export default function MyLayout({ children }) {
  return (
    <Layout>
      <Layout.Header>
        <h1 style={{ color: '#fff' }} >EmojiCloud</h1>
      </Layout.Header>
      <Layout.Content>
        {children}
      </Layout.Content>
      <Layout.Footer></Layout.Footer>
    </Layout>
  )
}