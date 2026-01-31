import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { Edit, Search } from 'lucide-react';
import { useState } from 'react';

interface ChatSidebarProps {
    chats: any[];
    activeChat: any | null;
    onSelectChat: (chat: any) => void;
    isLoading: boolean;
}

export default function ChatSidebar({ chats, activeChat, onSelectChat, isLoading }: ChatSidebarProps) {
    const [search, setSearch] = useState('');

    const filteredChats = chats.filter(chat =>
        chat.username.toLowerCase().includes(search.toLowerCase()) ||
        (chat.nickname && chat.nickname.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <div className="w-full md:w-[350px] md:border-r border-zinc-200 dark:border-zinc-800 flex flex-col h-full bg-white dark:bg-black">
            <div className="p-4 flex flex-col space-y-4">
                <div className="flex items-center justify-between">
                    <h1 className="text-xl font-bold flex items-center">
                        {/* Example username if needed, or just "Messages" */}
                        <span className="mr-1">username</span>
                        <span className="text-xs align-top">v</span>
                    </h1>
                    <button className="text-zinc-800 dark:text-zinc-100">
                        <Edit className="h-6 w-6" />
                    </button>
                </div>

                {/* Tabs could go here: Primary / General / Requests */}

                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
                    <Input
                        placeholder="Search"
                        className="pl-9 bg-zinc-100 dark:bg-zinc-900 border-none h-9 rounded-xl focus-visible:ring-0"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            <ScrollArea className="flex-1">
                <div className="px-2 pb-2 space-y-1">
                    {/* Hardcoded "Note" bubbles could go here for "Notes" feature */}

                    <div className="flex items-center justify-between px-4 py-2">
                        <span className="font-bold text-base">Messages</span>
                        <span className="text-sm text-zinc-500 font-semibold cursor-pointer">Requests</span>
                    </div>

                    {isLoading ? (
                        <div className="text-center p-4 text-zinc-400 text-sm">Loading...</div>
                    ) : filteredChats.length === 0 ? (
                        <div className="text-center p-4 text-zinc-400 text-sm">No conversations found</div>
                    ) : (
                        filteredChats.map((chat) => (
                            <div
                                key={chat.id}
                                onClick={() => onSelectChat(chat)}
                                className={cn(
                                    "flex items-center space-x-3 p-3 rounded-xl cursor-pointer transition-colors max-w-full overflow-hidden",
                                    activeChat?.id === chat.id
                                        ? "bg-zinc-100 dark:bg-zinc-900"
                                        : "hover:bg-zinc-50 dark:hover:bg-zinc-900/50"
                                )}
                            >
                                <div className="relative shrink-0">
                                    <Avatar className="h-14 w-14">
                                        <AvatarImage src={chat.profile_pic} />
                                        <AvatarFallback>{chat.username[0].toUpperCase()}</AvatarFallback>
                                    </Avatar>
                                    {/* Online indicator - mocked for now */}
                                    <span className="absolute bottom-0 right-0 h-3.5 w-3.5 bg-green-500 border-2 border-white dark:border-black rounded-full"></span>
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-baseline mb-0.5">
                                        <span className={cn("text-sm truncate block max-w-[140px] text-zinc-900 dark:text-zinc-100",
                                            chat.last_message && !chat.last_message.is_read && !chat.last_message.is_me ? "font-bold" : "font-medium"
                                        )}>
                                            {chat.nickname || chat.username}
                                        </span>
                                        {chat.last_message && (
                                            <span className="text-[10px] text-zinc-400 shrink-0 ml-1">
                                                {chat.last_message.timestamp}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center text-xs text-zinc-500 truncate space-x-1">
                                        <span className={cn("truncate",
                                            chat.last_message && !chat.last_message.is_read && !chat.last_message.is_me ? "font-bold text-zinc-900 dark:text-zinc-100" : ""
                                        )}>
                                            {chat.last_message ? (
                                                <>
                                                    {chat.last_message.is_me && "You: "}
                                                    {chat.last_message.media_type && chat.last_message.media_type !== 'false'
                                                        ? 'Sent an attachment'
                                                        : chat.last_message.content}
                                                </>
                                            ) : (
                                                "Start a conversation"
                                            )}
                                        </span>
                                    </div>
                                </div>

                                {chat.last_message && !chat.last_message.is_read && !chat.last_message.is_me && (
                                    <div className="h-2.5 w-2.5 bg-blue-500 rounded-full shrink-0 ml-2"></div>
                                )}

                                {/* Unread dot - mocked */}
                                {/* <div className="h-2.5 w-2.5 bg-blue-500 rounded-full shrink-0"></div> */}
                            </div>
                        ))
                    )}
                </div>
            </ScrollArea>
        </div>
    );
}
