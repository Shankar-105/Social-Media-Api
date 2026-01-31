import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { Smile, Reply, MoreVertical, Edit2, Trash2 } from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';

interface MessageItemProps {
    message: any;
    onReact: (msgId: number, emoji: string) => void;
    onReply: (message: any) => void;
    onEdit: (msgId: number, newContent: string) => void;
    onDelete: (msgId: number) => void;
}

export default function MessageItem({ message, onReact, onReply, onEdit, onDelete }: MessageItemProps) {
    const user = useAuthStore((state) => state.user);
    const isMe = message.from === user?.id || message.sender_id === user?.id;
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState(message.content);

    const handleEditSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (editContent.trim() && editContent !== message.content) {
            onEdit(message.id, editContent);
        }
        setIsEditing(false);
    };

    return (
        <div className={cn("flex flex-col mb-4", isMe ? "items-end" : "items-start")}>
            <div className={cn("flex items-start group", isMe ? "flex-row-reverse" : "flex-row")}>
                <div className={cn(
                    "relative max-w-[280px] md:max-w-[400px] p-3 rounded-2xl text-sm",
                    isMe
                        ? "bg-zinc-900 text-white rounded-tr-none"
                        : "bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-tl-none"
                )}>
                    {message.reply_to && (
                        <div className="mb-2 p-2 bg-white/10 rounded text-[10px] border-l-2 border-primary overflow-hidden line-clamp-2 italic opacity-80">
                            {message.reply_to.content}
                        </div>
                    )}

                    {isEditing ? (
                        <form onSubmit={handleEditSubmit} className="space-y-2 min-w-[200px]">
                            <textarea
                                value={editContent}
                                onChange={(e) => setEditContent(e.target.value)}
                                className="w-full bg-transparent border-none focus:ring-0 text-sm resize-none"
                                autoFocus
                            />
                            <div className="flex justify-end space-x-2">
                                <Button type="button" variant="ghost" size="sm" onClick={() => setIsEditing(false)}>Cancel</Button>
                                <Button type="submit" size="sm">Save</Button>
                            </div>
                        </form>
                    ) : (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                    )}

                    {message.reactions && message.reactions.length > 0 && (
                        <div className="absolute -bottom-2 -right-2 flex -space-x-1">
                            {message.reactions.map((r: any, i: number) => (
                                <span key={i} className="bg-white dark:bg-zinc-800 border rounded-full px-1 text-[10px] shadow-sm">
                                    {r.reaction}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                {!isEditing && (
                    <div className={cn(
                        "flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity px-2 self-center",
                        isMe ? "flex-row-reverse space-x-reverse" : "flex-row"
                    )}>
                        <button
                            onClick={() => onReply(message)}
                            className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-400 hover:text-zinc-600"
                        >
                            <Reply className="h-4 w-4" />
                        </button>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <button className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-400 hover:text-zinc-600">
                                    <Smile className="h-4 w-4" />
                                </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent className="flex p-1 gap-1">
                                {['❤️', '😂', '😮', '😢', '🔥', '👍'].map((emoji) => (
                                    <button
                                        key={emoji}
                                        onClick={() => onReact(message.id, emoji)}
                                        className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded text-lg"
                                    >
                                        {emoji}
                                    </button>
                                ))}
                            </DropdownMenuContent>
                        </DropdownMenu>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <button className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-400 hover:text-zinc-600">
                                    <MoreVertical className="h-4 w-4" />
                                </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align={isMe ? "end" : "start"}>
                                {isMe && (
                                    <DropdownMenuItem onClick={() => setIsEditing(true)}>
                                        <Edit2 className="mr-2 h-4 w-4" /> Edit
                                    </DropdownMenuItem>
                                )}
                                <DropdownMenuItem
                                    onClick={() => onDelete(message.id)}
                                    className="text-destructive focus:text-destructive"
                                >
                                    <Trash2 className="mr-2 h-4 w-4" /> Delete
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                )}
            </div>
            <span className="text-[10px] text-zinc-400 mt-1 px-1">
                {message.created_at && format(new Date(message.created_at), 'HH:mm')}
                {message.is_edited && ' (edited)'}
                {isMe && message.is_read && ' • Read'}
            </span>
        </div>
    );
}
