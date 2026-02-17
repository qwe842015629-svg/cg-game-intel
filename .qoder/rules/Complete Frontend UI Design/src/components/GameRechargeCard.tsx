import { Link } from "react-router";
import { Badge } from "./ui/badge";
import { RechargeGame } from "../data/rechargeGames";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { Flame } from "lucide-react";

interface GameRechargeCardProps {
  game: RechargeGame;
}

export function GameRechargeCard({ game }: GameRechargeCardProps) {
  return (
    <Link to={`/games/${game.id}`} className="group">
      <div className="bg-card border border-border rounded-lg overflow-hidden transition-all hover:scale-105 hover:shadow-lg">
        {/* Game Image */}
        <div className="relative aspect-[16/9] overflow-hidden">
          <ImageWithFallback
            src={game.image}
            alt={game.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
          {game.hot && (
            <div className="absolute top-2 right-2">
              <Badge className="bg-red-500 text-white flex items-center gap-1">
                <Flame className="w-3 h-3" />
                热门
              </Badge>
            </div>
          )}
          <div className="absolute bottom-2 left-2">
            <Badge variant="secondary" className="text-xs">
              {game.categoryName}
            </Badge>
          </div>
        </div>

        {/* Game Info */}
        <div className="p-4">
          <h3 className="font-semibold mb-1 truncate">{game.name}</h3>
          <p className="text-xs text-muted-foreground mb-3">{game.nameEn}</p>
          
          <div className="flex flex-wrap gap-1 mb-3">
            {game.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>

          <p className="text-sm text-muted-foreground line-clamp-2">
            {game.description}
          </p>
        </div>
      </div>
    </Link>
  );
}
