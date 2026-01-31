import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { socialService } from '@/api/socialService';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useState } from 'react';
import UnfollowModal from './UnfollowModal';

interface UserListModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    userId: number | null;
    type: 'followers' | 'following';
}

export default function UserListModal({ open, onOpenChange, title, userId, type }: UserListModalProps) {
    const currentUser = useAuthStore((state) => state.user);
    const queryClient = useQueryClient();
    const isMyProfile = currentUser?.id === userId;
    const [userToAction, setUserToAction] = useState<any>(null);
    const [actionType, setActionType] = useState<'unfollow' | 'remove' | null>(null);

    const { data: users = [], isLoading } = useQuery({
        queryKey: ['user-list', userId, type],
        queryFn: () => type === 'followers'
            ? socialService.getFollowers(userId!)
            : socialService.getFollowing(userId!),
        enabled: !!userId && open,
    });

    const followMutation = useMutation({
        mutationFn: (id: number) => socialService.followUser(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user-list', userId, type] });
            queryClient.invalidateQueries({ queryKey: ['profile', userId?.toString()] }); // update counts
        },
    });

    const unfollowMutation = useMutation({
        mutationFn: (id: number) => socialService.unfollowUser(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user-list', userId, type] });
            queryClient.invalidateQueries({ queryKey: ['profile', userId?.toString()] });
            setUserToAction(null);
            setActionType(null);
        },
    });

    const removeMutation = useMutation({
        mutationFn: (id: number) => socialService.removeFollower(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user-list', userId, type] });
            queryClient.invalidateQueries({ queryKey: ['profile', userId?.toString()] });
        },
    });

    const handleActionConfirm = () => {
        if (!userToAction) return;
        if (actionType === 'unfollow') {
            unfollowMutation.mutate(userToAction.id);
        }
    };

    return (
        <>
            <Dialog open={open} onOpenChange={onOpenChange}>
                <DialogContent className="sm:max-w-[400px] h-[500px] flex flex-col p-0 bg-white dark:bg-zinc-950 overflow-hidden shadow-2xl">
                    <DialogHeader className="p-4 border-b border-zinc-100 dark:border-zinc-800">
                        <DialogTitle className="text-center font-bold">{title}</DialogTitle>
                    </DialogHeader>
                    <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                        {isLoading ? (
                            <div className="h-full flex items-center justify-center">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        ) : users.length > 0 ? (
                            <div className="space-y-1">
                                {users.map((user: any) => {
                                    const isMe = user.id === currentUser?.id;
                                    // Logic:
                                    // 1. If viewing my followers -> Show Remove
                                    // 2. If viewing my following -> Show Following (click to unfollow)
                                    // 3. If viewing others -> Show Follow/Following based on status

                                    let button = null;

                                    if (isMe) {
                                        // Do nothing for myself in a list
                                    } else if (isMyProfile && type === 'followers') {
                                        // My followers list: Show Remove
                                        button = (
                                            <Button
                                                size="sm"
                                                className="font-bold h-8 px-4 rounded-lg bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-zinc-900 dark:text-zinc-100 border-none"
                                                onClick={() => removeMutation.mutate(user.id)}
                                                disabled={removeMutation.isPending}
                                            >
                                                {removeMutation.isPending ? 'Removing...' : 'Remove'}
                                            </Button>
                                        );
                                    } else {
                                        // Others list OR My following list
                                        if (user.is_following) {
                                            button = (
                                                <Button
                                                    size="sm"
                                                    variant="secondary"
                                                    className="font-bold h-8 px-4 rounded-lg focus-visible:ring-0 focus-visible:ring-offset-0"
                                                    onClick={() => {
                                                        setUserToAction(user);
                                                        setActionType('unfollow');
                                                    }}
                                                >
                                                    Following
                                                </Button>
                                            );
                                        } else {
                                            button = (
                                                <Button
                                                    size="sm"
                                                    className="font-bold h-8 px-4 rounded-lg bg-blue-500 hover:bg-blue-600 text-white focus-visible:ring-0 focus-visible:ring-offset-0"
                                                    onClick={() => followMutation.mutate(user.id)}
                                                    disabled={followMutation.isPending}
                                                >
                                                    {followMutation.isPending ? 'Following...' : 'Follow'}
                                                </Button>
                                            );
                                        }
                                    }

                                    return (
                                        <div key={user.id} className="flex items-center justify-between p-3 hover:bg-zinc-50 dark:hover:bg-zinc-900 rounded-xl transition-all group">
                                            <Link
                                                to={`/profile/${user.id}`}
                                                className="flex items-center space-x-3"
                                                onClick={() => onOpenChange(false)}
                                            >
                                                <Avatar className="h-11 w-11 shadow-sm transition-transform group-hover:scale-105">
                                                    <AvatarImage src={user.profile_pic} />
                                                    <AvatarFallback>{user.username[0].toUpperCase()}</AvatarFallback>
                                                </Avatar>
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-bold leading-none mb-1">{user.username}</span>
                                                    <span className="text-[11px] text-zinc-500 font-medium">
                                                        {user.nickname || `@${user.username}`}
                                                    </span>
                                                </div>
                                            </Link>
                                            {button}
                                        </div>
                                    )
                                })}
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-zinc-400 p-10 text-center">
                                <div className="h-16 w-16 bg-zinc-50 dark:bg-zinc-900 rounded-full flex items-center justify-center mb-4">
                                    <UsersIcon className="h-8 w-8 opacity-20" />
                                </div>
                                <h3 className="font-bold text-zinc-600 dark:text-zinc-300">No {title.toLowerCase()} yet</h3>
                                <p className="text-xs mt-1">When someone follows this user, you'll see them here.</p>
                            </div>
                        )}
                    </div>
                </DialogContent>
            </Dialog>

            {userToAction && actionType === 'unfollow' && (
                <UnfollowModal
                    isOpen={!!userToAction}
                    onClose={() => {
                        setUserToAction(null);
                        setActionType(null);
                    }}
                    onConfirm={handleActionConfirm}
                    user={userToAction}
                    isLoading={unfollowMutation.isPending}
                />
            )}
        </>
    );
}

function UsersIcon({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
    )
}
