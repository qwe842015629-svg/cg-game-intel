import { Outlet, Link, useLocation } from "react-router";
import { ShoppingCart, Search, User, Menu, Sun, Moon, MessageCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useCart } from "../contexts/CartContext";
import { useTheme } from "../contexts/ThemeContext";
import { useAuth } from "../contexts/AuthContext";
import { Badge } from "./ui/badge";
import { useState } from "react";
import { AuthDialog } from "./AuthDialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

export function Layout() {
  const location = useLocation();
  const { itemCount } = useCart();
  const { theme, toggleTheme } = useTheme();
  const { user, logout, isAuthenticated } = useAuth();
  const [authDialogOpen, setAuthDialogOpen] = useState(false);

  const navLinks = [
    { path: "/", label: "主页" },
    { path: "/games", label: "充值游戏" },
    { path: "/articles", label: "文章资讯" },
    { path: "/recharge-questions", label: "充值问题" },
    { path: "/customer-service", label: "客服中心" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card border-b border-border">
        <div className="container mx-auto px-4">
          {/* Top Bar */}
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded"></div>
              <span className="text-xl font-bold">游戏充值中心</span>
            </Link>

            {/* Search Bar */}
            <div className="hidden md:flex flex-1 max-w-xl mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="搜索游戏..."
                  className="pl-10"
                />
              </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              {/* Theme Toggle */}
              <Button variant="ghost" size="icon" onClick={toggleTheme}>
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </Button>

              {/* Customer Service */}
              <Link to="/customer-service">
                <Button variant="ghost" size="icon">
                  <MessageCircle className="w-5 h-5" />
                </Button>
              </Link>

              {/* User Menu */}
              {isAuthenticated ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <User className="w-5 h-5" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <div className="px-2 py-1.5">
                      <p className="font-medium">{user?.name}</p>
                      <p className="text-sm text-muted-foreground">{user?.email}</p>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link to="/profile">个人中心</Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout}>
                      退出登录
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button variant="ghost" size="icon" onClick={() => setAuthDialogOpen(true)}>
                  <User className="w-5 h-5" />
                </Button>
              )}

              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex gap-6 pb-3">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`text-sm transition-colors ${
                  location.pathname === link.path
                    ? "text-primary font-medium"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-card border-t border-border mt-20">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-bold mb-4">关于我们</h3>
              <p className="text-muted-foreground text-sm">
                专业的游戏充值平台，支持多种支付方式，安全快捷。
              </p>
            </div>
            <div>
              <h3 className="font-bold mb-4">客户服务</h3>
              <ul className="space-y-2 text-sm">
                <li><Link to="/customer-service" className="text-muted-foreground hover:text-foreground">联系客服</Link></li>
                <li><Link to="/recharge-questions" className="text-muted-foreground hover:text-foreground">充值问题</Link></li>
                <li><Link to="/articles" className="text-muted-foreground hover:text-foreground">常见问题</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-4">支付方式</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>支付宝</li>
                <li>微信支付</li>
                <li>PayPal</li>
                <li>USDT</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-4">关注我们</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="text-muted-foreground hover:text-foreground">微博</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-foreground">Twitter</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-foreground">Discord</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border mt-8 pt-8 text-center text-muted-foreground text-sm">
            <p>&copy; 2026 游戏充值中心. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Auth Dialog */}
      <AuthDialog open={authDialogOpen} onOpenChange={setAuthDialogOpen} />
    </div>
  );
}