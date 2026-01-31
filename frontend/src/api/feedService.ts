import api from './client';

export const feedService = {
    getHomeFeed: async (limit = 10, offset = 0) => {
        const response = await api.get('/feed/home', {
            params: { limit, offset },
        });
        return response.data;
    },
    getPost: async (postId: number) => {
        const response = await api.get(`/posts/getPost/${postId}`);
        return response.data;
    },
};
