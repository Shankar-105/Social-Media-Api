import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import AuthLayout from '@/components/layout/AuthLayout';
import api from '@/api/client';
import { Loader2 } from 'lucide-react';

const signupSchema = z.object({
    username: z.string().min(3, 'Username must be at least 3 characters'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    email: z.string().email('Invalid email address').optional().or(z.literal('')),
    nickname: z.string().optional(),
});

type SignupValues = z.infer<typeof signupSchema>;

export default function Signup() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const form = useForm<SignupValues>({
        resolver: zodResolver(signupSchema),
        defaultValues: {
            username: '',
            password: '',
            nickname: '',
            email: '',
        },
    });

    async function onSubmit(values: SignupValues) {
        setIsLoading(true);
        setError(null);
        try {
            await api.post('/user/signup', values);
            navigate('/login');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Something went wrong during registration');
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <AuthLayout>
            <Card className="border-zinc-200 dark:border-zinc-800 shadow-xl">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl text-center">Create an account</CardTitle>
                    <CardDescription className="text-center">
                        Sign up to see photos and videos from your friends
                    </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4">
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="username"
                                render={({ field }: { field: any }) => (
                                    <FormItem>
                                        <FormLabel>Username</FormLabel>
                                        <FormControl>
                                            <Input placeholder="johndoe" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }: { field: any }) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input type="password" placeholder="••••••••" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="email"
                                render={({ field }: { field: any }) => (
                                    <FormItem>
                                        <FormLabel>Email (for password reset)</FormLabel>
                                        <FormControl>
                                            <Input type="email" placeholder="john@example.com" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                        <p className="text-xs text-zinc-500">Optional - used for password recovery</p>
                                    </FormItem>
                                )}
                            />
                            {error && <p className="text-sm text-destructive text-center">{error}</p>}
                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Create Account
                            </Button>
                        </form>
                    </Form>
                </CardContent>
                <CardFooter className="flex flex-col space-y-2">
                    <div className="text-sm text-center text-zinc-500 dark:text-zinc-400">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary hover:underline font-semibold">
                            Login
                        </Link>
                    </div>
                </CardFooter>
            </Card>
        </AuthLayout>
    );
}
