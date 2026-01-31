import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';

interface UnfollowModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    user: {
        username: string;
        profile_pic?: string | null;
    };
    isLoading?: boolean;
}

export default function UnfollowModal({
    isOpen,
    onClose,
    onConfirm,
    user,
    isLoading = false,
}: UnfollowModalProps) {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[400px] flex flex-col items-center justify-center text-center p-8 gap-6 [&>button]:hidden">
                <Avatar className="h-24 w-24">
                    <AvatarImage src={user.profile_pic || undefined} />
                    <AvatarFallback className="text-2xl">{user.username[0]?.toUpperCase()}</AvatarFallback>
                </Avatar>

                <DialogHeader className="space-y-2">
                    <DialogTitle className="text-xl font-normal">
                        Unfollow @{user.username}?
                    </DialogTitle>
                    <DialogDescription className="text-center">
                        If you change your mind, you'll have to request to follow @{user.username} again.
                    </DialogDescription>
                </DialogHeader>

                <div className="flex flex-col w-full gap-3 pt-2">
                    <Button
                        variant="ghost"
                        className="w-full text-red-500 font-bold hover:text-red-600 hover:bg-transparent text-sm h-auto py-3 border-t border-b rounded-none border-border/40"
                        onClick={onConfirm}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Unfollowing...' : 'Unfollow'}
                    </Button>
                    <Button
                        variant="ghost"
                        className="w-full font-normal hover:bg-transparent text-sm h-auto py-1"
                        onClick={onClose}
                    >
                        Cancel
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
