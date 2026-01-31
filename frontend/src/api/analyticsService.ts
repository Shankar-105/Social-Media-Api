import api from './client';

export const analyticsService = {
    getVoteStats: async () => {
        const response = await api.get('/me/voteStats');
        return response.data;
    },
    getCommentStats: async () => {
        const response = await api.get('/me/comment-stats');
        return response.data;
    },
    getVotedPosts: async () => {
        const response = await api.get('/me/votedOnPosts');
        return response.data;
    },
    getCommentedPosts: async () => {
        const response = await api.get('/me/commented-on');
        return response.data;
    },
    getMyPosts: async (limit: number = 10, offset: number = 0) => {
        const response = await api.get('/me/posts', { params: { limit, offset } });
        return response.data;
    },
};
