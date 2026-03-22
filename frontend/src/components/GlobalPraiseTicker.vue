<template>
  <section class="global-praise" aria-label="Global user praise ticker">
    <div class="praise-shell">
      <div class="praise-row">
        <div class="praise-track praise-track--left">
          <article
            v-for="item in trackOne"
            :key="`track-1-${item.id}`"
            class="praise-card"
          >
            <div class="praise-meta">
              <span class="praise-user">{{ item.user }}</span>
              <span class="praise-locale">{{ item.country }} | {{ item.language }}</span>
            </div>
            <p class="praise-message" :dir="item.localeCode === 'ar' ? 'rtl' : 'ltr'">
              {{ item.message }}
            </p>
            <div class="praise-foot">
              <span class="praise-stars">5/5</span>
              <span class="praise-topic">{{ topicLabel(item.topic) }}</span>
            </div>
          </article>
        </div>
      </div>

      <div class="praise-row mt-3">
        <div class="praise-track praise-track--right">
          <article
            v-for="item in trackTwo"
            :key="`track-2-${item.id}`"
            class="praise-card"
          >
            <div class="praise-meta">
              <span class="praise-user">{{ item.user }}</span>
              <span class="praise-locale">{{ item.country }} | {{ item.language }}</span>
            </div>
            <p class="praise-message" :dir="item.localeCode === 'ar' ? 'rtl' : 'ltr'">
              {{ item.message }}
            </p>
            <div class="praise-foot">
              <span class="praise-stars">5/5</span>
              <span class="praise-topic">{{ topicLabel(item.topic) }}</span>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useLanguageStore } from "../stores/language";

type ReviewTopic = "recharge" | "tavern" | "story";
type ReviewLocaleCode = "en" | "zh" | "ja" | "ko" | "fr" | "de" | "es" | "pt" | "ar";

interface ReviewLocale {
  code: ReviewLocaleCode;
  country: string;
  language: string;
  users: string[];
  messages: Record<ReviewTopic, string[]>;
}

interface PraiseReview {
  id: number;
  user: string;
  country: string;
  language: string;
  localeCode: ReviewLocaleCode;
  topic: ReviewTopic;
  message: string;
}

const languageStore = useLanguageStore();

const TOTAL_REVIEWS = 100;
const REVIEW_TOPICS: ReviewTopic[] = ["recharge", "tavern", "story"];

const REVIEW_LOCALES: ReviewLocale[] = [
  {
    code: "en",
    country: "US",
    language: "English",
    users: ["Aiden", "Mia", "Ethan", "Luna", "Noah", "Chloe"],
    messages: {
      recharge: [
        "Overseas top-up to my US and EU accounts arrived in under 30 seconds.",
        "Cross-region recharge worked on first try and payment confirmation was instant.",
        "I can recharge from abroad at night and it still completes immediately.",
      ],
      tavern: [
        "Tavern sync imported my role cards perfectly, no broken fields.",
        "The Tavern panel grouped my characters clearly and export was one click.",
        "Role card sync back to Tavern is fast and stable every time.",
      ],
      story: [
        "The story planner gave me a solid chapter outline in minutes.",
        "Chapter continuation keeps tone consistent, great for long projects.",
        "Plot rewrite tools helped me fix pacing without losing character voice.",
      ],
    },
  },
  {
    code: "zh",
    country: "CN",
    language: "中文",
    users: ["星海", "阿澈", "南舟", "小棠", "未央", "景行"],
    messages: {
      recharge: [
        "海外给日服和美服充值都很快，基本秒到。",
        "跨区付款成功率很高，到账通知也及时。",
        "半夜在国外下单也稳定到账，省心。",
      ],
      tavern: [
        "酒馆角色导入很顺，字段基本不用再手动改。",
        "同步回酒馆一键完成，角色卡结构很干净。",
        "分组和检索做得好，角色多也不乱。",
      ],
      story: [
        "剧情策划生成的大纲可用度高，改几句就能开写。",
        "章节续写能保持人物语气，长篇也稳。",
        "重写受影响章节这个功能太实用了，节省很多时间。",
      ],
    },
  },
  {
    code: "ja",
    country: "JP",
    language: "日本語",
    users: ["Haru", "Yui", "Sora", "Ren", "Mio", "Kaito"],
    messages: {
      recharge: [
        "海外からでもチャージが速く、ほぼ即時反映です。",
        "別リージョンの課金でも決済が安定しています。",
        "深夜でも入金確認が早くて助かります。",
      ],
      tavern: [
        "酒場連携でロールカードをまとめて同期できて便利です。",
        "カードの項目崩れが少なく、移行がとても楽でした。",
        "検索とグループ管理が使いやすく作業が速いです。",
      ],
      story: [
        "プロット自動生成の精度が高く、執筆開始が早いです。",
        "章ごとの続き生成でも文体の一貫性があります。",
        "改稿支援でテンポ調整がしやすくなりました。",
      ],
    },
  },
  {
    code: "ko",
    country: "KR",
    language: "한국어",
    users: ["Minjun", "Jisoo", "Haerin", "Taeyang", "Yuna", "Seojin"],
    messages: {
      recharge: [
        "해외에서도 충전이 매우 빨라서 거의 즉시 반영됩니다.",
        "다른 서버 지역 결제도 안정적으로 완료됩니다.",
        "늦은 시간에도 충전 성공률이 높아 믿고 씁니다.",
      ],
      tavern: [
        "주점 동기화로 캐릭터 카드 정리가 정말 쉬워졌어요.",
        "카드 필드가 깔끔하게 매핑되어 수정이 거의 필요 없습니다.",
        "검색과 그룹 기능이 좋아서 많은 캐릭터도 관리가 편합니다.",
      ],
      story: [
        "스토리 플래너가 챕터 구조를 탄탄하게 잡아줍니다.",
        "이어쓰기 기능이 캐릭터 말투를 잘 유지합니다.",
        "영향 챕터 재작성 기능 덕분에 수정 시간이 크게 줄었습니다.",
      ],
    },
  },
  {
    code: "fr",
    country: "FR",
    language: "Français",
    users: ["Louis", "Emma", "Nolan", "Lina", "Hugo", "Jade"],
    messages: {
      recharge: [
        "Rechargement international validé en quelques secondes.",
        "Paiement cross-région fluide, sans échec pour moi.",
        "Même depuis l'étranger tard le soir, la recharge reste rapide.",
      ],
      tavern: [
        "La synchro Tavern importe mes cartes de rôle sans erreur.",
        "Le retour des cartes vers Tavern est simple et fiable.",
        "La recherche par groupe me fait gagner un temps énorme.",
      ],
      story: [
        "Le plan narratif généré est clair et directement exploitable.",
        "La continuation par chapitre garde bien le même ton.",
        "La réécriture assistée corrige le rythme sans casser les personnages.",
      ],
    },
  },
  {
    code: "de",
    country: "DE",
    language: "Deutsch",
    users: ["Lukas", "Mila", "Felix", "Lea", "Jonas", "Nina"],
    messages: {
      recharge: [
        "Internationale Aufladungen werden bei mir in Sekunden gutgeschrieben.",
        "Regionenübergreifende Zahlung läuft stabil und zuverlässig.",
        "Auch nachts aus dem Ausland klappt die Aufladung sofort.",
      ],
      tavern: [
        "Die Tavern-Synchronisierung übernimmt Rollenkarten sauber.",
        "Rücksync zu Tavern funktioniert schnell und ohne Datenverlust.",
        "Mit Gruppen und Suche finde ich jede Figur sofort.",
      ],
      story: [
        "Der Story-Planer liefert eine starke Kapitelstruktur.",
        "Die Kapitel-Fortsetzung hält Stil und Figurenstimme konsistent.",
        "Das Umschreiben betroffener Kapitel spart viel Zeit beim Feinschliff.",
      ],
    },
  },
  {
    code: "es",
    country: "ES",
    language: "Español",
    users: ["Mateo", "Valeria", "Sofia", "Daniel", "Lucia", "Thiago"],
    messages: {
      recharge: [
        "Las recargas internacionales me llegan en segundos.",
        "El pago entre regiones funciona estable y sin fricción.",
        "Desde el extranjero, incluso de noche, la recarga sigue rápida.",
      ],
      tavern: [
        "La sincronización con Tavern importa mis tarjetas sin errores.",
        "Volver a sincronizar tarjetas a Tavern es rápido y claro.",
        "La búsqueda por grupo facilita mucho gestionar personajes.",
      ],
      story: [
        "El plan de historia sale ordenado y listo para trabajar.",
        "La continuación por capítulos mantiene bien el tono.",
        "Reescribir capítulos afectados me ahorra muchísimo tiempo.",
      ],
    },
  },
  {
    code: "pt",
    country: "BR",
    language: "Português",
    users: ["Lucas", "Ana", "Rafael", "Bianca", "Gabriel", "Lara"],
    messages: {
      recharge: [
        "Recarga internacional caiu em segundos para mim.",
        "Pagamento entre regiões funciona estável e sem travar.",
        "Mesmo de madrugada no exterior, a recarga confirma rápido.",
      ],
      tavern: [
        "A sincronização com Tavern trouxe meus cards sem quebrar campos.",
        "Sincronizar de volta para o Tavern é simples e confiável.",
        "Busca e grupos ajudam muito quando há muitos personagens.",
      ],
      story: [
        "O planejador de enredo gera capítulos bem estruturados.",
        "A continuação mantém a voz dos personagens com consistência.",
        "Reescrever capítulos impactados reduziu muito meu retrabalho.",
      ],
    },
  },
  {
    code: "ar",
    country: "AE",
    language: "العربية",
    users: ["علي", "سارة", "ليان", "كريم", "نور", "يوسف"],
    messages: {
      recharge: [
        "شحن الألعاب من الخارج يصل بسرعة كبيرة.",
        "الدفع بين المناطق يعمل بثبات ومن دون مشاكل.",
        "حتى في وقت متأخر من الليل يتم تأكيد الشحن فورًا.",
      ],
      tavern: [
        "مزامنة Tavern تستورد بطاقات الشخصيات بدقة ممتازة.",
        "إعادة مزامنة البطاقات إلى Tavern سريعة وسهلة.",
        "البحث والتجميع جعلا إدارة الشخصيات أسهل بكثير.",
      ],
      story: [
        "مخطط القصة يولد هيكل فصول واضحًا وقابلًا للاستخدام.",
        "متابعة الكتابة تحافظ على نبرة الشخصيات بشكل جيد.",
        "إعادة كتابة الفصول المتأثرة وفرت علي وقتًا كبيرًا.",
      ],
    },
  },
];

const TOPIC_LABELS: Record<string, Record<ReviewTopic, string>> = {
  "zh-CN": {
    recharge: "海外充值",
    tavern: "酒馆同步",
    story: "剧情写作",
  },
  en: {
    recharge: "Overseas Recharge",
    tavern: "Tavern Sync",
    story: "Story Writing",
  },
  ja: {
    recharge: "海外チャージ",
    tavern: "酒場同期",
    story: "物語執筆",
  },
  ko: {
    recharge: "해외 충전",
    tavern: "주점 동기화",
    story: "스토리 작성",
  },
  fr: {
    recharge: "Recharge internationale",
    tavern: "Sync Tavern",
    story: "Écriture narrative",
  },
  de: {
    recharge: "Internationale Aufladung",
    tavern: "Tavern-Sync",
    story: "Story-Schreiben",
  },
};

const seeded = (value: number): number => {
  const x = Math.sin(value * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};

const randomPick = <T>(items: T[], seed: number): T => {
  const index = Math.floor(seeded(seed) * items.length) % items.length;
  return items[Math.max(index, 0)];
};

const shuffle = <T>(items: T[]): T[] => {
  const cloned = [...items];
  for (let i = cloned.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [cloned[i], cloned[j]] = [cloned[j], cloned[i]];
  }
  return cloned;
};

const buildPraiseReviews = (): PraiseReview[] => {
  const reviews: PraiseReview[] = [];
  for (let index = 0; index < TOTAL_REVIEWS; index += 1) {
    const locale = REVIEW_LOCALES[index % REVIEW_LOCALES.length];
    const topic = randomPick(REVIEW_TOPICS, (index + 1) * 4.71);
    const message = randomPick(locale.messages[topic], (index + 1) * 7.13);
    const userBase = locale.users[index % locale.users.length];
    reviews.push({
      id: index + 1,
      user: userBase,
      country: locale.country,
      language: locale.language,
      localeCode: locale.code,
      topic,
      message,
    });
  }
  return shuffle(reviews);
};

const praiseReviews = ref<PraiseReview[]>(buildPraiseReviews());

const rowOne = computed(() => praiseReviews.value.slice(0, 50));
const rowTwo = computed(() => praiseReviews.value.slice(50));
const trackOne = computed(() => [...rowOne.value, ...rowOne.value]);
const trackTwo = computed(() => [...rowTwo.value, ...rowTwo.value]);

const topicLabel = (topic: ReviewTopic): string => {
  const locale = languageStore.currentLocale;
  const labels = TOPIC_LABELS[locale] || TOPIC_LABELS.en;
  return labels[topic];
};
</script>

<style scoped>
.global-praise {
  position: relative;
  overflow: hidden;
  border: 0;
  background: transparent;
}

.praise-shell {
  width: 100%;
  padding: 10px 10px;
}

.praise-row {
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent 0%, #000 4%, #000 96%, transparent 100%);
}

.praise-track {
  display: flex;
  width: max-content;
  gap: 10px;
}

.praise-track--left {
  animation: praise-scroll-left 280s linear infinite;
}

.praise-track--right {
  animation: praise-scroll-right 330s linear infinite;
}

.praise-row:hover .praise-track {
  animation-play-state: paused;
}

.praise-card {
  width: 340px;
  min-height: 112px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  padding: 10px 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
}

.praise-meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.praise-user {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}

.praise-locale {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  padding: 1px 8px;
  font-size: 11px;
}

.praise-message {
  margin: 7px 0;
  font-size: 12px;
  line-height: 1.4;
  color: #1e293b;
  min-height: 48px;
}

.praise-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.praise-stars {
  color: #94a3b8;
  font-size: 12px;
  letter-spacing: 0.02em;
}

.praise-topic {
  color: #334155;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  padding: 1px 8px;
}

@keyframes praise-scroll-left {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(calc(-50% - 6px));
  }
}

@keyframes praise-scroll-right {
  from {
    transform: translateX(calc(-50% - 6px));
  }
  to {
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .praise-card {
    width: 260px;
    min-height: 124px;
  }

  .praise-shell {
    padding: 8px 6px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .praise-track--left,
  .praise-track--right {
    animation: none;
  }
}
</style>
