import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { chatService } from '@/api/chatService';
import { Loader2, MessageCircle } from 'lucide-react';
import ChatSidebar from '@/components/chat/ChatSidebar';
import ChatWindow from '@/components/chat/ChatWindow';
import { useSocket } from '@/context/SocketContext';

export default function Messages() {
    const [activeChat, setActiveChat] = useState<any | null>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [otherUserTyping, setOtherUserTyping] = useState(false);
    const [replyTo, setReplyTo] = useState<any | null>(null);

    const user = useAuthStore((state) => state.user);
    const location = useLocation();
    const { socket, setActiveChatId, resetUnreadCount, recentChats, refreshRecentChats } = useSocket();

    // Reset global unread count when visiting Messages page
    useEffect(() => {
        resetUnreadCount();
        refreshRecentChats();
    }, [resetUnreadCount, refreshRecentChats]);

    // Update context about which chat is active for notification suppression
    useEffect(() => {
        setActiveChatId(activeChat?.id || null);
    }, [activeChat, setActiveChatId]);

    // 2. Handle navigation from Profile
    useEffect(() => {
        if (location.state?.chatWith) {
            const chatUser = location.state.chatWith;
            setActiveChat(chatUser);
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    // 3. Socket Event Handling
    useEffect(() => {
        if (!socket || !activeChat || !user) return;

        const handleMessage = (msg: any) => {
            if (msg.type === 'typing') {
                if (msg.receiver_id === user.id && Number(msg.sender_id) === activeChat.id) {
                    setOtherUserTyping(msg.is_typing);
                }
            } else if (msg.type === 'reaction') {
                // standardized event from backend: msg.message_id, msg.reaction
                setMessages((prev) => prev.map(m =>
                    m.id === msg.message_id
                        ? { ...m, reactions: [...(m.reactions || []), msg] }
                        : m
                ));
            } else if (msg.type === 'edit_message') {
                // standardized event from backend: msg.message_id, msg.new_content
                setMessages((prev) => prev.map(m =>
                    m.id === msg.message_id
                        ? { ...m, content: msg.new_content, is_edited: true }
                        : m
                ));
            } else if (msg.type === 'delete_message') {
                // standardized event from backend: msg.message_id
                setMessages((prev) => prev.filter(m => m.id !== msg.message_id));
            } else if (msg.type === 'read_receipt') {
                if (msg.reader_id === activeChat.id) {
                    setMessages(prev => prev.map(m => ({ ...m, is_read: true })));
                }
            } else if (msg.type === 'message' || msg.type === 'shared_post') {
                if (msg.sender_id === activeChat.id || msg.sender_id === user.id) {
                    setMessages((prev) => [...prev, msg]);
                    if (msg.sender_id === activeChat.id) {
                        socket?.sendRead(activeChat.id);
                    }
                }
            }
        };

        socket.addListener(handleMessage);

        const fetchHistory = async () => {
            try {
                const history = await chatService.getChatHistory(activeChat.id);
                setMessages(history);
            } catch (err) {
                console.error('Failed to fetch chat history', err);
            }
        };
        fetchHistory();

        return () => {
            socket.removeListener(handleMessage);
        };
    }, [activeChat, user, socket]);

    // Handlers
    const handleSendMessage = (content: string) => {
        if (!socket || !activeChat) return;

        if (replyTo) {
            socket.sendReply(activeChat.id, replyTo.id, content);
            setReplyTo(null);
        } else {
            socket.sendMessage({
                to: activeChat.id,
                content: content,
            });
        }
    };

    const handleReaction = (msgId: number, emoji: string) => {
        socket?.sendReaction(msgId, emoji);
    };

    const handleTyping = (typing: boolean) => {
        if (activeChat) {
            socket?.sendTyping(typing, activeChat.id);
        }
    };

    const handleRead = (senderId: number) => {
        socket?.sendRead(senderId);
    };

    if (!user) return <div className="h-full flex items-center justify-center"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="flex h-[calc(100vh-theme(spacing.16))] md:h-[calc(100vh-0px)] overflow-hidden bg-white dark:bg-black">
            {/* Sidebar */}
            <div className={`w-full md:w-[350px] shrink-0 ${activeChat ? 'hidden md:flex' : 'flex'}`}>
                <ChatSidebar
                    chats={recentChats}
                    activeChat={activeChat}
                    onSelectChat={setActiveChat}
                />
            </div>

            {/* Chat Window */}
            <div className={`flex-1 ${!activeChat ? 'hidden md:flex' : 'flex'}`}>
                {activeChat ? (
                    <div className="flex flex-col w-full h-full relative">
                        <div className="md:hidden absolute top-4 left-2 z-10">
                            <button onClick={() => setActiveChat(null)} className="p-2 bg-zinc-100 rounded-full">
                                ←
                            </button>
                        </div>

                        <ChatWindow
                            activeChat={activeChat}
                            messages={messages}
                            onSendMessage={handleSendMessage}
                            onReaction={handleReaction}
                            onReply={setReplyTo}
                            onEdit={(id, content) => socket?.sendEdit(id, content, activeChat.id)}
                            onDelete={(id) => socket?.sendDelete(id, activeChat.id)}
                            onTyping={handleTyping}
                            isTyping={otherUserTyping}
                            onRead={handleRead}
                            currentUser={user}
                        />
                    </div>
                ) : (
                    <div className="hidden md:flex flex-col items-center justify-center w-full h-full text-zinc-400">
                        <div className="h-24 w-24 border-2 border-zinc-200 dark:border-zinc-800 rounded-full flex items-center justify-center mb-4">
                            <MessageCircle className="h-10 w-10 opacity-50" />
                        </div>
                        <h2 className="text-xl font-medium text-black dark:text-white">Your Messages</h2>
                        <p className="mt-2 text-sm">Send private messages to a friend.</p>
                        <button className="mt-6 font-semibold bg-blue-500 text-white px-4 py-1.5 rounded-lg text-sm">
                            Send message
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
