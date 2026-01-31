import api from './client';

export const socialService = {
    likePost: async (postId: number, choice: boolean = true) => {
        const response = await api.post('/vote/on_post', {
            post_id: postId,
            choice: choice,
        });
        return response.data;
    },
    followUser: async (userId: number) => {
        const response = await api.post(`/follow/${userId}`);
        return response.data;
    },
    unfollowUser: async (userId: number) => {
        const response = await api.delete(`/unfollow/${userId}`);
        return response.data;
    },
    removeFollower: async (userId: number) => {
        const response = await api.delete(`/remove_follower/${userId}`);
        return response.data;
    },
    likeComment: async (commentId: number, choice: boolean = true) => {
        const response = await api.post('/vote/on_comment', {
            comment_id: commentId,
            choice: choice,
        });
        return response.data;
    },
    getFollowers: async (userId: number) => {
        const response = await api.get(`/users/${userId}/followers`);
        return response.data;
    },
    getFollowing: async (userId: number) => {
        const response = await api.get(`/users/${userId}/following`);
        return response.data;
    },
    sharePost: async (postId: number, receiverId: number) => {
        const response = await api.post('/share', {
            post_id: postId,
            to_user_id: receiverId
        });
        return response.data;
    }
};
