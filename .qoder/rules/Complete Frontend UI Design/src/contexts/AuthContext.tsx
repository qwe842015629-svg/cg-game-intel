import React, { createContext, useContext, useState, ReactNode } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  phone?: string;
  joinDate: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    // Mock login
    const mockUser: User = {
      id: '1',
      name: '游戏玩家',
      email,
      avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200',
      phone: '138****8888',
      joinDate: '2024-01-01',
    };
    setUser(mockUser);
  };

  const register = async (name: string, email: string, password: string) => {
    // Mock register
    const mockUser: User = {
      id: '1',
      name,
      email,
      joinDate: new Date().toISOString().split('T')[0],
    };
    setUser(mockUser);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
