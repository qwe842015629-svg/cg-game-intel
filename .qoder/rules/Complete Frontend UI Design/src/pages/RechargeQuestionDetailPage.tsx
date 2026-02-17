import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router";
import { ArrowLeft, ThumbsUp, ThumbsDown, Eye, Share2 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { rechargeQuestions } from "../data/rechargeQuestions";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner@2.0.3";

export function RechargeQuestionDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [helpful, setHelpful] = useState<boolean | null>(null);
  
  const question = rechargeQuestions.find((q) => q.id === id);
  const relatedQuestions = rechargeQuestions
    .filter((q) => q.id !== id && q.category === question?.category)
    .slice(0, 5);

  if (!question) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl mb-4">问题未找到</h1>
        <Link to="/recharge-questions">
          <Button>返回问题列表</Button>
        </Link>
      </div>
    );
  }

  const handleFeedback = (isHelpful: boolean) => {
    setHelpful(isHelpful);
    toast.success(isHelpful ? "感谢您的反馈！" : "我们会继续改进");
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="w-4 h-4 mr-2" />
        返回
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Question Header */}
          <div className="mb-6">
            <Badge className="mb-4">{question.category}</Badge>
            <h1 className="text-4xl font-bold mb-6">{question.title}</h1>
            
            <div className="flex items-center gap-6 text-sm text-muted-foreground mb-6">
              <div className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                {question.views} 次查看
              </div>
              <div className="flex items-center gap-1">
                <ThumbsUp className="w-4 h-4" />
                {question.helpful} 人觉得有用
              </div>
            </div>

            {/* Related Games */}
            {question.relatedGames.length > 0 && (
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-2">适用游戏：</p>
                <div className="flex flex-wrap gap-2">
                  {question.relatedGames.map((game) => (
                    <Badge key={game} variant="outline">
                      {game}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Question Content */}
          <div className="prose prose-slate max-w-none mb-12 bg-card border border-border rounded-lg p-6">
            <ReactMarkdown>{question.content}</ReactMarkdown>
          </div>

          {/* Feedback */}
          <div className="bg-card border border-border rounded-lg p-6 mb-8">
            <h3 className="font-bold mb-4">这篇文章对您有帮助吗？</h3>
            <div className="flex gap-4">
              <Button
                variant={helpful === true ? "default" : "outline"}
                onClick={() => handleFeedback(true)}
                disabled={helpful !== null}
              >
                <ThumbsUp className="w-4 h-4 mr-2" />
                有帮助
              </Button>
              <Button
                variant={helpful === false ? "default" : "outline"}
                onClick={() => handleFeedback(false)}
                disabled={helpful !== null}
              >
                <ThumbsDown className="w-4 h-4 mr-2" />
                没帮助
              </Button>
            </div>
            {helpful !== null && (
              <p className="text-sm text-muted-foreground mt-4">
                感谢您的反馈！我们会继续改进内容质量。
              </p>
            )}
          </div>

          {/* Share */}
          <div className="flex items-center gap-4">
            <span className="text-muted-foreground">分享此问题：</span>
            <Button variant="outline" size="sm">
              <Share2 className="w-4 h-4 mr-2" />
              分享
            </Button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Related Questions */}
          {relatedQuestions.length > 0 && (
            <div className="mb-8 bg-card border border-border rounded-lg p-6">
              <h3 className="font-bold mb-4">相关问题</h3>
              <div className="space-y-4">
                {relatedQuestions.map((relatedQuestion) => (
                  <Link
                    key={relatedQuestion.id}
                    to={`/recharge-questions/${relatedQuestion.id}`}
                    className="block group"
                  >
                    <h4 className="text-sm font-medium mb-1 line-clamp-2 group-hover:text-primary transition-colors">
                      {relatedQuestion.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Eye className="w-3 h-3" />
                      {relatedQuestion.views}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Quick Links */}
          <div className="bg-card border border-border rounded-lg p-6 mb-8">
            <h3 className="font-bold mb-4">快速链接</h3>
            <div className="space-y-2">
              <Link to="/recharge-questions" className="block text-sm text-primary hover:underline">
                查看所有问题
              </Link>
              <Link to="/articles" className="block text-sm text-primary hover:underline">
                浏览文章资讯
              </Link>
              <Link to="/games" className="block text-sm text-primary hover:underline">
                充值游戏
              </Link>
            </div>
          </div>

          {/* Customer Service */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-bold mb-4">仍需帮助？</h3>
            <p className="text-sm text-muted-foreground mb-4">
              如果这篇文章没有解决您的问题，请联系我们的客服团队
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
