import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router";
import { User, Mail, Phone, Calendar, Heart, ShoppingBag, Edit2 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Badge } from "../components/ui/badge";
import { articles } from "../data/articles";
import { Link } from "react-router";

interface Order {
  id: string;
  game: string;
  amount: string;
  price: number;
  status: 'completed' | 'pending' | 'failed';
  date: string;
}

// Mock orders
const mockOrders: Order[] = [
  {
    id: 'ORD202601260001',
    game: '原神',
    amount: '980创世结晶',
    price: 98,
    status: 'completed',
    date: '2026-01-26 14:30',
  },
  {
    id: 'ORD202601250002',
    game: 'Mobile Legends',
    amount: '429钻石',
    price: 58,
    status: 'completed',
    date: '2026-01-25 10:15',
  },
  {
    id: 'ORD202601240003',
    game: '王者荣耀',
    amount: '588点券',
    price: 58,
    status: 'pending',
    date: '2026-01-24 20:45',
  },
];

// Mock saved articles
const mockSavedArticles = articles.slice(0, 3).map(a => a.id);

export function ProfilePage() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [editedUser, setEditedUser] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
  });

  if (!isAuthenticated) {
    navigate('/');
    return null;
  }

  const savedArticles = articles.filter(a => mockSavedArticles.includes(a.id));

  const statusColors = {
    completed: 'bg-green-500',
    pending: 'bg-yellow-500',
    failed: 'bg-red-500',
  };

  const statusLabels = {
    completed: '已完成',
    pending: '处理中',
    failed: '失败',
  };

  const handleSave = () => {
    // Mock save
    setIsEditing(false);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">个人中心</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Info Card */}
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-lg p-6 sticky top-24">
            <div className="text-center mb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                {user?.avatar ? (
                  <img src={user.avatar} alt={user.name} className="w-full h-full rounded-full object-cover" />
                ) : (
                  <User className="w-10 h-10 text-white" />
                )}
              </div>
              <h2 className="text-xl font-bold mb-1">{user?.name}</h2>
              <p className="text-sm text-muted-foreground">普通会员</p>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm text-muted-foreground">邮箱</p>
                  <p className="text-sm">{user?.email}</p>
                </div>
              </div>
              {user?.phone && (
                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">手机</p>
                    <p className="text-sm">{user.phone}</p>
                  </div>
                </div>
              )}
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm text-muted-foreground">注册时间</p>
                  <p className="text-sm">{user?.joinDate}</p>
                </div>
              </div>
            </div>

            <Button 
              variant="outline" 
              className="w-full mt-6"
              onClick={() => setIsEditing(true)}
            >
              <Edit2 className="w-4 h-4 mr-2" />
              编辑资料
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="info">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="info">
                <User className="w-4 h-4 mr-2" />
                个人信息
              </TabsTrigger>
              <TabsTrigger value="favorites">
                <Heart className="w-4 h-4 mr-2" />
                我的收藏
              </TabsTrigger>
              <TabsTrigger value="orders">
                <ShoppingBag className="w-4 h-4 mr-2" />
                我的订单
              </TabsTrigger>
            </TabsList>

            {/* Personal Info */}
            <TabsContent value="info" className="mt-6">
              <div className="bg-card border border-border rounded-lg p-6">
                {isEditing ? (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="name">用户名</Label>
                      <Input
                        id="name"
                        value={editedUser.name}
                        onChange={(e) => setEditedUser({ ...editedUser, name: e.target.value })}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">邮箱（不可修改）</Label>
                      <Input
                        id="email"
                        value={user?.email}
                        disabled
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone">手机号</Label>
                      <Input
                        id="phone"
                        value={editedUser.phone}
                        onChange={(e) => setEditedUser({ ...editedUser, phone: e.target.value })}
                        placeholder="请输入手机号"
                        className="mt-2"
                      />
                    </div>
                    <div className="flex gap-4">
                      <Button onClick={handleSave}>保存</Button>
                      <Button variant="outline" onClick={() => setIsEditing(false)}>取消</Button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <h3 className="font-bold mb-4">账户信息</h3>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">用户名</p>
                        <p>{user?.name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">邮箱</p>
                        <p>{user?.email}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">手机号</p>
                        <p>{user?.phone || '未设置'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">会员等级</p>
                        <Badge>普通会员</Badge>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Favorites */}
            <TabsContent value="favorites" className="mt-6">
              <div className="space-y-4">
                {savedArticles.length > 0 ? (
                  savedArticles.map((article) => (
                    <Link
                      key={article.id}
                      to={`/articles/${article.id}`}
                      className="block bg-card border border-border rounded-lg p-4 hover:shadow-lg transition-all"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold">{article.title}</h3>
                        <Badge>{article.categoryName}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                        {article.excerpt}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{article.publishDate}</span>
                        <span>{article.readTime}</span>
                      </div>
                    </Link>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <Heart className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground mb-4">还没有收藏任何文章</p>
                    <Link to="/articles">
                      <Button variant="outline">浏览文章</Button>
                    </Link>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Orders */}
            <TabsContent value="orders" className="mt-6">
              <div className="space-y-4">
                {mockOrders.map((order) => (
                  <div
                    key={order.id}
                    className="bg-card border border-border rounded-lg p-4"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">订单号: {order.id}</p>
                        <h3 className="font-semibold">{order.game} - {order.amount}</h3>
                      </div>
                      <Badge className={statusColors[order.status]}>
                        {statusLabels[order.status]}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">{order.date}</span>
                      <span className="font-bold text-primary">¥{order.price}</span>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
