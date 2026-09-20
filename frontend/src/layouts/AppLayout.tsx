import React, { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/common/Navbar';
import { Footer } from '../components/common/Footer';
import { AudioPlayerBar } from '../components/common/AudioPlayerBar';
import { useAuthStore } from '../stores/authStore';

export const AppLayout: React.FC = () => {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 pb-24">
        <Outlet />
      </main>
      <Footer />
      <AudioPlayerBar />
    </div>
  );
};
