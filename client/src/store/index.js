import create from "zustand";
import { persist } from "zustand/";

export const useConnection = create(
  persist((set, get) => ({
    ws: null,
    connect: (url, eventHandlers) => {
      const ws = new WebSocket(get().url);
      if (eventHandlers) {
        for (const key in eventHandlers) {
          ws.addEventListener(key, callback, eventHandlers[key]);
        }
      }
      set({ ws });
    },
  }))
);

export const useSID = create(
  persist(
    (set) => ({
      sid: null,
      setSid: (sid) => set(sid),
    }),
    { name: "sid" }
  )
);
