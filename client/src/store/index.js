import create from "zustand";
import { persist } from "zustand/middleware";

export const useConnection = create((set) => ({
  ws: null,
  wsState: null,
  connect: (url, eventHandlers) => {
    try {
      const ws = new WebSocket(url);
      set({ wsState: 1 });
      ws.addEventListener('open', () => {
        set({ wsState: 1 });
      })
      ws.addEventListener('close', () => {
        set({ wsState: 3 });
      })
      if (eventHandlers) {
        for (const key in eventHandlers) {
          ws.addEventListener(key, eventHandlers[key]);
        }
      }
      console.log('set ws', ws);
      set({ ws });
    } catch (e) {
      console.error(e);
    }
  },
}));

export const useSID = create(
  persist(
    (set) => ({
      sid: null,
      setSid: (sid) => set(sid),
    }),
    { name: "sid" }
  )
);
