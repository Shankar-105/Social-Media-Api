import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { chatService } from '@/api/chatService';
import { socialService } from '@/api/socialService';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Search, Loader2, Send } from 'lucide-react';

interface SharePostModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    postId: number;
}

export default function SharePostModal({ open, onOpenChange, postId }: SharePostModalProps) {
    const [search, setSearch] = useState('');

    // In a real app, we'd fetch actual recent chats or followers
    const { data: chats, isLoading } = useQuery({
        queryKey: ['recentChats'],
        queryFn: () => chatService.getRecentChats(),
        enabled: open,
    });

    const shareMutation = useMutation({
        mutationFn: (receiverId: number) => socialService.sharePost(postId, receiverId),
        onSuccess: () => {
            onOpenChange(false);
            // Show toast or notification
        },
    });

    const filteredChats = chats?.filter((chat: any) =>
        chat.username.toLowerCase().includes(search.toLowerCase())
    ) || [];

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[400px] h-[500px] flex flex-col p-0 bg-white dark:bg-zinc-950">
                <DialogHeader className="p-4 border-b">
                    <DialogTitle className="text-center font-bold">Share</DialogTitle>
                </DialogHeader>

                <div className="p-4 border-b">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                        <Input
                            placeholder="Search..."
                            className="pl-10 h-9 bg-zinc-50 dark:bg-zinc-900 border-none"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                    {isLoading ? (
                        <div className="flex justify-center p-10"><Loader2 className="h-6 w-6 animate-spin" /></div>
                    ) : filteredChats.length > 0 ? (
                        filteredChats.map((chat: any) => (
                            <div key={chat.id} className="flex items-center justify-between p-2 hover:bg-zinc-50 dark:hover:bg-zinc-900 rounded-lg transition-colors">
                                <div className="flex items-center space-x-3">
                                    <Avatar className="h-10 w-10">
                                        <AvatarImage src={chat.profile_pic} />
                                        <AvatarFallback>{chat.username[0].toUpperCase()}</AvatarFallback>
                                    </Avatar>
                                    <div className="flex flex-col text-left">
                                        <span className="text-sm font-semibold">{chat.username}</span>
                                        <span className="text-xs text-zinc-500">{chat.nickname || chat.username}</span>
                                    </div>
                                </div>
                                <Button
                                    size="sm"
                                    onClick={() => shareMutation.mutate(chat.id)}
                                    disabled={shareMutation.isPending}
                                >
                                    {shareMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Send'}
                                </Button>
                            </div>
                        ))
                    ) : (
                        <div className="p-10 text-center text-zinc-500">
                            <p className="text-sm">No results found.</p>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
