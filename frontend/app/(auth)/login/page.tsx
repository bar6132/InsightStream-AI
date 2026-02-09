// "use client";

// import { useState } from "react";
// import { useAuth } from "@/app/context/AuthContext";
// import { useRouter } from "next/navigation";
// import axios from "axios";
// import { authService } from "@/services/auth.service";

// export default function LoginPage() {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const { login } = useAuth();
//   const router = useRouter();

// const handleSubmit = async (e: React.FormEvent) => {
//   e.preventDefault();
//   setError("");

//   try {
//     const data = await authService.login({ email, password });
    
//     // אנחנו יוצרים אובייקט משתמש מהשדות שה-Backend החזיר
//     const userData = {
//       id: data.user_id,
//       email: data.email,
//       role: data.role || 'user' // ברירת מחדל אם השרת לא שלח role
//     };

//     login(data.access_token, userData);
//     router.push("/");
//   } catch (err: unknown) {
//     // ... טיפול בשגיאות כפי שהיה
//   }
// };

//   return (
//     <div className="flex min-h-screen items-center justify-center bg-background p-4">
//       <div className="w-full max-w-md space-y-8 rounded-2xl bg-surface p-8 shadow-xl border border-gray-800">
//         <div className="text-center">
//           <h2 className="text-3xl font-bold text-primary">Welcome Back</h2>
//           <p className="mt-2 text-gray-400 text-sm">Sign in to InsightStream AI</p>
//         </div>

//         <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
//           <div className="space-y-4">
//             <div>
//               <label className="block text-sm font-medium text-gray-300">Email Address</label>
//               <input
//                 type="email"
//                 required
//                 className="mt-1 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition"
//                 placeholder="you@example.com"
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//               />
//             </div>
//             <div>
//               <label className="block text-sm font-medium text-gray-300">Password</label>
//               <input
//                 type="password"
//                 required
//                 className="mt-1 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition"
//                 placeholder="••••••••"
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//               />
//             </div>
//           </div>

//           {error && (
//             <div className="text-danger text-sm text-center bg-danger/10 p-2 rounded-lg">
//               {error}
//             </div>
//           )}

//           <button
//             type="submit"
//             className="w-full rounded-lg bg-primary p-3 font-semibold text-white hover:bg-blue-600 transition duration-300 shadow-lg shadow-primary/20"
//           >
//             Sign In
//           </button>
//         </form>
//       </div>
//     </div>
//   );
// }

"use client";

import { useState } from "react";
import { useAuth } from "@/app/context/AuthContext";
import { useRouter } from "next/navigation";
import axios from "axios";
import { authService } from "@/services/auth.service";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // הוספתי מצב טעינה לכפתור
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await authService.login({ email, password });
      
      // יצירת אובייקט משתמש תקין לפי ה-Interface ב-AuthContext
      const userData = {
        id: data.user_id,
        email: data.email,
        // המרה בטוחה לטיפוס Role
        role: (data.role === 'admin' ? 'admin' : 'user') as 'user' | 'admin'
      };

      login(data.access_token, userData);
      router.push("/"); // או '/dashboard'
      
    } catch (err: unknown) {
      // טיפול תקין בשגיאות ב-TypeScript
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "Login failed. Please check your credentials.");
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-surface p-8 shadow-xl border border-gray-800">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white">Welcome Back</h2>
          <p className="mt-2 text-gray-400 text-sm">Sign in to InsightStream AI</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300">Email Address</label>
              <input
                type="email"
                required
                className="mt-1 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300">Password</label>
              <input
                type="password"
                required
                className="mt-1 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-500/10 p-2 rounded-lg border border-red-500/20">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-primary p-3 font-semibold text-white hover:bg-blue-600 transition duration-300 shadow-lg shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}