import { type ReactNode } from 'react';

export default function AuthLayout({ children }: { children: ReactNode }) {
    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 dark:bg-zinc-950 p-4">
            <div className="w-full max-w-[400px] space-y-8">
                <div className="flex flex-col items-center justify-center space-y-2">
                    <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 font-serif italic">
                        InstaClone
                    </h1>
                    <p className="text-zinc-500 dark:text-zinc-400 text-sm">
                        Experience the next generation of social
                    </p>
                </div>
                {children}
            </div>
        </div>
    );
}
