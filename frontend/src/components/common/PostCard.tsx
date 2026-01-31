import { useState } from 'react';
import { MoreHorizontal, Heart, MessageCircle, Send, Bookmark } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { socialService } from '@/api/socialService';
import CommentSection from './CommentSection';

interface PostCardProps {
    post: {
        id: number;
        title: string;
        content: string;
        media_url?: string;
        media_type?: string;
        likes: number;
        comments_count: number;
        created_at: string;
        is_liked?: boolean;
        owner: {
            id: number;
            username: string;
            profile_pic?: string;
        };
    };
}

export default function PostCard({ post }: PostCardProps) {
    const [isLiked, setIsLiked] = useState(post.is_liked || false);
    const [likesCount, setLikesCount] = useState(post.likes);
    const [showComments, setShowComments] = useState(false);
    const queryClient = useQueryClient();

    const likeMutation = useMutation({
        mutationFn: () => socialService.likePost(post.id, !isLiked),
        onMutate: () => {
            setIsLiked(!isLiked);
            setLikesCount(prev => isLiked ? prev - 1 : prev + 1);
        },
        onError: () => {
            setIsLiked(!isLiked);
            setLikesCount(prev => isLiked ? prev + 1 : prev - 1);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['homeFeed'] });
        },
    });

    return (
        <Card className="border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 overflow-hidden max-w-[470px] mx-auto w-full">
            <CardHeader className="flex flex-row items-center justify-between p-3">
                <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 rounded-full bg-zinc-200 dark:bg-zinc-800 border overflow-hidden">
                        {post.owner.profile_pic ? (
                            <img src={post.owner.profile_pic} alt={post.owner.username} className="h-full w-full object-cover" />
                        ) : (
                            <div className="h-full w-full flex items-center justify-center text-xs font-bold">
                                {post.owner.username[0].toUpperCase()}
                            </div>
                        )}
                    </div>
                    <span className="font-semibold text-sm hover:text-zinc-500 cursor-pointer">
                        {post.owner.username}
                    </span>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </CardHeader>

            <CardContent className="p-0 border-y border-zinc-100 dark:border-zinc-900">
                {post.media_type === 'video' ? (
                    <video src={post.media_url} controls className="w-full aspect-square object-cover" />
                ) : post.media_url ? (
                    <img src={post.media_url} alt={post.title} className="w-full aspect-square object-cover" />
                ) : (
                    <div className="aspect-square bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center p-8 text-center">
                        <span className="text-zinc-500 text-sm">{post.content}</span>
                    </div>
                )}
            </CardContent>

            <CardFooter className="flex flex-col items-start p-3 space-y-2">
                <div className="flex items-center justify-between w-full">
                    <div className="flex items-center space-x-4">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="p-0 h-auto hover:bg-transparent"
                            onClick={() => likeMutation.mutate()}
                            disabled={likeMutation.isPending}
                        >
                            <Heart className={cn(
                                "h-6 w-6 transition-all",
                                isLiked ? "fill-red-500 text-red-500" : "hover:text-zinc-500"
                            )} />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="p-0 h-auto hover:bg-transparent"
                            onClick={() => setShowComments(!showComments)}
                        >
                            <MessageCircle className={cn(
                                "h-6 w-6 transition-colors",
                                showComments ? "fill-zinc-900 dark:fill-zinc-50" : "hover:text-zinc-500"
                            )} />
                        </Button>
                        <Button variant="ghost" size="icon" className="p-0 h-auto hover:bg-transparent">
                            <Send className="h-6 w-6 hover:text-zinc-500 transition-colors" />
                        </Button>
                    </div>
                    <Button variant="ghost" size="icon" className="p-0 h-auto hover:bg-transparent">
                        <Bookmark className="h-6 w-6 hover:text-zinc-500 transition-colors" />
                    </Button>
                </div>

                <div className="text-sm font-bold">
                    {likesCount} likes
                </div>

                <div className="text-sm">
                    <span className="font-bold mr-2">{post.owner.username}</span>
                    <span className="text-zinc-700 dark:text-zinc-300">{post.title}</span>
                </div>

                {post.comments_count > 0 && !showComments && (
                    <button
                        onClick={() => setShowComments(true)}
                        className="text-sm text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 transition-colors"
                    >
                        View all {post.comments_count} comments
                    </button>
                )}

                <div className="text-[10px] text-zinc-400 uppercase tracking-tight">
                    {formatDistanceToNow(new Date(post.created_at))} ago
                </div>

                {showComments && <CommentSection postId={post.id} />}
            </CardFooter>
        </Card>
    );
}
