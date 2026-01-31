import { type ReactNode } from 'react';
import Sidebar from './Sidebar';

export default function MainLayout({ children }: { children: ReactNode }) {
    return (
        <div className="flex min-h-screen bg-white dark:bg-zinc-950">
            {/* Sidebar for Desktop */}
            <aside className="fixed left-0 top-0 h-screen w-[72px] lg:w-[244px] z-50">
                <Sidebar />
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 ml-[72px] lg:ml-[244px] min-h-screen">
                <div className="max-w-[1013px] mx-auto w-full px-4 sm:px-8 py-4">
                    {children}
                </div>
            </main>

            {/* Mobile Feed Header (Top bar for small screens) - To be refined later */}
            <div className="lg:hidden fixed top-0 left-0 right-0 h-14 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 flex items-center px-4 z-40">
                <h1 className="text-xl font-bold font-serif italic">InstaClone</h1>
            </div>
        </div>
    );
}
