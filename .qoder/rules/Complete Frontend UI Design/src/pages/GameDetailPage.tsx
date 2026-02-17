import { useParams, useNavigate, Link } from "react-router";
import { useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  Shield,
  MessageCircle,
  Globe,
  CreditCard,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { rechargeGames, paymentMethodLabels } from "../data/rechargeGames";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { toast } from "sonner@2.0.3";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { CommentSection } from "../components/CommentSection";

export function GameDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedOption, setSelectedOption] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("");
  const [gameId, setGameId] = useState("");
  const [selectedPayment, setSelectedPayment] = useState("");

  const game = rechargeGames.find((g) => g.id === id);

  if (!game) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl mb-4">游戏未找到</h1>
        <Link to="/games">
          <Button>返回游戏列表</Button>
        </Link>
      </div>
    );
  }

  const selectedRechargeOption = game.rechargeOptions.find(
    (opt) => opt.id === selectedOption
  );

  const handleRecharge = () => {
    if (!selectedOption) {
      toast.error("请选择充值金额");
      return;
    }
    if (!selectedRegion) {
      toast.error("请选择游戏区服");
      return;
    }
    if (!gameId) {
      toast.error("请输入游戏ID");
      return;
    }
    if (!selectedPayment) {
      toast.error("请选择支付方式");
      return;
    }

    toast.success("充值订单已提交，请完成支付");
    // Mock payment flow
    setTimeout(() => {
      toast.success("支付成功！充值将在" + game.processingTime + "内到账");
    }, 2000);
  };

  return (
    <div>
      {/* Back Button */}
      <div className="container mx-auto px-4 py-4">
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          返回
        </Button>
      </div>

      {/* Game Header */}
      <div className="relative h-[300px] bg-muted mb-8">
        <div className="absolute inset-0">
          <ImageWithFallback
            src={game.image}
            alt={game.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent"></div>
        </div>
      </div>

      <div className="container mx-auto px-4 -mt-32 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Title and Basic Info */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <Badge>{game.categoryName}</Badge>
                {game.hot && <Badge variant="destructive">热门</Badge>}
              </div>
              <h1 className="text-4xl font-bold mb-2">{game.name}</h1>
              <p className="text-muted-foreground">{game.nameEn}</p>
              
              <div className="flex flex-wrap gap-2 mt-4">
                {game.tags.map((tag) => (
                  <Badge key={tag} variant="outline">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="description" className="mb-8">
              <TabsList>
                <TabsTrigger value="description">游戏简介</TabsTrigger>
                <TabsTrigger value="instructions">充值说明</TabsTrigger>
                <TabsTrigger value="comments">用户评论</TabsTrigger>
              </TabsList>

              <TabsContent value="description" className="bg-card border border-border rounded-lg p-6 mt-4">
                <p className="mb-6">{game.description}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-primary mt-1" />
                    <div>
                      <p className="text-sm text-muted-foreground">到账时间</p>
                      <p>{game.processingTime}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Globe className="w-5 h-5 text-primary mt-1" />
                    <div>
                      <p className="text-sm text-muted-foreground">支持区服</p>
                      <p>{game.region.join("、")}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CreditCard className="w-5 h-5 text-primary mt-1" />
                    <div>
                      <p className="text-sm text-muted-foreground">支付方式</p>
                      <p>{game.paymentMethods.map(pm => paymentMethodLabels[pm]).join("、")}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-primary mt-1" />
                    <div>
                      <p className="text-sm text-muted-foreground">安全保障</p>
                      <p>正规渠道充值</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="instructions" className="bg-card border border-border rounded-lg p-6 mt-4">
                <h3 className="font-semibold mb-4">充值步骤</h3>
                <ol className="space-y-3 list-decimal list-inside">
                  {game.instructions.map((instruction, index) => (
                    <li key={index} className="text-muted-foreground">
                      {instruction}
                    </li>
                  ))}
                </ol>
                
                <div className="mt-6 p-4 bg-muted rounded-lg">
                  <div className="flex items-start gap-2">
                    <MessageCircle className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="font-semibold mb-1">需要帮助？</p>
                      <p className="text-sm text-muted-foreground mb-3">
                        如有任何疑问，请随时联系我们的客服团队
                      </p>
                      <Link to="/customer-service">
                        <Button size="sm">联系客服</Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="comments" className="mt-4">
                <CommentSection itemId={game.id} itemType="game" />
              </TabsContent>
            </Tabs>
          </div>

          {/* Recharge Card */}
          <div className="lg:col-span-1">
            <div className="bg-card border border-border rounded-lg p-6 sticky top-24">
              <h2 className="font-bold text-lg mb-4">充值选项</h2>

              {/* Region Selection */}
              <div className="mb-4">
                <Label>选择区服 *</Label>
                <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="请选择区服" />
                  </SelectTrigger>
                  <SelectContent>
                    {game.region.map((region) => (
                      <SelectItem key={region} value={region}>
                        {region}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Game ID Input */}
              <div className="mb-4">
                <Label htmlFor="game-id">游戏ID *</Label>
                <Input
                  id="game-id"
                  placeholder="请输入您的游戏ID"
                  value={gameId}
                  onChange={(e) => setGameId(e.target.value)}
                  className="mt-2"
                />
              </div>

              {/* Recharge Options */}
              <div className="mb-4">
                <Label>选择充值金额 *</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {game.rechargeOptions.map((option) => (
                    <button
                      key={option.id}
                      onClick={() => setSelectedOption(option.id)}
                      className={`relative p-3 border rounded-lg text-left transition-all ${
                        selectedOption === option.id
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      {option.popular && (
                        <Badge className="absolute -top-2 -right-2 text-xs">推荐</Badge>
                      )}
                      <div className="text-sm font-medium mb-1">{option.amount}</div>
                      <div className="flex items-baseline gap-1">
                        <span className="text-primary font-bold">¥{option.price}</span>
                        {option.originalPrice && (
                          <span className="text-xs text-muted-foreground line-through">
                            ¥{option.originalPrice}
                          </span>
                        )}
                      </div>
                      {option.discount && (
                        <div className="text-xs text-red-500 mt-1">-{option.discount}%</div>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Payment Method */}
              <div className="mb-6">
                <Label>支付方式 *</Label>
                <Select value={selectedPayment} onValueChange={setSelectedPayment}>
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="请选择支付方式" />
                  </SelectTrigger>
                  <SelectContent>
                    {game.paymentMethods.map((method) => (
                      <SelectItem key={method} value={method}>
                        {paymentMethodLabels[method]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Total */}
              {selectedRechargeOption && (
                <div className="mb-6 p-4 bg-muted rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">应付金额</span>
                    <span className="text-2xl font-bold text-primary">
                      ¥{selectedRechargeOption.price}
                    </span>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <Button
                onClick={handleRecharge}
                className="w-full"
                size="lg"
              >
                立即充值
              </Button>

              {/* Additional Info */}
              <div className="mt-6 pt-6 border-t border-border space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span className="text-muted-foreground">{game.processingTime}内到账</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span className="text-muted-foreground">正规渠道安全保障</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span className="text-muted-foreground">24小时客服支持</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
