import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { commentService } from '@/api/commentService';
import { socialService } from '@/api/socialService';
import { useAuthStore } from '@/store/authStore';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Heart, MessageCircle, MoreHorizontal, Trash2, Edit2, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface CommentProps {
    postId: number;
}

export default function CommentSection({ postId }: CommentProps) {
    const [content, setContent] = useState('');
    const user = useAuthStore((state) => state.user);
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ['comments', postId],
        queryFn: () => commentService.getComments(postId),
    });

    const createMutation = useMutation({
        mutationFn: (content: string) => commentService.createComment(postId, content),
        onSuccess: () => {
            setContent('');
            queryClient.invalidateQueries({ queryKey: ['comments', postId] });
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;
        createMutation.mutate(content);
    };

    const comments = data?.comments || [];

    return (
        <div className="space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-900 mt-4">
            <h4 className="text-sm font-semibold flex items-center space-x-2">
                <MessageCircle className="h-4 w-4" />
                <span>Comments ({data?.pagination?.total || 0})</span>
            </h4>

            <form onSubmit={handleSubmit} className="flex items-center space-x-2">
                <Input
                    placeholder="Add a comment..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="flex-1 bg-zinc-50 dark:bg-zinc-900 border-none focus-visible:ring-1 focus-visible:ring-zinc-400"
                    disabled={createMutation.isPending}
                />
                <Button
                    type="submit"
                    variant="ghost"
                    disabled={!content.trim() || createMutation.isPending}
                    className="text-zinc-900 dark:text-zinc-50 font-semibold"
                >
                    {createMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Post'}
                </Button>
            </form>

            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {isLoading ? (
                    <div className="flex justify-center p-4">
                        <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
                    </div>
                ) : comments.length > 0 ? (
                    comments.map((comment: any) => (
                        <CommentItem key={comment.id} comment={comment} postId={postId} />
                    ))
                ) : (
                    <p className="text-sm text-zinc-500 text-center py-4">No comments yet.</p>
                )}
            </div>
        </div>
    );
}

function CommentItem({ comment, postId }: { comment: any; postId: number }) {
    const user = useAuthStore((state) => state.user);
    const queryClient = useQueryClient();
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState(comment.content);
    const isOwner = user?.id === comment.user.id;

    const deleteMutation = useMutation({
        mutationFn: () => commentService.deleteComment(comment.id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['comments', postId] });
        },
    });

    const editMutation = useMutation({
        mutationFn: (newContent: string) => commentService.editComment(comment.id, newContent),
        onSuccess: () => {
            setIsEditing(false);
            queryClient.invalidateQueries({ queryKey: ['comments', postId] });
        },
    });

    const likeMutation = useMutation({
        mutationFn: () => socialService.likeComment(comment.id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['comments', postId] });
        },
    });

    const handleEdit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!editContent.trim()) return;
        editMutation.mutate(editContent);
    };

    return (
        <div className="flex space-x-3 group">
            <Avatar className="h-8 w-8 shrink-0">
                <AvatarImage src={comment.user.profile_pic} />
                <AvatarFallback>{comment.user.username[0].toUpperCase()}</AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold">{comment.user.username}</span>
                        <span className="text-xs text-zinc-500">
                            {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                        </span>
                    </div>
                    {isOwner && (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => setIsEditing(true)}>
                                    <Edit2 className="mr-2 h-4 w-4" /> Edit
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                    onClick={() => deleteMutation.mutate()}
                                    className="text-destructive focus:text-destructive"
                                >
                                    <Trash2 className="mr-2 h-4 w-4" /> Delete
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>

                {isEditing ? (
                    <form onSubmit={handleEdit} className="space-y-2">
                        <Input
                            value={editContent}
                            onChange={(e) => setEditContent(e.target.value)}
                            className="text-sm h-8"
                            autoFocus
                        />
                        <div className="flex space-x-2">
                            <Button type="submit" size="sm" disabled={editMutation.isPending}>Save</Button>
                            <Button type="button" variant="ghost" size="sm" onClick={() => setIsEditing(false)}>Cancel</Button>
                        </div>
                    </form>
                ) : (
                    <p className="text-sm text-zinc-700 dark:text-zinc-300">{comment.content}</p>
                )}

                <div className="flex items-center space-x-4 pt-1">
                    <button
                        onClick={() => likeMutation.mutate()}
                        className="flex items-center space-x-1 text-xs text-zinc-500 hover:text-red-500 transition-colors"
                    >
                        <Heart className={cn("h-3 w-3", comment.likes > 0 && "fill-red-500 text-red-500")} />
                        <span>{comment.likes}</span>
                    </button>
                    <button className="text-xs text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors">
                        Reply
                    </button>
                </div>
            </div>
        </div>
    );
}
