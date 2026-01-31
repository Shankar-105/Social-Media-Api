import api from './client';

export const authService = {
    requestPasswordOTP: async () => {
        const response = await api.post('/change-password');
        return response.data;
    },
    resetPassword: async (data: any) => {
        const response = await api.post('/reset-password', data);
        return response.data;
    },
};
