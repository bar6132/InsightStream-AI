"use client";

import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export type Article = {
  id: string;
  title: string;
  url: string;
  summary: string;
  source: string;
  published_at: string;
};

/**
 * Subscribes to Supabase Realtime INSERT events on the news_articles table.
 * Calls onNewArticle whenever a new row is saved by the worker.
 */
export function useRealtimeFeed(onNewArticle: (article: Article) => void) {
  useEffect(() => {
    const channel = supabase
      .channel("news_articles_feed")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "news_articles" },
        (payload) => {
          onNewArticle(payload.new as Article);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [onNewArticle]);
}
