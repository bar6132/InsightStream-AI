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
  async getMyFeed() {
    const response = await api.get<FeedResponse>("/news/feed");
    return response.data;
  },
};