import { useQuery } from '@tanstack/react-query';
import { searchService } from '@/api/searchService';
import { Loader2, Heart, MessageCircle } from 'lucide-react';

export default function Explore() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['explore'],
        queryFn: () => searchService.getExplorePosts(30, 0),
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
                Failed to load explore posts. Please try again later.
            </div>
        );
    }

    const posts = data?.posts || [];

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold px-4">Explore</h2>

            <div className="grid grid-cols-3 gap-1 md:gap-4">
                {posts.length > 0 ? (
                    posts.map((post: any) => (
                        <div key={post.id} className="relative aspect-square bg-zinc-100 dark:bg-zinc-900 overflow-hidden cursor-pointer group">
                            {post.media_type === 'video' ? (
                                <video src={post.media_url} className="h-full w-full object-cover" />
                            ) : post.media_url ? (
                                <img src={post.media_url} alt={post.title} className="h-full w-full object-cover" />
                            ) : (
                                <div className="h-full w-full flex items-center justify-center p-4 text-center bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-900 dark:to-zinc-800">
                                    <span className="text-sm text-zinc-500">{post.content}</span>
                                </div>
                            )}
                            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-6 text-white font-bold">
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
                        <h2 className="text-2xl font-bold">No posts to explore yet</h2>
                        <p className="text-zinc-500">Check back later for new content!</p>
                    </div>
                )}
            </div>
        </div>
    );
}
