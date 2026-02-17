import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { GamesPage } from "./pages/GamesPage";
import { GameDetailPage } from "./pages/GameDetailPage";
import { ArticlesPage } from "./pages/ArticlesPage";
import { ArticleDetailPage } from "./pages/ArticleDetailPage";
import { ProfilePage } from "./pages/ProfilePage";
import { CustomerServicePage } from "./pages/CustomerServicePage";
import { RechargeQuestionsPage } from "./pages/RechargeQuestionsPage";
import { RechargeQuestionDetailPage } from "./pages/RechargeQuestionDetailPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: HomePage },
      { path: "games", Component: GamesPage },
      { path: "games/:id", Component: GameDetailPage },
      { path: "articles", Component: ArticlesPage },
      { path: "articles/:id", Component: ArticleDetailPage },
      { path: "profile", Component: ProfilePage },
      { path: "customer-service", Component: CustomerServicePage },
      { path: "recharge-questions", Component: RechargeQuestionsPage },
      { path: "recharge-questions/:id", Component: RechargeQuestionDetailPage },
    ],
  },
]);