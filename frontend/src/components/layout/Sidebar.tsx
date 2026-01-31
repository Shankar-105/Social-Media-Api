import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    Home,
    Search,
    Compass,
    MessageCircle,
    Heart,
    PlusSquare,
    User,
    Menu,
    Instagram,
    Settings,
    TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';
import CreatePostModal from '@/components/common/CreatePostModal';
import { ThemeToggle } from '@/components/ThemeToggle';

const navItems = [
    { icon: Home, label: 'Home', path: '/' },
    { icon: Search, label: 'Search', path: '/search' },
    { icon: Compass, label: 'Explore', path: '/explore' },
    { icon: MessageCircle, label: 'Messages', path: '/messages' },
    { icon: Heart, label: 'Notifications', path: '/notifications' },
    { icon: TrendingUp, label: 'Insights', path: '/analytics' },
    { icon: PlusSquare, label: 'Create', path: '#', isButton: true },
    { icon: Settings, label: 'Settings', path: '/settings' },
];

export default function Sidebar() {
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const location = useLocation();
    const user = useAuthStore((state) => state.user);

    return (
        <div className="flex flex-col h-full border-r border-zinc-200 dark:border-zinc-800 px-3 py-5 bg-white dark:bg-zinc-950">
            <div className="px-3 mb-10">
                <Link to="/" className="hidden lg:block">
                    <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 font-serif italic">
                        InstaClone
                    </h1>
                </Link>
                <Link to="/" className="lg:hidden block">
                    <Instagram className="h-7 w-7" />
                </Link>
            </div>

            <nav className="flex-1 space-y-2">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <React.Fragment key={item.label}>
                            {item.isButton ? (
                                <button
                                    onClick={() => setIsCreateModalOpen(true)}
                                    className={cn(
                                        "flex items-center space-x-4 px-3 py-3 rounded-lg transition-colors group w-full text-left",
                                        "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                                    )}
                                >
                                    <item.icon className={cn("h-7 w-7 transition-transform group-hover:scale-110")} />
                                    <span className="hidden lg:block text-[16px]">{item.label}</span>
                                </button>
                            ) : (
                                <Link
                                    to={item.path}
                                    className={cn(
                                        "flex items-center space-x-4 px-3 py-3 rounded-lg transition-colors group",
                                        isActive
                                            ? "font-bold text-zinc-900 dark:text-zinc-50"
                                            : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                                    )}
                                >
                                    <item.icon className={cn("h-7 w-7 transition-transform group-hover:scale-110", isActive && "stroke-[2.5px]")} />
                                    <span className="hidden lg:block text-[16px]">{item.label}</span>
                                </Link>
                            )}
                        </React.Fragment>
                    );
                })}

                <Link
                    to={`/profile/${user?.id}`}
                    className={cn(
                        "flex items-center space-x-4 px-3 py-3 rounded-lg transition-colors group",
                        location.pathname.startsWith('/profile')
                            ? "font-bold text-zinc-900 dark:text-zinc-50"
                            : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                    )}
                >
                    <div className="h-7 w-7 rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden border border-zinc-200 dark:border-zinc-800">
                        <User className="h-full w-full p-1" />
                    </div>
                    <span className="hidden lg:block text-[16px]">Profile</span>
                </Link>
            </nav>

            <div className="mt-auto flex items-center justify-between px-3 py-3">
                <button className="flex items-center space-x-4 rounded-lg w-full text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors">
                    <Menu className="h-7 w-7" />
                    <span className="hidden lg:block text-[16px]">More</span>
                </button>
                <div className="hidden lg:block">
                    <ThemeToggle />
                </div>
            </div>

            <CreatePostModal
                open={isCreateModalOpen}
                onOpenChange={setIsCreateModalOpen}
            />
        </div>
    );
}
