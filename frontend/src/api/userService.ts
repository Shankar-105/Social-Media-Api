import api from './client';

export const userService = {
    getProfile: async (userId: string | number) => {
        const response = await api.get(`/users/${userId}/profile`);
        return response.data;
    },
    getUserPosts: async (userId: string | number) => {
        const response = await api.get(`/users/${userId}/posts`);
        return response.data;
    },
    getMyProfile: async () => {
        const response = await api.get('/me/profile');
        return response.data;
    },
    updateProfile: async (data: FormData) => {
        const response = await api.patch('/me/updateInfo', data, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
};
