import api from './client';

export const commentService = {
    getComments: async (postId: number, limit = 10, offset = 0) => {
        const response = await api.get(`/comments-on/${postId}`, {
            params: { limit, offset },
        });
        return response.data;
    },
    createComment: async (postId: number, content: string) => {
        const response = await api.post('/comment', {
            post_id: postId,
            content: content,
        });
        return response.data;
    },
    deleteComment: async (commentId: number) => {
        const response = await api.delete(`/comments/delete_comment/${commentId}`);
        return response.data;
    },
    editComment: async (commentId: number, content: string) => {
        const response = await api.patch(`/comments/edit_comment/${commentId}`, {
            comment_content: content,
        });
        return response.data;
    },
    likeComment: async (commentId: number) => {
        // Checking if backend supports comment liking in like.py
        const response = await api.post(`/comments/${commentId}/like`);
        return response.data;
    },
};
