/* eslint-disable react-hooks/set-state-in-effect */
// "use client";

// import Link from "next/link";
// import { useAuth } from "@/app/context/AuthContext";
// import { usePathname } from "next/navigation";
// import { Shield, LayoutDashboard, LogOut, User as UserIcon } from "lucide-react";

// export default function Navbar() {
//   const { user, logout, loading } = useAuth();
//   const pathname = usePathname();

//   if (loading) return (
//     <nav className="h-16 border-b border-gray-800 bg-background/80" />
//   );

//   const isActive = (path: string) => pathname === path ? "text-primary" : "text-gray-300 hover:text-white";

//   return (
//     <nav className="sticky top-0 z-50 w-full border-b border-gray-800 bg-background/95 backdrop-blur-md">
//       <div className="container mx-auto flex h-16 items-center justify-between px-4">
        
//         {/* Logo */}
//         <Link href="/" className="flex items-center space-x-2">
//           <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
//             <span className="text-white font-bold text-sm">IS</span>
//           </div>
//           <span className="text-xl font-bold tracking-tight text-white hidden sm:block">
//             InsightStream
//           </span>
//         </Link>

//         {/* Action Links */}
//         <div className="flex items-center gap-6">
//           {!user ? (
//             <div className="flex items-center gap-4">
//               <Link href="/login" className="text-sm font-medium text-gray-300 hover:text-white transition">
//                 Sign In
//               </Link>
//               <Link
//                 href="/signup"
//                 className="rounded-full bg-white px-5 py-2 text-sm font-bold text-black hover:bg-gray-200 transition"
//               >
//                 Get Started
//               </Link>
//             </div>
//           ) : (
//             <div className="flex items-center gap-6">
//               {/* Dashboard Link (Always for logged in users) */}
//               <Link href="/dashboard" className={`flex items-center gap-2 text-sm font-medium transition ${isActive("/dashboard")}`}>
//                 <LayoutDashboard className="h-4 w-4" />
//                 <span className="hidden md:inline">Feed</span>
//               </Link>

//               {/* Admin Panel (Only for admins) */}
//               {user.role === 'admin' && (
//                 <Link href="/admin" className={`flex items-center gap-2 text-sm font-medium transition ${isActive("/admin")}`}>
//                   <Shield className="h-4 w-4 text-secondary" />
//                   <span className="text-secondary hidden md:inline">Admin</span>
//                 </Link>
//               )}

//               {/* User Dropdown / Profile Area */}
//               <div className="flex items-center gap-3 pl-4 border-l border-gray-800">
//                 <div className="flex flex-col items-end">
//                   <span className="text-xs font-bold text-white leading-none">
//                     {user.email.split('@')[0]}
//                   </span>
//                   <span className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
//                     {user.role}
//                   </span>
//                 </div>
//                 <button
//                   onClick={logout}
//                   className="p-2 rounded-lg bg-gray-900 text-gray-400 hover:text-danger hover:bg-danger/10 transition"
//                   title="Logout"
//                 >
//                   <LogOut className="h-4 w-4" />
//                 </button>
//               </div>
//             </div>
//           )}
//         </div>
//       </div>
//     </nav>
//   );
// }
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/app/context/AuthContext";
import { usePathname } from "next/navigation";

import { Shield, LayoutDashboard, LogOut } from "lucide-react";

export default function Navbar() {
  const { user, loading, logout  } = useAuth();
  const pathname = usePathname();
  
  // שימוש ב-State כדי לוודא שאנחנו בצד הלקוח
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const isActive = (path: string) => 
    pathname === path ? "text-primary" : "text-gray-300 hover:text-white";

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-gray-800 bg-background/95 backdrop-blur-md">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <span className="text-white font-bold text-sm">IS</span>
          </div>
          <span className="text-xl font-bold tracking-tight text-white hidden sm:block">
            InsightStream
          </span>
        </Link>

        {/* Action Links */}
        <div className="flex items-center gap-6">
          {/* כאן הלב של התיקון: 
             אם אנחנו עדיין בשרת (isClient = false) או בטעינה, 
             נציג מצב נייטרלי או ריק שלא מתנגש עם ה-Auth.
          */}
          {!isClient || loading ? (
            <div className="h-8 w-20 bg-gray-800 animate-pulse rounded-full" />
          ) : !user ? (
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-sm font-medium text-gray-300 hover:text-white transition">
                Sign In
              </Link>
              <Link
                href="/signup"
                className="rounded-full bg-white px-5 py-2 text-sm font-bold text-black hover:bg-gray-200 transition"
              >
                Get Started
              </Link>
            </div>
          ) : (
            <div className="flex items-center gap-6">
              <Link href="/dashboard" className={`flex items-center gap-2 text-sm font-medium transition ${isActive("/dashboard")}`}>
                <LayoutDashboard className="h-4 w-4" />
                <span className="hidden md:inline">Feed</span>
              </Link>

              {user.role === 'admin' && (
                <Link href="/admin" className={`flex items-center gap-2 text-sm font-medium transition ${isActive("/admin")}`}>
                  <Shield className="h-4 w-4 text-secondary" />
                  <span className="text-secondary hidden md:inline">Admin</span>
                </Link>
              )}

              <div className="flex items-center gap-3 pl-4 border-l border-gray-800">
                <div className="flex flex-col items-end">
                  <span className="text-xs font-bold text-white leading-none">
                    {user.email.split('@')[0]}
                  </span>
                  <span className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg bg-gray-900 text-gray-400 hover:text-danger hover:bg-danger/10 transition"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}