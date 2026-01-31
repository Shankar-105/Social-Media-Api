import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { ImagePlus, Loader2, X } from 'lucide-react';
import api from '@/api/client';
import { useMutation, useQueryClient } from '@tanstack/react-query';

const postSchema = z.object({
    title: z.string().min(1, 'Title is required'),
    content: z.string().min(1, 'Caption is required'),
});

type PostValues = z.infer<typeof postSchema>;

interface CreatePostModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export default function CreatePostModal({ open, onOpenChange }: CreatePostModalProps) {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const queryClient = useQueryClient();

    const form = useForm<PostValues>({
        resolver: zodResolver(postSchema),
        defaultValues: {
            title: '',
            content: '',
        },
    });

    const mutation = useMutation({
        mutationFn: async (values: PostValues) => {
            const formData = new FormData();
            formData.append('title', values.title);
            formData.append('content', values.content);
            if (file) {
                formData.append('media', file);
            }
            return api.post('/posts/createPost', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['homeFeed'] });
            onOpenChange(false);
            form.reset();
            setFile(null);
            setPreview(null);
        },
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
        }
    };

    const removeFile = () => {
        setFile(null);
        setPreview(null);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] p-0 overflow-hidden">
                <DialogHeader className="p-4 border-b flex flex-row items-center justify-between">
                    <DialogTitle className="text-center w-full">Create new post</DialogTitle>
                </DialogHeader>

                <div className="p-6 space-y-6">
                    {!preview ? (
                        <div className="flex flex-col items-center justify-center border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl p-12 space-y-4">
                            <ImagePlus className="h-12 w-12 text-zinc-400" />
                            <div className="text-center">
                                <p className="font-semibold">Drag photos and videos here</p>
                                <p className="text-sm text-zinc-500">Or select from computer</p>
                            </div>
                            <Button variant="secondary" onClick={() => document.getElementById('file-upload')?.click()}>
                                Select from computer
                            </Button>
                            <input
                                id="file-upload"
                                type="file"
                                className="hidden"
                                accept="image/*,video/*"
                                onChange={handleFileChange}
                            />
                        </div>
                    ) : (
                        <div className="relative aspect-square rounded-lg overflow-hidden border">
                            {file?.type.startsWith('video') ? (
                                <video src={preview} className="h-full w-full object-cover" />
                            ) : (
                                <img src={preview} alt="Preview" className="h-full w-full object-cover" />
                            )}
                            <Button
                                variant="destructive"
                                size="icon"
                                className="absolute top-2 right-2 h-8 w-8 rounded-full"
                                onClick={removeFile}
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    )}

                    <Form {...form}>
                        <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="title"
                                render={({ field }: { field: any }) => (
                                    <FormItem>
                                        <FormLabel>Title</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Post title..." {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="content"
                                render={({ field }: { field: any }) => (
                                    <FormItem>
                                        <FormLabel>Caption</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Write a caption..." {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <DialogFooter className="pt-4">
                                <Button
                                    type="submit"
                                    className="w-full"
                                    disabled={mutation.isPending || !file}
                                >
                                    {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    Share
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                </div>
            </DialogContent>
        </Dialog>
    );
}
