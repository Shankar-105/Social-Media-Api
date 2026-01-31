import { useState } from 'react';
import {
    Dialog,
    DialogContent,
} from '@/components/ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Heart, MessageCircle, Bookmark, Share2, MoreHorizontal, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { feedService } from '@/api/feedService';
import { socialService } from '@/api/socialService';
import CommentSection from '@/components/common/CommentSection';
import { cn } from '@/lib/utils';

interface PostDetailModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    postId: number | null;
}

export default function PostDetailModal({ open, onOpenChange, postId }: PostDetailModalProps) {
    const queryClient = useQueryClient();
    const [isLiked, setIsLiked] = useState(false);

    const { data: post, isLoading } = useQuery({
        queryKey: ['post', postId],
        queryFn: async () => {
            const data = await feedService.getPost(postId!);
            setIsLiked(data.is_liked);
            return data;
        },
        enabled: !!postId && open,
    });

    const likeMutation = useMutation({
        mutationFn: () => socialService.likePost(postId!, !isLiked),
        onSuccess: () => {
            setIsLiked(!isLiked);
            queryClient.invalidateQueries({ queryKey: ['post', postId] });
        },
    });

    if (!postId) return null;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-[90vw] md:max-w-[1000px] h-[90vh] md:h-[600px] p-0 overflow-hidden bg-white dark:bg-zinc-950 border-none gap-0">
                {isLoading ? (
                    <div className="h-full w-full flex items-center justify-center">
                        <Loader2 className="h-10 w-10 animate-spin text-primary" />
                    </div>
                ) : post ? (
                    <div className="flex flex-col md:flex-row h-full">
                        {/* Left: Image */}
                        <div className="w-full md:w-3/5 bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center relative group">
                            {post.media_type === 'video' ? (
                                <video src={post.media_url} controls className="h-full w-full object-contain" />
                            ) : (
                                <img
                                    src={post.media_url}
                                    alt={post.title}
                                    className="h-full w-full object-contain"
                                />
                            )}
                        </div>

                        {/* Right: Info & Comments */}
                        <div className="w-full md:w-2/5 flex flex-col h-full border-l border-zinc-100 dark:border-zinc-800">
                            {/* Header */}
                            <div className="p-4 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <Avatar className="h-8 w-8 ring-1 ring-zinc-100 dark:ring-zinc-800">
                                        <AvatarImage src={post.owner.profile_pic} />
                                        <AvatarFallback>{post.owner.username[0].toUpperCase()}</AvatarFallback>
                                    </Avatar>
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold leading-none">{post.owner.username}</span>
                                        <span className="text-[10px] text-zinc-500 uppercase font-medium tracking-tighter">Location</span>
                                    </div>
                                </div>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </div>

                            {/* Content & Comments */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                                <div className="flex space-x-3">
                                    <Avatar className="h-8 w-8">
                                        <AvatarImage src={post.owner.profile_pic} />
                                        <AvatarFallback>{post.owner.username[0].toUpperCase()}</AvatarFallback>
                                    </Avatar>
                                    <div className="flex-1 space-y-1">
                                        <p className="text-sm">
                                            <span className="font-bold mr-2">{post.owner.username}</span>
                                            {post.content}
                                        </p>
                                        <p className="text-[10px] text-zinc-400 uppercase">
                                            {formatDistanceToNow(new Date(post.created_at))} ago
                                        </p>
                                    </div>
                                </div>

                                <div className="pt-4">
                                    <CommentSection postId={post.id} />
                                </div>
                            </div>

                            {/* Actions & Input Box Logic usually inside CommentSection or here */}
                            {/* For Instagram feel, actions are right above the input */}
                            <div className="p-4 border-t border-zinc-100 dark:border-zinc-800 bg-white dark:bg-zinc-950">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-4">
                                        <button onClick={() => likeMutation.mutate()}>
                                            <Heart className={cn("h-6 w-6 transition-all", isLiked ? "fill-rose-500 text-rose-500 scale-110" : "hover:text-zinc-500")} />
                                        </button>
                                        <MessageCircle className="h-6 w-6 hover:text-zinc-500 transition-colors" />
                                        <Share2 className="h-6 w-6 hover:text-zinc-500 transition-colors" />
                                    </div>
                                    <Bookmark className="h-6 w-6 hover:text-zinc-500 transition-colors" />
                                </div>
                                <div className="space-y-1">
                                    <p className="text-sm font-bold">{post.likes} likes</p>
                                    <p className="text-[10px] text-zinc-400 uppercase tracking-wider">
                                        {new Date(post.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : null}
            </DialogContent>
        </Dialog>
    );
}
