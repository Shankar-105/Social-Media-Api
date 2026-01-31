import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { searchService } from '@/api/searchService';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Loader2, Search as SearchIcon, Grid, Users as UsersIcon, Heart, MessageCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import PostDetailModal from '@/components/common/PostDetailModal';

export default function Search() {
    const [query, setQuery] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const [searchType, setSearchType] = useState<'users' | 'posts'>('users');
    const [selectedPostId, setSelectedPostId] = useState<number | null>(null);
    const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedQuery(query);
            // Auto-switch to posts if query starts with #
            if (query.startsWith('#')) {
                setSearchType('posts');
            }
        }, 400);
        return () => clearTimeout(timer);
    }, [query]);

    const { data: results, isLoading } = useQuery({
        queryKey: ['search', debouncedQuery, searchType],
        queryFn: () => searchService.search({
            q: debouncedQuery,
            limit: 20
        }),
        enabled: debouncedQuery.length > 1,
    });

    return (
        <div className="max-w-4xl mx-auto space-y-8 p-4 md:p-8">
            <div className="space-y-4 text-center">
                <h1 className="text-3xl font-bold tracking-tight">Explore</h1>
                <p className="text-zinc-500 dark:text-zinc-400">Find people, posts, and hashtags from across the community.</p>
            </div>

            <div className="relative max-w-xl mx-auto">
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-400" />
                <Input
                    type="text"
                    placeholder="Search for @users or #hashtags..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pl-12 h-14 text-lg bg-zinc-50 dark:bg-zinc-900 border-none rounded-2xl shadow-sm focus-visible:ring-2 focus-visible:ring-primary/20 transition-all"
                />
            </div>

            <div className="flex justify-center border-b border-zinc-100 dark:border-zinc-800">
                <button
                    onClick={() => setSearchType('users')}
                    className={cn(
                        "flex items-center space-x-2 px-8 py-4 font-semibold transition-colors relative",
                        searchType === 'users' ? "text-primary" : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-300"
                    )}
                >
                    <UsersIcon className="h-4 w-4" />
                    <span>Users</span>
                    {searchType === 'users' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary animate-in fade-in" />}
                </button>
                <button
                    onClick={() => setSearchType('posts')}
                    className={cn(
                        "flex items-center space-x-2 px-8 py-4 font-semibold transition-colors relative",
                        searchType === 'posts' ? "text-primary" : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-300"
                    )}
                >
                    <Grid className="h-4 w-4" />
                    <span>Posts</span>
                    {searchType === 'posts' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary animate-in fade-in" />}
                </button>
            </div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center p-20 space-y-4">
                    <Loader2 className="h-10 w-10 animate-spin text-primary" />
                    <p className="text-sm font-medium animate-pulse">Searching the universe...</p>
                </div>
            ) : results && debouncedQuery ? (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {searchType === 'users' && results.result_type === 'users' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {results.users.length > 0 ? (
                                results.users.map((user: any) => (
                                    <Link
                                        key={user.id}
                                        to={`/profile/${user.id}`}
                                        className="flex items-center space-x-4 p-4 bg-white dark:bg-zinc-900 border border-zinc-100 dark:border-zinc-800 rounded-2xl hover:shadow-md transition-all group"
                                    >
                                        <Avatar className="h-14 w-14 ring-2 ring-primary/5 group-hover:ring-primary/20 transition-all">
                                            <AvatarImage src={user.profile_pic} alt={user.username} />
                                            <AvatarFallback>{user.username[0].toUpperCase()}</AvatarFallback>
                                        </Avatar>
                                        <div className="flex-1">
                                            <p className="font-bold text-lg leading-tight">{user.username}</p>
                                            <p className="text-sm text-zinc-500">{user.nickname || `@${user.username}`}</p>
                                        </div>
                                    </Link>
                                ))
                            ) : (
                                <NoResults query={debouncedQuery} />
                            )}
                        </div>
                    )}

                    {searchType === 'posts' && results.result_type === 'posts' && (
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-6">
                            {results.posts.length > 0 ? (
                                results.posts.map((post: any) => (
                                    <div
                                        key={post.id}
                                        onClick={() => {
                                            setSelectedPostId(post.id);
                                            setIsPostDetailOpen(true);
                                        }}
                                        className="group relative aspect-square rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 shadow-sm cursor-pointer"
                                    >
                                        <img src={post.media_url} alt={post.title} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-6 text-white font-bold backdrop-blur-[2px]">
                                            <div className="flex items-center space-x-1.5">
                                                <Heart className="h-6 w-6 fill-white" />
                                                <span>{post.likes}</span>
                                            </div>
                                            <div className="flex items-center space-x-1.5">
                                                <MessageCircle className="h-6 w-6 fill-white" />
                                                <span>{post.comments_count}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="col-span-full">
                                    <NoResults query={debouncedQuery} />
                                </div>
                            )}
                        </div>
                    )}
                </div>
            ) : (
                <div className="text-center p-20 text-zinc-400 space-y-4">
                    <SearchIcon className="h-20 w-20 mx-auto opacity-20" />
                    <div className="space-y-1">
                        <p className="text-xl font-bold text-zinc-300 dark:text-zinc-600">Start exploring</p>
                        <p className="text-sm">Search for friends, topics, or trends</p>
                    </div>
                </div>
            )}

            <PostDetailModal
                open={isPostDetailOpen}
                onOpenChange={setIsPostDetailOpen}
                postId={selectedPostId}
            />
        </div>
    );
}

function NoResults({ query }: { query: string }) {
    return (
        <div className="flex flex-col items-center justify-center p-12 text-center space-y-4">
            <div className="bg-zinc-50 dark:bg-zinc-900 p-6 rounded-full">
                <SearchIcon className="h-10 w-10 text-zinc-300" />
            </div>
            <div className="space-y-1">
                <h3 className="text-lg font-bold">No results found</h3>
                <p className="text-sm text-zinc-500">We couldn't find anything matching "{query}"</p>
            </div>
        </div>
    );
}
