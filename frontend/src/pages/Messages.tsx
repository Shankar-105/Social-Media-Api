import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { ChatSocket, chatService } from '@/api/chatService';
import { Loader2, MessageCircle } from 'lucide-react';
import ChatSidebar from '@/components/chat/ChatSidebar';
import ChatWindow from '@/components/chat/ChatWindow';

export default function Messages() {
    const [chats, setChats] = useState<any[]>([]);
    const [activeChat, setActiveChat] = useState<any | null>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [otherUserTyping, setOtherUserTyping] = useState(false);
    const [replyTo, setReplyTo] = useState<any | null>(null);

    const user = useAuthStore((state) => state.user);
    const token = useAuthStore((state) => state.token);
    const socketRef = useRef<ChatSocket | null>(null);
    const location = useLocation();

    // 1. Fetch Chat List
    useEffect(() => {
        const fetchChats = async () => {
            try {
                const data = await chatService.getRecentChats();
                setChats(data.length > 0 ? data : []);
                setIsLoading(false);
            } catch (err) {
                setChats([]);
                setIsLoading(false);
            }
        };
        fetchChats();
    }, []);

    // 2. Handle navigation from Profile
    useEffect(() => {
        if (location.state?.chatWith) {
            const chatUser = location.state.chatWith;
            setChats(prev => {
                const exists = prev.some(c => c.id === chatUser.id);
                if (!exists) return [chatUser, ...prev];
                return prev;
            });
            setActiveChat(chatUser);
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    // 3. Socket Connection & Events
    useEffect(() => {
        if (activeChat && user && token) {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }

            socketRef.current = new ChatSocket(user.id, token);
            socketRef.current.connect((msg) => {
                if (msg.type === 'typing') {
                    if (msg.receiver_id === user.id && Number(msg.sender_id) === activeChat.id) {
                        setOtherUserTyping(msg.is_typing);
                    }
                } else if (msg.type === 'reaction') {
                    setMessages((prev) => prev.map(m =>
                        m.id === msg.message_id
                            ? { ...m, reactions: [...(m.reactions || []), msg] }
                            : m
                    ));
                } else if (msg.type === 'edit_message') {
                    setMessages((prev) => prev.map(m =>
                        m.id === msg.msg_id
                            ? { ...m, content: msg.new_content, is_edited: true }
                            : m
                    ));
                } else if (msg.type === 'delete_for_everyone') {
                    setMessages((prev) => prev.filter(m => m.id !== msg.message_id));
                } else if (msg.type === 'read_receipt') {
                    if (msg.reader_id === activeChat.id) {
                        setMessages(prev => prev.map(m => ({ ...m, is_read: true })));
                    }
                } else {
                    if (msg.sender_id === activeChat.id || msg.sender_id === user.id) {
                        setMessages((prev) => [...prev, msg]);
                        if (msg.sender_id === activeChat.id) {
                            socketRef.current?.sendRead(activeChat.id);
                        }
                    }
                }
            });

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
                socketRef.current?.disconnect();
            };
        }
    }, [activeChat, user, token]);

    // Handlers
    const handleSendMessage = (content: string) => {
        if (!socketRef.current || !activeChat) return;

        if (replyTo) {
            socketRef.current.sendReply(activeChat.id, replyTo.id, content);
            setReplyTo(null);
        } else {
            socketRef.current.sendMessage({
                to: activeChat.id,
                content: content,
            });
        }
    };

    const handleReaction = (msgId: number, emoji: string) => {
        socketRef.current?.sendReaction(msgId, emoji);
    };

    const handleTyping = (typing: boolean) => {
        if (activeChat) {
            socketRef.current?.sendTyping(typing, activeChat.id);
        }
    };

    const handleRead = (senderId: number) => {
        socketRef.current?.sendRead(senderId);
    };

    if (!user) return <div className="h-full flex items-center justify-center"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="flex h-[calc(100vh-theme(spacing.16))] md:h-[calc(100vh-0px)] overflow-hidden bg-white dark:bg-black">
            {/* Sidebar */}
            <div className={`w-full md:w-[350px] shrink-0 ${activeChat ? 'hidden md:flex' : 'flex'}`}>
                <ChatSidebar
                    chats={chats}
                    activeChat={activeChat}
                    onSelectChat={setActiveChat}
                    isLoading={isLoading}
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
                            onEdit={(id, content) => socketRef.current?.sendEdit(id, content, activeChat.id)}
                            onDelete={(id) => socketRef.current?.sendDelete(id, activeChat.id)}
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
