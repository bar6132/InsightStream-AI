"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Loader2, AlertCircle, SlidersHorizontal, RefreshCw, Zap } from "lucide-react";
import { useAuth } from "@/app/context/AuthContext";
import { newsService, Article } from "@/services/news.service";
import { useRealtimeFeed } from "@/hooks/useRealtimeFeed";
import NewsCard from "@/components/NewsCard";
import PreferencesModal from "@/components/PreferencesModal";

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [articles, setArticles] = useState<Article[]>([]);
  const [feedLoading, setFeedLoading] = useState(true);
  const [error, setError] = useState("");
  const [isPrefsOpen, setIsPrefsOpen] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [triggerMessage, setTriggerMessage] = useState("");

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const fetchFeed = useCallback(async () => {
    setFeedLoading(true);
    setError("");
    try {
      const data = await newsService.getMyFeed();
      setArticles(data.feed);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load your feed.";
      setError(message);
    } finally {
      setFeedLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchFeed();
    }
  }, [user, fetchFeed]);

  // Live realtime: prepend new articles as they arrive from the worker
  useRealtimeFeed(
    useCallback((newArticle: Article) => {
      setArticles((prev) => {
        // Avoid duplicates if the article is already in the feed
        if (prev.some((a) => a.id === newArticle.id)) return prev;
        return [newArticle, ...prev];
      });
    }, [])
  );

  const handleTriggerIngestion = async () => {
    setTriggering(true);
    setTriggerMessage("");
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/trigger-ingestion", {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      const data = await res.json();
      setTriggerMessage(data.status ?? "Job queued!");
    } catch {
      setTriggerMessage("Failed to trigger ingestion.");
    } finally {
      setTriggering(false);
      setTimeout(() => setTriggerMessage(""), 5000);
    }
  };

  // Show full-screen loader while auth or first feed fetch is in progress
  if (authLoading || (feedLoading && articles.length === 0)) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-4 py-10 md:px-8">
      <div className="mx-auto max-w-7xl">

        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Your Insight <span className="text-primary">Stream</span>
            </h1>
            <p className="mt-1 text-gray-400">
              Personalized intelligence based on your interests.
              {articles.length > 0 && (
                <span className="ml-2 text-gray-500">
                  ({articles.length} articles)
                </span>
              )}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Trigger ingestion — queues a scrape job via RabbitMQ */}
            <button
              onClick={handleTriggerIngestion}
              disabled={triggering}
              className="flex items-center gap-2 rounded-lg border border-primary/40 bg-primary/10 px-4 py-2 text-sm font-medium text-primary hover:bg-primary/20 disabled:opacity-50 transition"
            >
              {triggering ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Zap className="h-4 w-4" />
              )}
              {triggering ? "Queuing..." : "Fetch News"}
            </button>

            {/* Refresh current feed from backend */}
            <button
              onClick={fetchFeed}
              disabled={feedLoading}
              className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white disabled:opacity-50 transition"
            >
              <RefreshCw className={`h-4 w-4 ${feedLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>

            {/* Preferences */}
            <button
              onClick={() => setIsPrefsOpen(true)}
              className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition"
            >
              <SlidersHorizontal className="h-4 w-4" />
              Customize
            </button>
          </div>
        </div>

        {/* Trigger status message */}
        {triggerMessage && (
          <div className="mb-6 rounded-lg border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-primary">
            {triggerMessage} New articles will appear automatically.
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-red-400">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Articles grid */}
        {articles.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        ) : (
          !error && (
            <div className="flex flex-col items-center justify-center py-32 text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-900">
                <Zap className="h-8 w-8 text-gray-700" />
              </div>
              <h3 className="text-xl font-medium text-gray-300">No articles yet</h3>
              <p className="mt-2 text-gray-500">
                Click <span className="text-primary font-medium">Fetch News</span> to start the ingestion pipeline,
                <br />
                or set your interests first via <span className="text-primary font-medium">Customize</span>.
              </p>
            </div>
          )
        )}
      </div>

      {/* Preferences modal */}
      <PreferencesModal
        isOpen={isPrefsOpen}
        onClose={() => setIsPrefsOpen(false)}
        onSave={fetchFeed}
      />
    </div>
  );
}
