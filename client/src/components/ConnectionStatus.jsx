import React from 'react'
import { useConnection } from "../store";

const state_to_color = {
  'Connecting': 'gray',
  'Connected': 'green',
  'Disconnecting': 'gray',
  'Disconnected': 'red'
}

export default function ConnectionStatus() {
  const wsState = useConnection(state => state.wsState);
  let state;
  if (wsState === null) {
    state = 'Disconnect';
  } else {
    switch (ws.readyState) {
      case 0:
        state = 'Connecting';
      case 1:
        state = 'Connected';
      case 2:
        state = 'Disconnecting';
      case 3:
        state = 'Disconnected';
    }
  }
  return (
    <div><span style={{color: state_to_color[state]}}>{state}</span></div>
  )
}
