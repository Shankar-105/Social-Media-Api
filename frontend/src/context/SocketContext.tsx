import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';
import { ChatSocket, chatService } from '@/api/chatService';

interface SocketContextType {
    socket: ChatSocket | null;
    unreadCount: number;
    resetUnreadCount: () => void;
    setActiveChatId: (id: number | null) => void;
    recentChats: any[];
    refreshRecentChats: () => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const user = useAuthStore((state) => state.user);
    const token = useAuthStore((state) => state.token);
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

    const [socket, setSocket] = useState<ChatSocket | null>(null);
    const [unreadCount, setUnreadCount] = useState(0);
    const [recentChats, setRecentChats] = useState<any[]>([]);
    const activeChatIdRef = useRef<number | null>(null);

    const refreshRecentChats = async () => {
        try {
            const data = await chatService.getRecentChats();
            setRecentChats(data);
        } catch (err) {
            console.error('Failed to fetch recent chats', err);
        }
    };

    const setActiveChatId = (id: number | null) => {
        activeChatIdRef.current = id;
    };

    const resetUnreadCount = () => setUnreadCount(0);

    useEffect(() => {
        if (isAuthenticated && user && token) {
            refreshRecentChats();
            const chatSocket = new ChatSocket(user.id, token);

            const handleMessage = (msg: any) => {
                if (msg.type === 'message' || msg.type === 'shared_post') {
                    // Update unread count
                    if (msg.sender_id !== user.id && msg.sender_id !== activeChatIdRef.current) {
                        setUnreadCount(prev => prev + 1);
                    }
                    // Update recent chats list in real-time
                    setRecentChats(prev => {
                        const senderId = msg.sender_id === user.id ? msg.receiver_id : msg.sender_id;
                        const existingChatIndex = prev.findIndex(c => c.id === senderId);

                        const updatedChat = existingChatIndex !== -1 ? { ...prev[existingChatIndex] } : { id: senderId, username: msg.sender_username || 'Unknown' };
                        updatedChat.last_message = msg.content;
                        updatedChat.last_msg_time = msg.created_at || new Date().toISOString();
                        updatedChat.is_read = msg.sender_id === user.id;

                        if (existingChatIndex !== -1) {
                            const newChats = [...prev];
                            newChats.splice(existingChatIndex, 1);
                            return [updatedChat, ...newChats];
                        }
                        return [updatedChat, ...prev];
                    });
                }
            };

            chatSocket.connect(handleMessage);
            setSocket(chatSocket);

            return () => {
                chatSocket.disconnect();
                setSocket(null);
            };
        }
    }, [isAuthenticated, user, token]);

    return (
        <SocketContext.Provider value={{ socket, unreadCount, resetUnreadCount, setActiveChatId, recentChats, refreshRecentChats }}>
            {children}
        </SocketContext.Provider>
    );
};

export const useSocket = () => {
    const context = useContext(SocketContext);
    if (!context) {
        throw new Error('useSocket must be used within a SocketProvider');
    }
    return context;
};
