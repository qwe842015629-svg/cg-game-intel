import { useState } from "react";
import { Link } from "react-router";
import { Search, HelpCircle, ThumbsUp, Eye } from "lucide-react";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { rechargeQuestions, questionCategories } from "../data/rechargeQuestions";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";

export function RechargeQuestionsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("全部问题");

  const filteredQuestions = rechargeQuestions.filter((q) => {
    const matchesSearch =
      !searchQuery ||
      q.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      q.content.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory =
      selectedCategory === "全部问题" || q.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8 text-center">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <HelpCircle className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold mb-2">充值问题解答</h1>
        <p className="text-muted-foreground">快速找到您遇到的问题和解决方案</p>
      </div>

      {/* Search */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            placeholder="搜索您的问题..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-12 text-lg"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-8">
        <TabsList className="w-full justify-start flex-wrap h-auto">
          {questionCategories.map((category) => (
            <TabsTrigger key={category} value={category}>
              {category}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Results Count */}
      <div className="mb-6">
        <p className="text-muted-foreground">
          找到 <span className="font-semibold text-foreground">{filteredQuestions.length}</span> 个问题
        </p>
      </div>

      {/* Questions List */}
      {filteredQuestions.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 mb-8">
          {filteredQuestions.map((question) => (
            <Link
              key={question.id}
              to={`/recharge-questions/${question.id}`}
              className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-all group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <Badge className="mb-2">{question.category}</Badge>
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                    {question.title}
                  </h3>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-2 mb-3">
                {question.relatedGames.slice(0, 3).map((game) => (
                  <Badge key={game} variant="outline" className="text-xs">
                    {game}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Eye className="w-4 h-4" />
                  {question.views} 次查看
                </div>
                <div className="flex items-center gap-1">
                  <ThumbsUp className="w-4 h-4" />
                  {question.helpful} 人觉得有用
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">未找到相关问题</h3>
          <p className="text-muted-foreground mb-4">尝试使用其他关键词搜索</p>
          <Button onClick={() => setSearchQuery("")} variant="outline">
            清除搜索
          </Button>
        </div>
      )}

      {/* Contact Support */}
      <div className="max-w-2xl mx-auto mt-12 bg-card border border-border rounded-lg p-8 text-center">
        <h3 className="text-xl font-bold mb-4">没有找到您的问题？</h3>
        <p className="text-muted-foreground mb-6">
          我们的客服团队随时准备为您提供帮助
        </p>
        <Link to="/customer-service">
          <Button size="lg">联系客服</Button>
        </Link>
      </div>
    </div>
  );
}
