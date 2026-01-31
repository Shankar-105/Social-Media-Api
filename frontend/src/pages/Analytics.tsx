import { useQueries } from '@tanstack/react-query';
import { analyticsService } from '@/api/analyticsService';
import { userService } from '@/api/userService';
import {
    TrendingUp,
    MessageSquare,
    Heart,
    Users,
    LayoutGrid,
    Loader2,
    ArrowUpRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function Analytics() {
    const results = useQueries({
        queries: [
            { queryKey: ['meProfile'], queryFn: () => userService.getMyProfile() },
            { queryKey: ['voteStats'], queryFn: () => analyticsService.getVoteStats() },
            { queryKey: ['commentStats'], queryFn: () => analyticsService.getCommentStats() },
            { queryKey: ['myPosts'], queryFn: () => analyticsService.getMyPosts(5) },
        ]
    });

    const [profile, voteStats, commentStats, recentPosts] = results;
    const isLoading = results.some(r => r.isLoading);

    if (isLoading) {
        return (
            <div className="flex h-[80vh] items-center justify-center">
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
            </div>
        );
    }

    const p = profile.data;
    const v = voteStats.data;
    const c = commentStats.data;

    const statsCards = [
        { label: 'Followers', value: p?.followers_count || 0, icon: Users, color: 'text-blue-500' },
        { label: 'Total Posts', value: p?.posts_count || 0, icon: LayoutGrid, color: 'text-purple-500' },
        { label: 'Likes Given', value: v?.liked_posts_count || 0, icon: Heart, color: 'text-rose-500' },
        { label: 'Total Comments', value: c?.total_comments || 0, icon: MessageSquare, color: 'text-amber-500' },
    ];

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-8 pb-20">
            <header className="space-y-2">
                <div className="flex items-center space-x-2 text-primary font-bold">
                    <TrendingUp className="h-5 w-5" />
                    <span>Insights</span>
                </div>
                <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
                <p className="text-zinc-500">Track your engagement and community reach.</p>
            </header>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {statsCards.map((stat, i) => (
                    <Card key={i} className="border-none bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md transition-all rounded-3xl group overflow-hidden relative">
                        <CardHeader className="pb-2">
                            <stat.icon className={cn("h-6 w-6 mb-2", stat.color)} />
                            <CardTitle className="text-sm font-medium text-zinc-500">{stat.label}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold">{stat.value}</div>
                            <div className="mt-2 text-[10px] text-zinc-400 font-bold uppercase tracking-wider">Across all activity</div>
                        </CardContent>
                        <div className="absolute -right-4 -bottom-4 h-24 w-24 bg-zinc-50 dark:bg-zinc-800/20 rounded-full group-hover:scale-110 transition-transform" />
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Voter Distribution */}
                <Card className="border-none bg-white dark:bg-zinc-900 shadow-sm rounded-3xl p-6">
                    <CardHeader className="px-0 pt-0">
                        <CardTitle className="text-lg">Engagement Balance</CardTitle>
                        <p className="text-xs text-zinc-500">Liked vs Disliked posts</p>
                    </CardHeader>
                    <CardContent className="px-0 space-y-8">
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs font-bold px-1">
                                <span className="text-rose-500 uppercase tracking-tighter">Liked ({v?.liked_posts_count})</span>
                                <span className="text-zinc-400 uppercase tracking-tighter">Disliked ({v?.disliked_posts_count})</span>
                            </div>
                            <div className="h-4 w-full bg-zinc-100 dark:bg-zinc-800 rounded-full flex overflow-hidden">
                                {v?.liked_posts_count + v?.disliked_posts_count > 0 ? (
                                    <>
                                        <div
                                            className="h-full bg-rose-500 transition-all duration-1000"
                                            style={{ width: `${(v?.liked_posts_count / (v?.liked_posts_count + v?.disliked_posts_count)) * 100}%` }}
                                        />
                                        <div className="h-full bg-zinc-400 dark:bg-zinc-600 transition-all duration-1000" style={{ flex: 1 }} />
                                    </>
                                ) : (
                                    <div className="h-full bg-zinc-200 dark:bg-zinc-700 w-full" />
                                )}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 rounded-2xl bg-zinc-50 dark:bg-zinc-800/40">
                                <p className="text-[10px] font-bold text-zinc-400 uppercase mb-1">Comment Reach</p>
                                <div className="text-2xl font-bold">{c?.unique_posts_commented}</div>
                                <p className="text-[10px] text-zinc-500">Unique posts found</p>
                            </div>
                            <div className="p-4 rounded-2xl bg-zinc-50 dark:bg-zinc-800/40">
                                <p className="text-[10px] font-bold text-zinc-400 uppercase mb-1">Engagement Rate</p>
                                <div className="text-2xl font-bold">
                                    {p?.posts_count > 0 ? ((v?.liked_posts_count / p.posts_count).toFixed(1)) : '0.0'}
                                </div>
                                <p className="text-[10px] text-zinc-500">Likes per post</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Recent My Posts Performance */}
                <Card className="border-none bg-white dark:bg-zinc-900 shadow-sm rounded-3xl p-6">
                    <CardHeader className="px-0 pt-0">
                        <CardTitle className="text-lg">Recent Post Performance</CardTitle>
                        <p className="text-xs text-zinc-500">Top 5 latest contributions</p>
                    </CardHeader>
                    <CardContent className="px-0">
                        <div className="space-y-4">
                            {recentPosts.data?.posts.length > 0 ? (
                                recentPosts.data.posts.map((post: any) => (
                                    <div key={post.id} className="flex items-center justify-between p-3 rounded-2xl hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors">
                                        <div className="flex items-center space-x-3">
                                            <div className="h-12 w-12 rounded-lg bg-zinc-100 dark:bg-zinc-800 overflow-hidden">
                                                <img src={post.media_url} className="h-full w-full object-cover" alt="" />
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="text-sm font-bold truncate max-w-[150px]">{post.title || 'Untitled'}</span>
                                                <span className="text-[10px] text-zinc-500">{new Date(post.created_at).toLocaleDateString()}</span>
                                            </div>
                                        </div>
                                        <div className="flex space-x-4">
                                            <div className="flex flex-col items-center">
                                                <span className="text-xs font-bold">{post.likes}</span>
                                                <Heart className="h-3 w-3 text-rose-500" />
                                            </div>
                                            <div className="flex flex-col items-center">
                                                <span className="text-xs font-bold">{post.comments_count}</span>
                                                <MessageSquare className="h-3 w-3 text-primary" />
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="p-10 text-center text-zinc-500">
                                    <p className="text-sm">No posts to analyze yet.</p>
                                </div>
                            )}
                        </div>
                        <Button variant="ghost" className="w-full mt-4 text-xs font-bold text-zinc-400 group">
                            VIEW FULL REPORT
                            <ArrowUpRight className="ml-1 h-3 w-3 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition-transform" />
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
