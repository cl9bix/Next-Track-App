import type { WSMessage, WSEventType } from '@/types';

type WSHandler = (message: WSMessage) => void;

interface WSClientOptions {
  url: string;
  token?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers = new Map<WSEventType, Set<WSHandler>>();
  private globalHandlers = new Set<WSHandler>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private intentionalClose = false;
  private options: Required<WSClientOptions>;

  constructor(options: WSClientOptions) {
    this.options = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      token: '',
      ...options,
    };
  }

  connect(eventId?: string): void {
    this.intentionalClose = false;
    this.reconnectAttempts = 0;

    const params = new URLSearchParams();
    if (this.options.token) params.set('token', this.options.token);
    if (eventId) params.set('event_id', eventId);

    const url = `${this.options.url}?${params}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('[WS] Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        this.dispatch(msg);
      } catch (e) {
        console.error('[WS] Parse error:', e);
      }
    };

    this.ws.onclose = () => {
      if (!this.intentionalClose) {
        this.scheduleReconnect(eventId);
      }
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Error:', err);
    };
  }

  disconnect(): void {
    this.intentionalClose = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  on(type: WSEventType, handler: WSHandler): () => void {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set());
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  onAny(handler: WSHandler): () => void {
    this.globalHandlers.add(handler);
    return () => this.globalHandlers.delete(handler);
  }

  send(type: WSEventType, payload: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload, timestamp: new Date().toISOString() }));
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private dispatch(msg: WSMessage): void {
    this.globalHandlers.forEach(h => h(msg));
    this.handlers.get(msg.type)?.forEach(h => h(msg));
  }

  private scheduleReconnect(eventId?: string): void {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }
    const delay = this.options.reconnectInterval * Math.pow(1.5, this.reconnectAttempts);
    this.reconnectAttempts++;
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.reconnectTimer = setTimeout(() => this.connect(eventId), delay);
  }
}
