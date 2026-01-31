import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/components/ThemeProvider';
import Login from '@/pages/auth/Login';
import Signup from '@/pages/auth/Signup';
import Feed from '@/pages/Feed';
import Profile from '@/pages/Profile';
import Messages from '@/pages/Messages';
import Search from '@/pages/Search';
import Explore from '@/pages/Explore';
import Notifications from '@/pages/Notifications';
import Settings from '@/pages/Settings';
import Analytics from '@/pages/Analytics';
import MainLayout from '@/components/layout/MainLayout';
import { useAuthStore } from '@/store/authStore';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <ThemeProvider defaultTheme="dark" storageKey="instaclone-theme">
      <Router>
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
          <Route path="/signup" element={!isAuthenticated ? <Signup /> : <Navigate to="/" />} />
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Feed />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/profile/:userId"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Profile />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/messages"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Messages />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/search"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Search />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/explore"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Explore />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/notifications"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Notifications />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/settings"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Settings />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/analytics"
            element={
              isAuthenticated ? (
                <MainLayout>
                  <Analytics />
                </MainLayout>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
