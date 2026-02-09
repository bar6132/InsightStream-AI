import React from 'react';
import { ExternalLink, Calendar, Star } from 'lucide-react';

interface Article {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at?: string;
  score?: number;
}

interface NewsCardProps {
  article: Article;
}

export default function NewsCard({ article }: NewsCardProps) {
  // פונקציית עזר לפרמוט תאריך (אם אין תאריך, נציג 'Just now')
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Just now';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="group relative flex flex-col justify-between rounded-xl bg-surface border border-gray-800 p-6 transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10">
      
      {/* ציון רלוונטיות (אם קיים) */}
      {article.score && (
        <div className="absolute top-4 right-4 flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
          <Star className="h-3 w-3 fill-primary" />
          <span>{Math.round(article.score * 100)}% Match</span>
        </div>
      )}

      <div>
        {/* מקור ותאריך */}
        <div className="mb-3 flex items-center gap-2 text-xs text-gray-400">
          <span className="font-semibold text-gray-300 uppercase tracking-wider">{article.source}</span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDate(article.published_at)}
          </span>
        </div>

        {/* כותרת */}
        <h3 className="mb-2 text-xl font-bold text-white leading-tight group-hover:text-primary transition-colors">
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
        </h3>

        {/* תקציר */}
        <p className="text-gray-400 text-sm leading-relaxed line-clamp-3">
          {article.summary}
        </p>
      </div>

      {/* כפתור קריאה */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <a 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex items-center text-sm font-medium text-primary hover:text-blue-400 transition-colors"
        >
          Read full article <ExternalLink className="ml-1 h-3 w-3" />
        </a>
      </div>
    </div>
  );
}