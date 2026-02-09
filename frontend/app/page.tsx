import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 text-center">
      <div className="space-y-6 max-w-3xl">
        <div className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary border border-primary/20">
          The Future of News Consumption 🚀
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-gradient-to-b from-white to-gray-500 bg-clip-text text-transparent pb-2">
          Welcome to <br />
          InsightStream AI
        </h1>
        
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Your personalized, AI-powered news aggregator. We analyze thousands of articles to bring you only what truly matters.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <Link 
            href="/signup"
            className="rounded-lg bg-primary px-8 py-3 font-semibold text-white hover:bg-blue-600 transition shadow-lg shadow-primary/25"
          >
            Get Started Free
          </Link>
          <Link 
            href="/login"
            className="rounded-lg border border-gray-700 bg-surface px-8 py-3 font-semibold text-gray-300 hover:bg-gray-800 transition"
          >
            Sign In
          </Link>
        </div>
      </div>
    </main>
  );
}