import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { authService } from '@/api/authService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Shield, Key, Mail, Loader2, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Settings() {
    const [activeTab, setActiveTab] = useState<'password' | 'privacy' | 'account'>('password');
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [otp, setOtp] = useState('');
    const [step, setStep] = useState<1 | 2>(1);
    const [success, setSuccess] = useState(false);

    const otpMutation = useMutation({
        mutationFn: () => authService.requestPasswordOTP(),
        onSuccess: () => {
            setStep(2);
        },
    });

    const resetMutation = useMutation({
        mutationFn: () => authService.resetPassword({
            old_password: oldPassword,
            new_password: newPassword,
            otp: otp
        }),
        onSuccess: () => {
            setSuccess(true);
            setOldPassword('');
            setNewPassword('');
            setOtp('');
        },
    });

    const tabs = [
        { id: 'password', label: 'Security', icon: Shield },
        { id: 'privacy', label: 'Privacy', icon: Key },
        { id: 'account', label: 'Account', icon: Mail },
    ];

    return (
        <div className="max-w-4xl mx-auto p-4 md:p-8 flex flex-col md:flex-row gap-8">
            <div className="w-full md:w-64 space-y-1">
                <h1 className="text-2xl font-bold mb-6 px-4">Settings</h1>
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={cn(
                            "w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all group",
                            activeTab === tab.id
                                ? "bg-primary text-white shadow-lg shadow-primary/20"
                                : "text-zinc-500 hover:bg-zinc-50 dark:hover:bg-zinc-900"
                        )}
                    >
                        <tab.icon className={cn("h-5 w-5", activeTab === tab.id ? "text-white" : "text-zinc-400 group-hover:text-zinc-600")} />
                        <span>{tab.label}</span>
                    </button>
                ))}
            </div>

            <div className="flex-1 bg-white dark:bg-zinc-950 border border-zinc-100 dark:border-zinc-800 rounded-3xl p-6 md:p-10 shadow-sm">
                {activeTab === 'password' && (
                    <div className="space-y-8 animate-in fade-in duration-500">
                        <div>
                            <h2 className="text-xl font-bold">Security Settings</h2>
                            <p className="text-sm text-zinc-500 mt-1">Manage your password and security preferences.</p>
                        </div>

                        {success ? (
                            <div className="flex flex-col items-center justify-center py-10 space-y-4 text-center">
                                <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-full">
                                    <CheckCircle2 className="h-12 w-12 text-green-500" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold">Password Updated</h3>
                                    <p className="text-sm text-zinc-500">Your security is our priority. Next time, use your new password.</p>
                                </div>
                                <Button onClick={() => setSuccess(false)}>Back to Security</Button>
                            </div>
                        ) : (
                            <div className="space-y-6 max-w-md">
                                {step === 1 ? (
                                    <>
                                        <div className="space-y-2">
                                            <Label htmlFor="old">Current Password</Label>
                                            <Input
                                                id="old"
                                                type="password"
                                                value={oldPassword}
                                                onChange={(e) => setOldPassword(e.target.value)}
                                                className="bg-zinc-50 dark:bg-zinc-900 border-none h-12"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="new">New Password</Label>
                                            <Input
                                                id="new"
                                                type="password"
                                                value={newPassword}
                                                onChange={(e) => setNewPassword(e.target.value)}
                                                className="bg-zinc-50 dark:bg-zinc-900 border-none h-12"
                                            />
                                        </div>
                                        <Button
                                            onClick={() => otpMutation.mutate()}
                                            className="w-full h-12 font-bold"
                                            disabled={!oldPassword || !newPassword || otpMutation.isPending}
                                        >
                                            {otpMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                                            Send Verification Code
                                        </Button>
                                    </>
                                ) : (
                                    <>
                                        <div className="p-4 bg-primary/5 border border-primary/10 rounded-2xl flex items-center space-x-3 mb-4">
                                            <Mail className="h-5 w-5 text-primary" />
                                            <p className="text-xs font-medium text-primary">Verification code sent to your registered email.</p>
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="otp">Enter 6-digit Code</Label>
                                            <Input
                                                id="otp"
                                                placeholder="000000"
                                                maxLength={6}
                                                value={otp}
                                                onChange={(e) => setOtp(e.target.value)}
                                                className="bg-zinc-50 dark:bg-zinc-900 border-none h-14 text-center text-2xl font-mono tracking-widest"
                                            />
                                        </div>
                                        <div className="flex space-x-3">
                                            <Button variant="ghost" className="flex-1" onClick={() => setStep(1)}>Back</Button>
                                            <Button
                                                className="flex-2"
                                                onClick={() => resetMutation.mutate()}
                                                disabled={otp.length !== 6 || resetMutation.isPending}
                                            >
                                                {resetMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                                                Update Password
                                            </Button>
                                        </div>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                )}
                {activeTab !== 'password' && (
                    <div className="flex flex-col items-center justify-center p-20 text-zinc-400">
                        <Loader2 className="h-8 w-8 animate-spin mb-4" />
                        <p>Under construction...</p>
                    </div>
                )}
            </div>
        </div>
    );
}
