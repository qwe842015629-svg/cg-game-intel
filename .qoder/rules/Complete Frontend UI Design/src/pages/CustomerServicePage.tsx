import { MessageCircle, Mail, Clock, HelpCircle, Send } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { useState } from "react";
import { toast } from "sonner@2.0.3";
import { Link } from "react-router";

export function CustomerServicePage() {
  const [message, setMessage] = useState({
    name: '',
    email: '',
    subject: '',
    content: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("留言已提交，我们会尽快回复您！");
    setMessage({ name: '', email: '', subject: '', content: '' });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="text-center mb-12">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <MessageCircle className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold mb-2">客服中心</h1>
        <p className="text-muted-foreground">我们随时为您提供帮助</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Contact Methods */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Online Chat */}
            <div className="bg-card border border-border rounded-lg p-6">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <MessageCircle className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-bold mb-2">在线客服</h3>
              <p className="text-sm text-muted-foreground mb-4">
                即时响应，快速解决问题
              </p>
              <Button className="w-full">
                开始聊天
              </Button>
            </div>

            {/* Email */}
            <div className="bg-card border border-border rounded-lg p-6">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Mail className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-bold mb-2">邮件支持</h3>
              <p className="text-sm text-muted-foreground mb-4">
                support@gamecharge.com
              </p>
              <Button variant="outline" className="w-full">
                发送邮件
              </Button>
            </div>

            {/* FAQ */}
            <div className="bg-card border border-border rounded-lg p-6">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <HelpCircle className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-bold mb-2">常见问题</h3>
              <p className="text-sm text-muted-foreground mb-4">
                快速找到答案
              </p>
              <Link to="/recharge-questions">
                <Button variant="outline" className="w-full">
                  查看FAQ
                </Button>
              </Link>
            </div>

            {/* Working Hours */}
            <div className="bg-card border border-border rounded-lg p-6">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Clock className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-bold mb-2">服务时间</h3>
              <p className="text-sm text-muted-foreground mb-2">
                7 x 24小时全天候服务
              </p>
              <p className="text-xs text-muted-foreground">
                平均响应时间：5分钟
              </p>
            </div>
          </div>

          {/* Contact Form */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-xl font-bold mb-6">留言咨询</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">您的姓名 *</Label>
                  <Input
                    id="name"
                    value={message.name}
                    onChange={(e) => setMessage({ ...message, name: e.target.value })}
                    required
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="email">邮箱地址 *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={message.email}
                    onChange={(e) => setMessage({ ...message, email: e.target.value })}
                    required
                    className="mt-2"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="subject">问题类型 *</Label>
                <Input
                  id="subject"
                  value={message.subject}
                  onChange={(e) => setMessage({ ...message, subject: e.target.value })}
                  placeholder="例如：充值问题、账号问题等"
                  required
                  className="mt-2"
                />
              </div>
              <div>
                <Label htmlFor="content">详细描述 *</Label>
                <Textarea
                  id="content"
                  value={message.content}
                  onChange={(e) => setMessage({ ...message, content: e.target.value })}
                  placeholder="请详细描述您遇到的问题..."
                  rows={6}
                  required
                  className="mt-2"
                />
              </div>
              <Button type="submit" className="w-full">
                <Send className="w-4 h-4 mr-2" />
                提交留言
              </Button>
            </form>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Quick Links */}
          <div className="bg-card border border-border rounded-lg p-6 mb-6">
            <h3 className="font-bold mb-4">快速链接</h3>
            <div className="space-y-2">
              <Link to="/recharge-questions" className="block text-sm text-primary hover:underline">
                充值问题解答
              </Link>
              <Link to="/articles" className="block text-sm text-primary hover:underline">
                文章资讯
              </Link>
              <Link to="/games" className="block text-sm text-primary hover:underline">
                充值游戏
              </Link>
            </div>
          </div>

          {/* Contact Info */}
          <div className="bg-card border border-border rounded-lg p-6 mb-6">
            <h3 className="font-bold mb-4">联系方式</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-muted-foreground mb-1">客服邮箱</p>
                <p className="font-medium">support@gamecharge.com</p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">工作时间</p>
                <p className="font-medium">7x24小时</p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">响应时间</p>
                <p className="font-medium">5分钟内</p>
              </div>
            </div>
          </div>

          {/* Social Media */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-bold mb-4">关注我们</h3>
            <div className="space-y-2">
              <a href="#" className="block text-sm hover:text-primary transition-colors">
                📱 微信公众号
              </a>
              <a href="#" className="block text-sm hover:text-primary transition-colors">
                🐦 Twitter
              </a>
              <a href="#" className="block text-sm hover:text-primary transition-colors">
                💬 Discord
              </a>
              <a href="#" className="block text-sm hover:text-primary transition-colors">
                📘 Facebook
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
