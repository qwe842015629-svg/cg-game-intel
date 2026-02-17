import { useState, useEffect } from "react";
import { Link } from "react-router";
import { ChevronLeft, ChevronRight, TrendingUp, Zap, Shield, Clock } from "lucide-react";
import { Button } from "../components/ui/button";
import { GameRechargeCard } from "../components/GameRechargeCard";
import { rechargeGames, gameCategories } from "../data/rechargeGames";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";

export function HomePage() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const featuredGames = rechargeGames.filter(g => g.hot).slice(0, 3);
  const hotGames = rechargeGames.filter(g => g.hot);

  // Auto-play carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % featuredGames.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [featuredGames.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % featuredGames.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + featuredGames.length) % featuredGames.length);
  };

  return (
    <div>
      {/* Hero Carousel */}
      <section className="relative h-[500px] bg-muted overflow-hidden">
        <div className="relative h-full">
          {featuredGames.map((game, index) => (
            <div
              key={game.id}
              className={`absolute inset-0 transition-opacity duration-500 ${
                index === currentSlide ? "opacity-100" : "opacity-0"
              }`}
            >
              <div className="absolute inset-0">
                <ImageWithFallback
                  src={game.image}
                  alt={game.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent"></div>
              </div>
              <div className="relative container mx-auto px-4 h-full flex items-center">
                <div className="max-w-xl">
                  <div className="text-sm text-muted-foreground mb-2">{game.categoryName}</div>
                  <h1 className="text-5xl font-bold mb-2">{game.name}</h1>
                  <p className="text-lg mb-6 text-muted-foreground">{game.description}</p>
                  <div className="flex items-center gap-4 mb-6">
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4" />
                      <span>{game.processingTime}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Shield className="w-4 h-4" />
                      <span>安全保障</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Link to={`/games/${game.id}`}>
                      <Button size="lg">
                        立即充值
                      </Button>
                    </Link>
                    <Link to="/games">
                      <Button size="lg" variant="outline">
                        浏览更多游戏
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Carousel Controls */}
        <button
          onClick={prevSlide}
          className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-background/50 hover:bg-background/70 rounded-full flex items-center justify-center transition-colors"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button
          onClick={nextSlide}
          className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-background/50 hover:bg-background/70 rounded-full flex items-center justify-center transition-colors"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Carousel Indicators */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
          {featuredGames.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`h-2 rounded-full transition-all ${
                index === currentSlide ? "bg-primary w-8" : "bg-muted-foreground/50 w-2"
              }`}
            />
          ))}
        </div>
      </section>

      <div className="container mx-auto px-4 py-12">
        {/* Features */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="bg-card border border-border rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">快速到账</h3>
            <p className="text-sm text-muted-foreground">充值后1-10分钟快速到账</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">安全保障</h3>
            <p className="text-sm text-muted-foreground">正规渠道，交易安全有保障</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">24小时客服</h3>
            <p className="text-sm text-muted-foreground">专业客服团队随时为您服务</p>
          </div>
        </section>

        {/* Hot Games Section */}
        <section className="mb-16">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-6 h-6 text-red-500" />
              <h2 className="text-2xl font-bold">热门充值游戏</h2>
            </div>
            <Link to="/games">
              <Button variant="ghost">查看更多 →</Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {hotGames.map((game) => (
              <GameRechargeCard key={game.id} game={game} />
            ))}
          </div>
        </section>

        {/* Categories Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6">游戏分类</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {gameCategories.map((category) => (
              <Link
                key={category.id}
                to={category.id === 'all' ? '/games' : `/games?category=${category.id}`}
                className="bg-card border border-border hover:border-primary rounded-lg p-6 text-center transition-all group"
              >
                <div className="text-4xl mb-3">{category.icon}</div>
                <h3 className="font-semibold">{category.name}</h3>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
