import { useState, useMemo } from "react";
import { useSearchParams } from "react-router";
import { Search } from "lucide-react";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { GameRechargeCard } from "../components/GameRechargeCard";
import { rechargeGames, gameCategories } from "../data/rechargeGames";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs";

export function GamesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState("");
  const categoryParam = searchParams.get('category') || 'all';

  // Filter games
  const filteredGames = useMemo(() => {
    let result = rechargeGames;

    // Filter by search query
    if (searchQuery) {
      result = result.filter((game) =>
        game.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        game.nameEn.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by category
    if (categoryParam !== 'all') {
      result = result.filter((game) => game.category === categoryParam);
    }

    return result;
  }, [searchQuery, categoryParam]);

  const handleCategoryChange = (value: string) => {
    if (value === 'all') {
      setSearchParams({});
    } else {
      setSearchParams({ category: value });
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">充值游戏</h1>
        <p className="text-muted-foreground">选择您要充值的游戏</p>
      </div>

      {/* Filters */}
      <div className="mb-8">
        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="搜索游戏名称..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 max-w-md"
          />
        </div>

        {/* Category Tabs */}
        <Tabs value={categoryParam} onValueChange={handleCategoryChange}>
          <TabsList>
            {gameCategories.map((category) => (
              <TabsTrigger key={category.id} value={category.id}>
                {category.icon} {category.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Results Count */}
      <div className="mb-6">
        <p className="text-muted-foreground">
          找到 <span className="font-semibold text-foreground">{filteredGames.length}</span> 款游戏
        </p>
      </div>

      {/* Games Grid */}
      {filteredGames.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredGames.map((game) => (
            <GameRechargeCard key={game.id} game={game} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">未找到游戏</h3>
          <p className="text-muted-foreground mb-4">尝试调整您的搜索条件</p>
          <Button onClick={() => { setSearchQuery(""); handleCategoryChange("all"); }} variant="outline">
            清除筛选
          </Button>
        </div>
      )}
    </div>
  );
}
