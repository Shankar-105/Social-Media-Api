import api from './client';

export interface SearchParams {
    q: string;
    limit?: number;
    offset?: number;
    orderBy?: 'likes' | 'created_at';
}

export const searchService = {
    search: async (params: SearchParams) => {
        const response = await api.get('/search', { params });
        return response.data;
    },
    getExplorePosts: async (limit: number = 20, offset: number = 0) => {
        const response = await api.get('/feed/explore', {
            params: { limit, offset }
        });
        return response.data;
    },
};
