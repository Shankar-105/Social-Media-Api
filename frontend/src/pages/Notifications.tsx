import { useQuery } from '@tanstack/react-query';
import { notificationService } from '@/api/notificationService';
import { Loader2, Heart, MessageCircle, UserPlus } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function Notifications() {
    const { data: notifications, isLoading, error } = useQuery({
        queryKey: ['notifications'],
        queryFn: notificationService.getNotifications,
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
                Failed to load notifications.
            </div>
        );
    }

    const notifs = notifications || [];

    const getIcon = (type: string) => {
        switch (type) {
            case 'like':
                return <Heart className="h-5 w-5 text-red-500 fill-red-500" />;
            case 'comment':
                return <MessageCircle className="h-5 w-5 text-blue-500" />;
            case 'follow':
                return <UserPlus className="h-5 w-5 text-green-500" />;
            default:
                return <Heart className="h-5 w-5" />;
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-4 p-4">
            <h2 className="text-2xl font-bold">Notifications</h2>

            {notifs.length > 0 ? (
                <div className="space-y-2">
                    {notifs.map((notif: any) => (
                        <div key={notif.id} className="flex items-center space-x-4 p-3 hover:bg-zinc-50 dark:hover:bg-zinc-900 rounded-lg transition-colors">
                            <Avatar className="h-12 w-12">
                                <AvatarImage src={notif.user?.profile_picture} alt={notif.user?.username} />
                                <AvatarFallback>{notif.user?.username?.[0]?.toUpperCase()}</AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                                <p className="text-sm">
                                    <span className="font-semibold">{notif.user?.username}</span>{' '}
                                    <span className="text-zinc-600 dark:text-zinc-400">{notif.message}</span>
                                </p>
                                <p className="text-xs text-zinc-400">
                                    {formatDistanceToNow(new Date(notif.created_at))} ago
                                </p>
                            </div>
                            <div>{getIcon(notif.type)}</div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center p-20 text-zinc-500">
                    <Heart className="h-16 w-16 mx-auto mb-4 text-zinc-300" />
                    <p className="text-lg font-semibold">No notifications yet</p>
                    <p className="text-sm">When someone likes or comments on your posts, you'll see it here.</p>
                </div>
            )}
        </div>
    );
}
