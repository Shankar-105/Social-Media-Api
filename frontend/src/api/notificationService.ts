import api from './client';

export const notificationService = {
    getNotifications: async () => {
        const response = await api.get('/notifications');
        return response.data;
    },
    markAsRead: async (notificationId: number) => {
        const response = await api.patch(`/notifications/${notificationId}/read`);
        return response.data;
    },
};
