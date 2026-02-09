// "use client";

// import { useEffect, useState } from "react";
// import { useAuth } from "@/app/context/AuthContext";
// import { useRouter } from "next/navigation";
// import { Loader2, AlertCircle } from "lucide-react";
// // ייבוא ה-Service והטיפוסים שהגדרנו בו
// import { newsService, Article } from "@/services/news.service"; 
// import NewsCard from "@/components/NewsCard";
// import axios from "axios";

// export default function Dashboard() {
//   const { user, loading: authLoading } = useAuth();
//   // כאן אנחנו מגדירים שהסטייט הוא מערך של Article (במקום any)
//   const [articles, setArticles] = useState<Article[]>([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");
//   const router = useRouter();

//   useEffect(() => {
//     if (!authLoading && !user) {
//       router.push("/login");
//       return;
//     }

//     const fetchFeed = async () => {
//       try {
//         // נוודא שהתגיות קיימות, אם לא נשתמש בברירת מחדל
//         const tags = ["Tech", "AI", "Apple"]; 
        
//         // שימוש ב-Service החדש
//         const data = await newsService.getMyFeed(tags);
        
//         setArticles(data.feed);
//       } catch (err: unknown) {
//         if (axios.isAxiosError(err)) {
//           setError(err.response?.data?.detail || "Failed to load feed.");
//         } else {
//           setError("An unexpected error occurred.");
//         }
//       } finally {
//         setLoading(false);
//       }
//     };

//     if (user) {
//       fetchFeed();
//     }
//   }, [user, authLoading, router]);

//   if (authLoading || loading) {
//     return (
//       <div className="flex h-[80vh] items-center justify-center">
//         <Loader2 className="h-10 w-10 animate-spin text-primary" />
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-background px-4 py-12 md:px-8">
//       <div className="mx-auto max-w-7xl">
//         <header className="mb-12">
//           <h1 className="text-4xl font-bold text-white tracking-tight">
//             Your Insight <span className="text-primary">Stream</span>
//           </h1>
//           <p className="mt-2 text-gray-400 text-lg">
//             Personalized intelligence for your selected interests.
//           </p>
//         </header>

//         {error ? (
//           <div className="flex items-center gap-3 rounded-xl bg-danger/10 p-4 text-danger border border-danger/20">
//             <AlertCircle className="h-5 w-5" />
//             <p>{error}</p>
//           </div>
//         ) : (
//           <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
//             {articles.map((article) => (
//               <NewsCard key={article.id} article={article} />
//             ))}
//           </div>
//         )}
        
//         {!loading && articles.length === 0 && !error && (
//           <div className="flex flex-col items-center justify-center py-24 text-center">
//             <div className="h-16 w-16 rounded-full bg-gray-900 flex items-center justify-center mb-4">
//                <Loader2 className="h-8 w-8 text-gray-700" />
//             </div>
//             <h3 className="text-xl font-medium text-gray-300">No articles found</h3>
//             <p className="text-gray-500 mt-2">Try updating your interest tags in your profile.</p>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }
"use client";

import { useEffect, useState } from "react";
import { SlidersHorizontal } from "lucide-react"; // אייקון של הגדרות
import PreferencesModal from "@/components/PreferencesModal";
// ... ייבואים אחרים

export default function Dashboard() {
  const [isPrefsOpen, setIsPrefsOpen] = useState(false);
  // ... שאר ה-State שלך (articles, etc)

  // פונקציה לרענון הפיד (תעביר אותה למודאל כדי שיקרא לה אחרי שמירה)
  const refreshFeed = () => {
    // כאן תהיה הקריאה ל-fetchFeed שכבר כתבת או נכתוב בהמשך
    console.log("Refreshing feed...");
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-6xl">
        
        {/* Header Area */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Your Insight Stream</h1>
            <p className="text-gray-400">Personalized intelligence based on your interests.</p>
          </div>
          
          {/* כפתור עריכת העדפות */}
          <button
            onClick={() => setIsPrefsOpen(true)}
            className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition"
          >
            <SlidersHorizontal className="h-4 w-4" />
            Customize Feed
          </button>
        </div>

        {/* כאן יבוא ה-Grid של החדשות בהמשך... */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* News Cards... */}
        </div>

        {/* המודאל מחוץ לזרימה הרגילה */}
        <PreferencesModal 
            isOpen={isPrefsOpen} 
            onClose={() => setIsPrefsOpen(false)} 
            onSave={refreshFeed} 
        />
      </div>
    </div>
  );
}