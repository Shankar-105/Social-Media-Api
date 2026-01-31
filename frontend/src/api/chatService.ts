import api from './client';

export const chatService = {
    getChatHistory: async (userId: string | number) => {
        const response = await api.get(`/chat/history/${userId}`);
        return response.data;
    },
    getRecentChats: async () => {
        const response = await api.get('/chat/recent-chats');
        return response.data;
    },
};

export class ChatSocket {
    private socket: WebSocket | null = null;
    private userId: number;
    private token: string;

    constructor(userId: number, token: string) {
        this.userId = userId;
        this.token = token;
    }

    connect(onMessage: (msg: any) => void) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/^https?:\/\//, '') || `${window.location.hostname}:8000`;
        this.socket = new WebSocket(`${protocol}//${baseUrl}/chat/ws/${this.userId}?token=${this.token}`);

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'ping') {
                this.socket?.send(JSON.stringify({ type: 'pong' }));
            } else {
                onMessage(data);
            }
        };

        this.socket.onclose = () => {
            console.log('Chat socket closed');
        };

        this.socket.onerror = (error) => {
            console.error('Chat socket error:', error);
        };
    }

    sendMessage(message: any) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        }
    }

    sendReaction(msgId: number, emoji: string) {
        this.sendMessage({ type: 'reaction', message_id: msgId, reaction: emoji });
    }

    sendEdit(msgId: number, newContent: string, receiverId: number) {
        this.sendMessage({ type: 'edit_message', msg_id: msgId, new_content: newContent, receiver_id: receiverId });
    }

    sendDelete(msgId: number, receiverId: number) {
        this.sendMessage({ type: 'delete_for_everyone', message_id: msgId, receiver_id: receiverId });
    }

    sendTyping(isTyping: boolean, receiverId: number) {
        this.sendMessage({ type: 'typing', is_typing: isTyping, receiver_id: receiverId });
    }

    sendReply(toId: number, replyMsgId: number, content: string) {
        this.sendMessage({ type: 'reply_message', to: toId, reply_msg_id: replyMsgId, content });
    }

    sendRead(senderId: number) {
        this.sendMessage({ type: 'read_receipt', sender_id: senderId });
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}
