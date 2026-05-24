import { ref } from "vue";
import { useSyncerActivityStore } from "~/stores/syncerActivity";

const ws = ref<WebSocket | null>(null);

const connected = ref(false);

const lastMessage = ref<any>(null);

let reconnectTimeout: NodeJS.Timeout | null = null;

export function useSyncerWebSocket() {
  const { runtime, isElectron } = useElectron();
  const syncerActivity = useSyncerActivityStore();

  async function connect() {
    if (!isElectron.value) {
      return;
    }

    if (
      ws.value &&
      (ws.value.readyState === WebSocket.OPEN ||
        ws.value.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    while (!runtime.value?.host || !runtime.value?.port) {
      console.log("[WS] Waiting runtime...");
      await new Promise((r) => setTimeout(r, 100));
    }

    const url = `ws://${runtime.value.host}:${runtime.value.port}/ws?token=${runtime.value.token}`;
    ws.value = new WebSocket(url);

    ws.value.onopen = () => {
      console.log("[WS] Connected");

      connected.value = true;
      syncerActivity.setConnected(true);
    };

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        
        lastMessage.value = data;

        console.log("[WS] Message", data);

        if (data?.event && data?.data && typeof data.data === "object") {
          syncerActivity.ingestEvent({ event: data.event, ...data.data });
        } else {
          syncerActivity.ingestEvent(data);
        }
      } catch (err) {
        console.error("[WS] Invalid JSON", err);
      }
    };

    ws.value.onerror = (err) => {
      console.error("[WS] Error", err);
    };

    ws.value.onclose = () => {
      console.warn("[WS] Disconnected");

      connected.value = false;
      syncerActivity.setConnected(false);

      reconnect();
    };
  }

  function reconnect() {
    if (reconnectTimeout) return;

    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null;

      connect();
    }, 2000);
  }

  function send(data: any) {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      return;
    }

    ws.value.send(JSON.stringify(data));
  }

  function disconnect() {
    ws.value?.close();
  }

  return {
    ws,
    connected,
    lastMessage,
    connect,
    disconnect,
    send,
  };
}
