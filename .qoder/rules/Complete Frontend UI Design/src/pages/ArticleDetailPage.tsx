import { useParams, useNavigate, Link } from "react-router";
import { ArrowLeft, Calendar, Eye, Clock, User, Share2 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { articles } from "../data/articles";
import { rechargeGames } from "../data/rechargeGames";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { CommentSection } from "../components/CommentSection";
import { GameRechargeCard } from "../components/GameRechargeCard";
import ReactMarkdown from "react-markdown";

export function ArticleDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const article = articles.find((a) => a.id === id);
  const relatedArticles = articles
    .filter((a) => a.id !== id && a.category === article?.category)
    .slice(0, 3);
  const hotGames = rechargeGames.filter(g => g.hot).slice(0, 3);

  if (!article) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl mb-4">文章未找到</h1>
        <Link to="/articles">
          <Button>返回文章列表</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="w-4 h-4 mr-2" />
        返回
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Article Header */}
          <div className="mb-6">
            <Badge className="mb-4">{article.categoryName}</Badge>
            <h1 className="text-4xl font-bold mb-4">{article.title}</h1>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-6">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4" />
                {article.author}
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                {article.publishDate}
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {article.readTime}
              </div>
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4" />
                {article.views} 次阅读
              </div>
            </div>

            <div className="flex gap-2 mb-6">
              {article.tags.map((tag) => (
                <Badge key={tag} variant="outline">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Featured Image */}
          <div className="aspect-video rounded-lg overflow-hidden mb-8">
            <ImageWithFallback
              src={article.image}
              alt={article.title}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Article Content */}
          <div className="prose prose-slate max-w-none mb-12 bg-card border border-border rounded-lg p-6">
            <ReactMarkdown>{article.content}</ReactMarkdown>
          </div>

          {/* Share */}
          <div className="flex items-center gap-4 mb-12 pb-12 border-b border-border">
            <span className="text-muted-foreground">分享文章：</span>
            <Button variant="outline" size="sm">
              <Share2 className="w-4 h-4 mr-2" />
              分享
            </Button>
          </div>

          {/* Comments */}
          <CommentSection itemId={article.id} itemType="article" />
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Hot Articles */}
          {relatedArticles.length > 0 && (
            <div className="mb-8 bg-card border border-border rounded-lg p-6">
              <h3 className="font-bold mb-4">相关文章</h3>
              <div className="space-y-4">
                {relatedArticles.map((relatedArticle) => (
                  <Link
                    key={relatedArticle.id}
                    to={`/articles/${relatedArticle.id}`}
                    className="block group"
                  >
                    <h4 className="text-sm font-medium mb-1 line-clamp-2 group-hover:text-primary transition-colors">
                      {relatedArticle.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Eye className="w-3 h-3" />
                      {relatedArticle.views}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Hot Games */}
          <div className="mb-8 bg-card border border-border rounded-lg p-6">
            <h3 className="font-bold mb-4">热门充值游戏</h3>
            <div className="space-y-4">
              {hotGames.map((game) => (
                <Link
                  key={game.id}
                  to={`/games/${game.id}`}
                  className="flex gap-3 group"
                >
                  <div className="w-20 h-12 flex-shrink-0 rounded overflow-hidden">
                    <ImageWithFallback
                      src={game.image}
                      alt={game.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium line-clamp-1 group-hover:text-primary transition-colors">
                      {game.name}
                    </h4>
                    <p className="text-xs text-muted-foreground">{game.categoryName}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Customer Service */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-bold mb-4">需要帮助？</h3>
            <p className="text-sm text-muted-foreground mb-4">
              如有任何疑问，请随时联系我们的客服团队
            </p>
            <Link to="/customer-service">
              <Button className="w-full">联系客服</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
