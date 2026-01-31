import { useState, useRef, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Phone, Video, Info, Image as ImageIcon, Heart, Send } from 'lucide-react';
import MessageItem from '@/components/common/MessageItem';

interface ChatWindowProps {
    activeChat: any;
    messages: any[];
    onSendMessage: (content: string) => void;
    onReaction: (msgId: number, emoji: string) => void;
    onReply: (message: any) => void;
    onEdit: (msgId: number, content: string) => void;
    onDelete: (msgId: number) => void;
    onTyping: (isTyping: boolean) => void;
    onRead: (senderId: number) => void;
    isTyping: boolean; // Is the OTHER user typing?
    currentUser: any;
}

export default function ChatWindow({
    activeChat,
    messages,
    onSendMessage,
    onReaction,
    onReply,
    onEdit,
    onDelete,
    onTyping,
    onRead,
    isTyping,
    currentUser
}: ChatWindowProps) {
    const [inputValue, setInputValue] = useState('');
    const lastMessageRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (lastMessageRef.current) {
            lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isTyping]);

    // Read logic
    useEffect(() => {
        if (!messages.length || !activeChat) return;

        // Find last unread message from them
        const lastMsg = messages[messages.length - 1];
        const isMe = lastMsg.sender_id === currentUser.id || lastMsg.from === currentUser.id;

        // If last message is from them and not read (or we assume unread if we just opened it because frontend might not have updated 'is_read' in real-time instantly without a fetch)
        // Backend handles "mark all as read".
        if (!isMe) {
            onRead(activeChat.id);
        }
    }, [messages, activeChat, currentUser.id, onRead]);

    const handleSend = () => {
        if (!inputValue.trim()) return;
        onSendMessage(inputValue);
        setInputValue('');
        onTyping(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
        if (e.target.value.length > 0) {
            onTyping(true);
        } else {
            onTyping(false);
        }
    };

    if (!activeChat) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-zinc-400 bg-white dark:bg-black">
                <div className="h-24 w-24 rounded-full border-2 border-zinc-200 dark:border-zinc-800 flex items-center justify-center mb-4">
                    <Send className="h-10 w-10" />
                </div>
                <h2 className="text-xl font-medium text-black dark:text-white">Your Messages</h2>
                <p className="text-sm">Send private photos and messages to a friend.</p>
                <Button className="mt-4" onClick={() => { }}>Send message</Button>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-white dark:bg-black w-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 px-6 border-b border-zinc-200 dark:border-zinc-800 h-[75px] shrink-0">
                <div className="flex items-center space-x-3 cursor-pointer hover:opacity-70 transition-opacity">
                    <Avatar className="h-11 w-11 border border-zinc-200 dark:border-zinc-800">
                        <AvatarImage src={activeChat.profile_pic} />
                        <AvatarFallback>{activeChat.username[0]?.toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col">
                        <span className="font-bold text-base leading-none">{activeChat.nickname || activeChat.username}</span>
                        <span className="text-xs text-zinc-500 font-medium pt-1">
                            {/* Active status or username */}
                            {activeChat.username}
                        </span>
                    </div>
                </div>
                <div className="flex items-center space-x-6 text-zinc-800 dark:text-white">
                    <Phone className="h-7 w-7 stroke-[1.5]" />
                    <Video className="h-7 w-7 stroke-[1.5]" />
                    <Info className="h-7 w-7 stroke-[1.5]" />
                </div>
            </div>

            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4 custom-scrollbar">
                <div className="flex flex-col justify-end min-h-full py-4 space-y-1">
                    {/* Timestamp for start of conversation? */}
                    <div className="flex flex-col items-center py-6 space-y-2 mb-4">
                        <Avatar className="h-20 w-20 mb-2">
                            <AvatarImage src={activeChat.profile_pic} />
                            <AvatarFallback className="text-2xl">{activeChat.username[0]?.toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <h3 className="text-xl font-bold">{activeChat.nickname || activeChat.username}</h3>
                        <Button variant="secondary" size="sm">View profile</Button>
                    </div>

                    {messages.map((msg, index) => (
                        <div key={msg.id || index}>
                            <MessageItem
                                message={msg}
                                onReact={onReaction}
                                onReply={onReply}
                                onEdit={onEdit}
                                onDelete={onDelete}
                            />
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex items-center space-x-2 p-2 bg-zinc-100 dark:bg-zinc-900 rounded-full w-fit mb-4 ml-2 animate-in fade-in duration-300">
                            <Avatar className="h-6 w-6">
                                <AvatarImage src={activeChat.profile_pic} />
                            </Avatar>
                            <div className="flex space-x-1">
                                <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce"></span>
                            </div>
                        </div>
                    )}
                    <div ref={lastMessageRef} />
                </div>
            </ScrollArea>

            {/* Footer Input */}
            <div className="p-4 px-4 pb-4">
                <div className="flex items-center space-x-2 bg-zinc-100 dark:bg-zinc-900 rounded-full p-2 pl-4 border border-transparent focus-within:border-zinc-300 dark:focus-within:border-zinc-700 transition-colors">
                    <button className="p-1 rounded-full bg-blue-500 text-white flex items-center justify-center">
                        <CameraIcon className="h-4 w-4" />
                    </button>
                    <Input
                        placeholder="Message..."
                        className="flex-1 border-none bg-transparent shadow-none focus-visible:ring-0 text-base"
                        value={inputValue}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                    />
                    {inputValue.trim().length > 0 ? (
                        <button
                            className="p-2 text-blue-500 font-bold hover:text-blue-600 transition-colors"
                            onClick={handleSend}
                        >
                            Send
                        </button>
                    ) : (
                        <div className="flex items-center space-x-3 pr-2 text-zinc-500 dark:text-zinc-400">
                            <button className="hover:text-zinc-800 dark:hover:text-white"><ImageIcon className="h-6 w-6" /></button>
                            <button className="hover:text-zinc-800 dark:hover:text-white"><Heart className="h-6 w-6" /></button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function CameraIcon({ className }: { className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
            <path d="M12 9a3.75 3.75 0 100 7.5A3.75 3.75 0 0012 9z" />
            <path fillRule="evenodd" d="M9.344 3.071a4.993 4.993 0 015.312 0l.208.119a6.539 6.539 0 002.246.809 3.126 3.126 0 011.852 1.894l.509 1.527a3 3 0 01.107.828l-.007.41V20a3 3 0 01-3 3H7.5a3 3 0 01-3-3V8.658c0-.28-.003-.556.007-.828l.509-1.527a3.126 3.126 0 011.852-1.894 6.539 6.539 0 002.246-.809l.208-.119.023-.013zM12 7.75A5 5 0 1012 17.75a5 5 0 000-10z" clipRule="evenodd" />
        </svg>
    )
}
