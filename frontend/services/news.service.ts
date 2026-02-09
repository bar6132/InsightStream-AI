import api from "@/lib/api";

export interface FeedRequest {
  tags: string[];
}

// נשתמש בזה כדי להגדיר איך נראית כתבה שחוזרת
export interface Article {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at?: string;
  score?: number;
}

export interface FeedResponse {
  feed: Article[];
}

export const newsService = {
  // קבלת הפיד האישי
  async getMyFeed(tags: string[]) {
    const response = await api.post<FeedResponse>("/feed", { tags });
    return response.data;
  },
  
  // בעתיד נוסיף פה: getArticleById, searchNews, etc.
};