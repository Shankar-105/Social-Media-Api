import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '@/api/userService';
import { socialService } from '@/api/socialService';
import { Loader2, Settings, Grid, Heart, Bookmark, MessageCircle, Users as UsersIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/authStore';
import EditProfileModal from '@/components/common/EditProfileModal';
import UserListModal from '@/components/common/UserListModal';
import PostDetailModal from '@/components/common/PostDetailModal';
import UnfollowModal from '@/components/common/UnfollowModal';

export default function Profile() {
    const { userId } = useParams<{ userId: string }>();
    const navigate = useNavigate();
    const currentUser = useAuthStore((state) => state.user);
    const isOwnProfile = currentUser?.id.toString() === userId;
    const queryClient = useQueryClient();

    const { data: profile, isLoading: isProfileLoading, error: profileError } = useQuery({
        queryKey: ['profile', userId],
        queryFn: () => userService.getProfile(userId!),
        enabled: !!userId,
    });

    const { data: postsData, isLoading: isPostsLoading } = useQuery({
        queryKey: ['userPosts', userId],
        queryFn: () => userService.getUserPosts(userId!),
        enabled: !!userId,
    });

    const isLoading = isProfileLoading || isPostsLoading;
    const error = profileError;

    const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);
    const [selectedPostId, setSelectedPostId] = useState<number | null>(null);
    const [isUnfollowModalOpen, setIsUnfollowModalOpen] = useState(false);

    // Derived state from profile data provided by backend
    const isFollowing = profile?.is_following || false;

    const followMutation = useMutation({
        mutationFn: () => socialService.followUser(Number(userId)),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['profile', userId] });
        },
    });

    const unfollowMutation = useMutation({
        mutationFn: () => socialService.unfollowUser(Number(userId)),
        onSuccess: () => {
            setIsUnfollowModalOpen(false);
            queryClient.invalidateQueries({ queryKey: ['profile', userId] });
        },
    });

    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isUserListOpen, setIsUserListOpen] = useState(false);
    const [userListTitle, setUserListTitle] = useState('');
    const [listType, setListType] = useState<'followers' | 'following'>('followers');

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-20">
                <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
            </div>
        );
    }

    if (error || !profile) {
        return (
            <div className="text-center p-20 text-destructive">
                User not found.
            </div>
        );
    }

    const posts = postsData?.posts || [];

    return (
        <div className="flex flex-col space-y-10 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-20 px-4 md:px-10">
                <div className="h-32 w-32 md:h-40 md:w-40 rounded-full bg-linear-to-tr from-yellow-400 via-rose-500 to-purple-600 p-[3px] shrink-0">
                    <div className="h-full w-full rounded-full bg-white dark:bg-black p-1">
                        <div className="h-full w-full rounded-full bg-zinc-100 dark:bg-zinc-900 border overflow-hidden">
                            {profile.profile_picture ? (
                                <img src={profile.profile_picture} alt={profile.username} className="h-full w-full object-cover" />
                            ) : (
                                <div className="h-full w-full flex items-center justify-center text-5xl font-bold text-zinc-300">
                                    {profile.username[0].toUpperCase()}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex-1 space-y-6">
                    <div className="flex flex-wrap items-center gap-4">
                        <h1 className="text-xl font-medium">{profile.username}</h1>
                        {isOwnProfile ? (
                            <div className="flex items-center gap-2">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    className="font-bold px-4 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 border-none"
                                    onClick={() => setIsEditModalOpen(true)}
                                >
                                    Edit profile
                                </Button>
                                <Button variant="secondary" size="sm" className="font-bold px-4 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 border-none">
                                    View archive
                                </Button>
                                <Button variant="ghost" size="icon" className="h-9 w-9">
                                    <Settings className="h-5 w-5" />
                                </Button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                {isFollowing ? (
                                    <Button
                                        size="sm"
                                        variant="secondary"
                                        className="font-bold px-6 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-900 dark:text-zinc-100 border-none"
                                        onClick={() => setIsUnfollowModalOpen(true)}
                                    >
                                        Following
                                    </Button>
                                ) : (
                                    <Button
                                        size="sm"
                                        className="font-bold px-6 h-9 rounded-lg bg-primary hover:bg-primary/90 text-white border-none focus-visible:ring-0 focus-visible:ring-offset-0"
                                        onClick={() => followMutation.mutate()}
                                        disabled={followMutation.isPending}
                                    >
                                        Follow
                                    </Button>
                                )}
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    className="font-bold px-6 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 border-none"
                                    onClick={() => navigate('/messages', { state: { chatWith: profile } })}
                                >
                                    Message
                                </Button>
                                <Button variant="secondary" size="icon" className="h-9 w-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 border-none">
                                    <UsersIcon className="h-4 w-4" />
                                </Button>
                            </div>
                        )}
                    </div>

                    <div className="flex items-center space-x-10 text-[16px]">
                        <div><span className="font-bold">{profile.posts_count || posts.length}</span> posts</div>
                        <button
                            className="hover:opacity-70 transition-opacity"
                            onClick={() => {
                                setUserListTitle('Followers');
                                setListType('followers');
                                setIsUserListOpen(true);
                            }}
                        >
                            <span className="font-bold">{profile.followers_count || 0}</span> followers
                        </button>
                        <button
                            className="hover:opacity-70 transition-opacity"
                            onClick={() => {
                                setUserListTitle('Following');
                                setListType('following');
                                setIsUserListOpen(true);
                            }}
                        >
                            <span className="font-bold">{profile.following_count || 0}</span> following
                        </button>
                    </div>

                    <div className="space-y-1">
                        <div className="font-bold text-sm">{profile.nickname || profile.username}</div>
                        {profile.bio && <p className="text-sm whitespace-pre-wrap pt-1">{profile.bio}</p>}
                    </div>
                </div>
            </div>


            <div className="border-t border-zinc-200 dark:border-zinc-800">
                <div className="flex justify-center space-x-14">
                    <button className="flex items-center space-x-2 py-4 border-t border-zinc-900 dark:border-white -mt-[1px] uppercase text-[12px] font-bold tracking-widest transition-opacity">
                        <Grid className="h-4 w-4" />
                        <span>Posts</span>
                    </button>
                    <button className="flex items-center space-x-2 py-4 text-zinc-400 uppercase text-[12px] font-bold tracking-widest hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors">
                        <Bookmark className="h-4 w-4" />
                        <span>Saved</span>
                    </button>
                    <button className="flex items-center space-x-2 py-4 text-zinc-400 uppercase text-[12px] font-bold tracking-widest hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors">
                        <Heart className="h-4 w-4" />
                        <span>Tagged</span>
                    </button>
                </div>

                <div className="grid grid-cols-3 gap-1 md:gap-1 mt-4">
                    {posts.length > 0 ? (
                        posts.map((post: any) => (
                            <div
                                key={post.id}
                                className="relative aspect-square bg-zinc-100 dark:bg-zinc-900 overflow-hidden cursor-pointer group"
                                onClick={() => {
                                    setSelectedPostId(post.id);
                                    setIsPostDetailOpen(true);
                                }}
                            >
                                {post.media_type === 'video' ? (
                                    <video src={post.media_url} className="h-full w-full object-cover" />
                                ) : (
                                    <img src={post.media_url} alt={post.title} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
                                )}
                                <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-4 md:space-x-8 text-white font-bold">
                                    <div className="flex items-center space-x-2">
                                        <Heart className="h-6 w-6 fill-white" />
                                        <span>{post.likes}</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <MessageCircle className="h-6 w-6 fill-white" />
                                        <span>{post.comments_count}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-3 flex flex-col items-center justify-center p-20 space-y-4">
                            <div className="h-20 w-20 rounded-full border-2 border-zinc-200 dark:border-zinc-800 flex items-center justify-center">
                                <Grid className="h-10 w-10 text-zinc-400" />
                            </div>
                            <div className="text-center">
                                <h2 className="text-2xl font-black">No Posts Yet</h2>
                                <p className="text-sm text-zinc-500">When you share photos, they'll appear on your profile.</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <EditProfileModal
                open={isEditModalOpen}
                onOpenChange={setIsEditModalOpen}
                profile={profile}
            />
            <UserListModal
                open={isUserListOpen}
                onOpenChange={setIsUserListOpen}
                title={userListTitle}
                userId={Number(userId)}
                type={listType}
            />
            <PostDetailModal
                open={isPostDetailOpen}
                onOpenChange={setIsPostDetailOpen}
                postId={selectedPostId}
            />
            {profile && (
                <UnfollowModal
                    isOpen={isUnfollowModalOpen}
                    onClose={() => setIsUnfollowModalOpen(false)}
                    onConfirm={() => unfollowMutation.mutate()}
                    user={profile}
                    isLoading={unfollowMutation.isPending}
                />
            )}
        </div>
    );
}
