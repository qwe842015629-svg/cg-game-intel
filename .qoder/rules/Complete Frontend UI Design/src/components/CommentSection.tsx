import { useState } from "react";
import { MessageSquare, ThumbsUp, User as UserIcon } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner@2.0.3";
import { Badge } from "./ui/badge";

interface Comment {
  id: string;
  author: string;
  content: string;
  date: string;
  likes: number;
  avatar?: string;
}

interface CommentSectionProps {
  itemId: string;
  itemType: 'game' | 'article';
}

// Mock comments data
const mockComments: Record<string, Comment[]> = {
  '1': [
    {
      id: '1',
      author: '游戏玩家小李',
      content: '充值速度很快，客服态度也很好，推荐！',
      date: '2026-01-25 15:30',
      likes: 12,
    },
    {
      id: '2',
      author: '原神大佬',
      content: '这个教程写得很详细，帮助很大，感谢分享！',
      date: '2026-01-24 10:20',
      likes: 8,
    },
  ],
  '2': [
    {
      id: '3',
      author: 'ML玩家',
      content: '优惠力度很大，性价比高！',
      date: '2026-01-26 09:15',
      likes: 15,
    },
  ],
};

export function CommentSection({ itemId, itemType }: CommentSectionProps) {
  const { isAuthenticated } = useAuth();
  const [comments, setComments] = useState<Comment[]>(mockComments[itemId] || []);
  const [newComment, setNewComment] = useState('');
  const [likedComments, setLikedComments] = useState<Set<string>>(new Set());

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      toast.error('请先登录再发表评论');
      return;
    }

    if (!newComment.trim()) {
      toast.error('评论内容不能为空');
      return;
    }

    const comment: Comment = {
      id: Date.now().toString(),
      author: '当前用户',
      content: newComment,
      date: new Date().toLocaleString('zh-CN'),
      likes: 0,
    };

    setComments([comment, ...comments]);
    setNewComment('');
    toast.success('评论发表成功！');
  };

  const handleLike = (commentId: string) => {
    if (!isAuthenticated) {
      toast.error('请先登录');
      return;
    }

    if (likedComments.has(commentId)) {
      setLikedComments((prev) => {
        const next = new Set(prev);
        next.delete(commentId);
        return next;
      });
      setComments((prev) =>
        prev.map((c) =>
          c.id === commentId ? { ...c, likes: c.likes - 1 } : c
        )
      );
    } else {
      setLikedComments((prev) => new Set(prev).add(commentId));
      setComments((prev) =>
        prev.map((c) =>
          c.id === commentId ? { ...c, likes: c.likes + 1 } : c
        )
      );
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <MessageSquare className="w-5 h-5" />
        <h3 className="font-bold">
          {itemType === 'game' ? '用户评价' : '评论'} ({comments.length})
        </h3>
      </div>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="mb-8">
        <Textarea
          placeholder={isAuthenticated ? "写下您的评论..." : "请先登录后再发表评论"}
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          rows={4}
          className="mb-3"
          disabled={!isAuthenticated}
        />
        <div className="flex justify-end">
          <Button type="submit" disabled={!isAuthenticated || !newComment.trim()}>
            发表评论
          </Button>
        </div>
      </form>

      {/* Comments List */}
      <div className="space-y-6">
        {comments.length > 0 ? (
          comments.map((comment) => (
            <div key={comment.id} className="flex gap-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                {comment.avatar ? (
                  <img
                    src={comment.avatar}
                    alt={comment.author}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <UserIcon className="w-5 h-5 text-white" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium">{comment.author}</span>
                  <span className="text-xs text-muted-foreground">{comment.date}</span>
                </div>
                <p className="text-sm mb-3">{comment.content}</p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleLike(comment.id)}
                  className={likedComments.has(comment.id) ? 'text-primary' : ''}
                >
                  <ThumbsUp className="w-4 h-4 mr-1" />
                  {comment.likes > 0 && comment.likes}
                </Button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            还没有评论，快来发表第一条评论吧！
          </div>
        )}
      </div>
    </div>
  );
}
