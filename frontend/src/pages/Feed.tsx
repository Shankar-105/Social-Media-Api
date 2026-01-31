import { useQuery } from '@tanstack/react-query';
import { feedService } from '@/api/feedService';
import PostCard from '@/components/common/PostCard';
import { Loader2 } from 'lucide-react';

export default function Feed() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['homeFeed'],
        queryFn: () => feedService.getHomeFeed(20, 0),
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-20">
                <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center p-20 text-destructive">
                Failed to load feed. Please try again later.
            </div>
        );
    }

    const posts = data?.posts || [];

    return (
        <div className="flex flex-col items-center space-y-4 max-w-[470px] mx-auto">
            {posts.length > 0 ? (
                posts.map((post: any) => (
                    <PostCard key={post.id} post={post} />
                ))
            ) : (
                <div className="text-center p-20 text-zinc-500">
                    <p className="text-lg font-semibold">Welcome to InstaClone</p>
                    <p className="text-sm">Start following people to see their posts here.</p>
                </div>
            )}
        </div>
    );
}
