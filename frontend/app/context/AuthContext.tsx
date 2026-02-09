// "use client";

// import React, { createContext, useContext, useState, useEffect } from 'react';

// interface User {
//   id: string;
//   email: string;
//   role: 'user' | 'admin';
// }

// interface AuthContextType {
//   user: User | null;
//   loading: boolean;
//   login: (token: string, userData: User) => void;
//   logout: () => void;
// }

// const AuthContext = createContext<AuthContextType | undefined>(undefined);

// // פונקציית עזר לבדיקה האם אנחנו בדפדפן (מניעת שגיאות SSR)
// const isBrowser = typeof window !== 'undefined';

// export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
//   // 1. אתחול המשתמש ישירות מה-localStorage
//   const [user, setUser] = useState<User | null>(() => {
//     if (isBrowser) {
//       const savedUser = localStorage.getItem('user');
//       try {
//         return savedUser ? JSON.parse(savedUser) : null;
//       } catch {
//         return null;
//       }
//     }
//     return null;
//   });

//   // 2. אתחול ה-Loading כ-false אם כבר בדקנו את ה-localStorage
//   // ב-Next.js App Router, הטעינה הראשונית תמיד מסתיימת ברגע שה-Client Component עולה
//   const [loading, setLoading] = useState(false);

// const login = (token: string, userData: User) => {
//   localStorage.setItem('token', token);
//   localStorage.setItem('user', JSON.stringify(userData));
//   setUser(userData); // השורה הזו גורמת ל-Navbar לרנדר מחדש
// };

//   const logout = () => {
//     localStorage.removeItem('token');
//     localStorage.removeItem('user');
//     setUser(null);
//     window.location.href = '/login';
//   };

//   return (
//     <AuthContext.Provider value={{ user, loading, login, logout }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };

// export const useAuth = () => {
//   const context = useContext(AuthContext);
//   if (context === undefined) {
//     throw new Error('useAuth must be used within an AuthProvider');
//   }
//   return context;
// };

"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from "next/navigation";

// הגדרת המבנה של המשתמש
export interface User {
  id: string;
  email: string;
  role: 'user' | 'admin';
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // 1. התחלה תמיד ב-null כדי להתאים לשרת (מונע שגיאות Hydration)
  const [user, setUser] = useState<User | null>(null);
  
  // 2. Loading מתחיל ב-true כדי שלא נציג UI שגוי בזמן הבדיקה
  const [loading, setLoading] = useState(true);
  
  const router = useRouter();

  // 3. בדיקת localStorage מתבצעת רק בצד הלקוח (Client Side)
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedUser = localStorage.getItem('user');
        const storedToken = localStorage.getItem('token');

        if (storedUser && storedToken) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error("Failed to parse user from storage:", error);
        // במקרה של שגיאה בפרסור, מנקים את הזבל
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      } finally {
        setLoading(false); // סיימנו לבדוק
      }
    };

    initAuth();
  }, []);

  const login = (token: string, userData: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};