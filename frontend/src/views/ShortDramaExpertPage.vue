<template>
  <div class="min-h-screen py-10">
    <div class="container mx-auto px-4 max-w-7xl space-y-6">
      <section class="surface-card p-5 md:p-6 space-y-2">
        <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground">
          Local Dev Only
        </p>
        <h1 class="text-2xl md:text-3xl font-bold text-foreground">短剧专家</h1>
        <p class="text-sm text-muted-foreground">
          本页仅用于本地测试：图生视频任务创建/查询 + 即梦全球化短剧 JSON 工单生成。
        </p>
      </section>

      <section class="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <article class="surface-card p-5 space-y-4">
          <h2 class="text-lg font-semibold text-foreground">任务1：创建图生视频任务</h2>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">API Key（仅本地内存，不落库）</span>
            <input
              v-model.trim="apiKey"
              type="password"
              class="field-input"
              placeholder="粘贴 Bearer Key"
            />
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">Model</span>
            <input v-model.trim="model" type="text" class="field-input" />
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">Prompt</span>
            <textarea
              v-model.trim="taskPrompt"
              rows="4"
              class="field-input"
              placeholder="英文视觉描述 + 参数"
            />
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">Image URL</span>
            <input
              v-model.trim="imageUrl"
              type="url"
              class="field-input"
              placeholder="https://..."
            />
          </label>

          <div class="flex flex-wrap items-center gap-2">
            <button
              class="action-btn action-btn-primary"
              :disabled="creatingTask"
              @click="handleCreateTask"
            >
              {{ creatingTask ? "创建中..." : "创建任务" }}
            </button>
            <span v-if="createdTaskId" class="text-xs text-emerald-600">
              任务ID：{{ createdTaskId }}
            </span>
          </div>

          <p v-if="createError" class="text-sm text-red-600 break-all">{{ createError }}</p>
          <pre v-if="createResponseText" class="json-view">{{ createResponseText }}</pre>
        </article>

        <article class="surface-card p-5 space-y-4">
          <h2 class="text-lg font-semibold text-foreground">任务1：查询任务状态</h2>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">任务ID</span>
            <input
              v-model.trim="queryTaskId"
              type="text"
              class="field-input"
              placeholder="粘贴任务ID"
            />
          </label>

          <div class="flex flex-wrap items-center gap-2">
            <button
              class="action-btn action-btn-primary"
              :disabled="queryingTask"
              @click="handleQueryTask"
            >
              {{ queryingTask ? "查询中..." : "查询任务" }}
            </button>
          </div>

          <p v-if="queryError" class="text-sm text-red-600 break-all">{{ queryError }}</p>
          <pre v-if="queryResponseText" class="json-view">{{ queryResponseText }}</pre>
        </article>
      </section>

      <section class="surface-card p-5 space-y-4">
        <h2 class="text-lg font-semibold text-foreground">任务2：即梦 API 全球化短剧专家 (V3.0)</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">目标对白语言</span>
            <input
              v-model.trim="targetLanguage"
              type="text"
              class="field-input"
              placeholder="如：中文 / English / 日本語"
            />
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">镜头数量</span>
            <input v-model.number="totalScenesInput" type="number" min="1" max="80" class="field-input" />
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">区域</span>
            <select v-model="billingRegion" class="field-input">
              <option value="cn">中国大陆（CNY）</option>
              <option value="global">海外地区（需后端汇率转换）</option>
            </select>
          </label>

          <label class="block md:col-span-2">
            <span class="block text-xs text-muted-foreground mb-1">角色锚点（英文，50字内）</span>
            <input v-model.trim="characterAnchor" type="text" class="field-input" maxlength="50" />
          </label>

          <label class="block md:col-span-2 xl:col-span-1">
            <span class="block text-xs text-muted-foreground mb-1">场景锚点（英文）</span>
            <input v-model.trim="sceneAnchor" type="text" class="field-input" />
          </label>

          <label class="block md:col-span-2 xl:col-span-3">
            <span class="block text-xs text-muted-foreground mb-1">核心动作（英文）</span>
            <input v-model.trim="actionAnchor" type="text" class="field-input" />
          </label>

          <label class="block md:col-span-2 xl:col-span-3">
            <span class="block text-xs text-muted-foreground mb-1">小说原文/剧情梗概（可选）</span>
            <textarea
              v-model.trim="storySource"
              rows="3"
              class="field-input"
              placeholder="用于附加到输出 JSON 的 source_text 字段"
            />
          </label>
        </div>

        <div class="rounded-xl border border-border bg-muted/30 p-4 text-sm">
          <p class="text-muted-foreground">报价预览（利润保底 10 元）：</p>
          <p class="mt-1 text-foreground font-semibold">
            生成费用: ¥{{ estimatedCost.toFixed(2) }} + 技术服务费: ¥10.00 = 合计: ¥{{ estimatedPrice.toFixed(2) }}
          </p>
          <p v-if="billingRegion === 'global'" class="mt-1 text-amber-600">
            当前为海外场景，后端应按实时汇率转换展示币种。
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button class="action-btn action-btn-primary" @click="generateExpertSpec">
            生成工业化 JSON
          </button>
          <button class="action-btn action-btn-ghost" @click="copySpecJson">
            复制 JSON
          </button>
          <span v-if="copyFeedback" class="text-xs text-emerald-600">{{ copyFeedback }}</span>
        </div>

        <pre class="json-view">{{ expertSpecJson }}</pre>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

const TASK_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks";
const EMOTION_TAGS = ["neutral", "happy", "sad", "angry", "fear", "surprise"] as const;

const apiKey = ref("");
const model = ref("doubao-seedance-1-5-pro-251215");
const taskPrompt = ref(
  "Fast FPV drone rushes through complex obstacles and natural wonders, immersive flight experience --duration 5 --camerafixed false --watermark true",
);
const imageUrl = ref("https://ark-project.tos-cn-beijing.volces.com/doc_image/seepro_i2v.png");
const createdTaskId = ref("");
const queryTaskId = ref("");

const creatingTask = ref(false);
const queryingTask = ref(false);
const createError = ref("");
const queryError = ref("");
const createResponseText = ref("");
const queryResponseText = ref("");

const totalScenesInput = ref(8);
const targetLanguage = ref("中文");
const billingRegion = ref<"cn" | "global">("cn");
const characterAnchor = ref("Young female swordswoman with black ponytail, red hanfu, determined eyes");
const sceneAnchor = ref("Ancient Chinese palace, sunset glow, cinematic fog");
const actionAnchor = ref("She walks through the corridor, stops, then turns to camera");
const storySource = ref("");
const expertSpecJson = ref("");
const copyFeedback = ref("");

const totalScenes = computed(() => {
  const raw = Number(totalScenesInput.value);
  if (!Number.isFinite(raw)) return 1;
  return Math.min(80, Math.max(1, Math.round(raw)));
});

const estimatedCost = computed(() => {
  const rawCost = totalScenes.value * 1.5 + 0.8;
  return Math.round(rawCost * 100) / 100;
});

const estimatedPrice = computed(() => {
  return Math.round((estimatedCost.value + 10) * 100) / 100;
});

const safeJsonStringify = (data: unknown): string => {
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data ?? "");
  }
};

const parseJsonMaybe = (rawText: string): unknown => {
  const text = String(rawText || "").trim();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
};

const pickTaskId = (payload: any): string => {
  const candidates = [
    payload?.id,
    payload?.task_id,
    payload?.data?.id,
    payload?.data?.task_id,
    payload?.result?.id,
    payload?.result?.task_id,
  ];
  const matched = candidates.find((value) => typeof value === "string" && value.trim());
  return matched ? String(matched).trim() : "";
};

const buildHeaders = (): HeadersInit => {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey.value.trim()}`,
  };
};

const assertApiKey = () => {
  if (!apiKey.value.trim()) {
    throw new Error("请先输入 API Key");
  }
};

const handleCreateTask = async () => {
  createError.value = "";
  createResponseText.value = "";
  try {
    assertApiKey();
    creatingTask.value = true;

    const payload = {
      model: model.value.trim(),
      content: [
        {
          type: "text",
          text: taskPrompt.value.trim(),
        },
        {
          type: "image_url",
          image_url: {
            url: imageUrl.value.trim(),
          },
        },
      ],
    };

    const response = await fetch(TASK_ENDPOINT, {
      method: "POST",
      headers: buildHeaders(),
      body: JSON.stringify(payload),
    });
    const rawText = await response.text();
    const data = parseJsonMaybe(rawText);

    if (!response.ok) {
      throw new Error(`创建失败(${response.status}): ${safeJsonStringify(data).slice(0, 500)}`);
    }

    createResponseText.value = safeJsonStringify(data);
    const taskId = pickTaskId(data);
    if (taskId) {
      createdTaskId.value = taskId;
      queryTaskId.value = taskId;
    }
  } catch (error: any) {
    createError.value = String(error?.message || error || "创建任务失败");
  } finally {
    creatingTask.value = false;
  }
};

const handleQueryTask = async () => {
  queryError.value = "";
  queryResponseText.value = "";
  try {
    assertApiKey();
    const taskId = queryTaskId.value.trim();
    if (!taskId) throw new Error("请先输入任务ID");

    queryingTask.value = true;
    const response = await fetch(`${TASK_ENDPOINT}/${encodeURIComponent(taskId)}`, {
      method: "GET",
      headers: buildHeaders(),
    });
    const rawText = await response.text();
    const data = parseJsonMaybe(rawText);

    if (!response.ok) {
      throw new Error(`查询失败(${response.status}): ${safeJsonStringify(data).slice(0, 500)}`);
    }

    queryResponseText.value = safeJsonStringify(data);
  } catch (error: any) {
    queryError.value = String(error?.message || error || "查询任务失败");
  } finally {
    queryingTask.value = false;
  }
};

const resolveVoiceHint = (language: string): string => {
  const token = String(language || "").trim().toLowerCase();
  if (token.includes("english") || token === "en" || token.includes("英语")) return "voice_en_female_01";
  if (token.includes("japanese") || token === "ja" || token.includes("日语")) return "voice_ja_female_01";
  if (token.includes("korean") || token === "ko" || token.includes("韩语")) return "voice_ko_female_01";
  if (token.includes("thai") || token === "th" || token.includes("泰语")) return "voice_th_female_01";
  if (token.includes("vietnamese") || token === "vi" || token.includes("越南")) return "voice_vi_female_01";
  if (token.includes("french") || token === "fr" || token.includes("法语")) return "voice_fr_female_01";
  if (token.includes("german") || token === "de" || token.includes("德语")) return "voice_de_female_01";
  return "voice_zh_female_01";
};

const buildVisualPrompt = (sceneIndex: number): string => {
  const shotType = sceneIndex % 2 === 0 ? "slow dolly-in" : "tracking shot";
  return `${characterAnchor.value}. ${actionAnchor.value}. ${sceneAnchor.value}. cinematic lighting, volumetric atmosphere, ${shotType}, high detail`;
};

const generateExpertSpec = () => {
  const steps = Array.from({ length: totalScenes.value }, (_, index) => {
    const stepNo = index + 1;
    return {
      scene_no: stepNo,
      duration_seconds: 5,
      emotion_tag: EMOTION_TAGS[index % EMOTION_TAGS.length],
      visual_prompt: buildVisualPrompt(index),
      dialogue: `[${targetLanguage.value}] Scene ${stepNo} dialogue placeholder`,
      api_params: {
        strong_consistency_mode: true,
        ref_image: "{{character_assets.lead_1.seed_image_url}}",
      },
    };
  });

  const payload = {
    workflow_version: "short_drama_expert_v3.0",
    target_language: targetLanguage.value || "中文",
    visual_prompt_language: "English",
    story_source_text: storySource.value || "",
    scene_anchor: sceneAnchor.value,
    character_assets: [
      {
        character_id: "lead_1",
        appearance_anchor: characterAnchor.value.slice(0, 50),
        seed_image_url: "{{auto_or_uploaded_seed_image_url}}",
      },
    ],
    api_defaults: {
      duration_seconds: "3-8s (default 5s)",
      strong_consistency_mode: true,
      emotion_tag_whitelist: [...EMOTION_TAGS],
    },
    pricing: {
      currency: "CNY",
      formulas: {
        cost: "(total_scenes * 1.5) + 0.8",
        user_price: "cost + 10.0",
      },
      total_scenes: totalScenes.value,
      generation_cost: estimatedCost.value,
      service_fee: 10,
      total_quote: estimatedPrice.value,
      region_hint:
        billingRegion.value === "global"
          ? "Non-mainland locale: backend should apply realtime exchange-rate conversion."
          : "Mainland locale: direct CNY quote.",
    },
    voice_recommendation: {
      target_language: targetLanguage.value,
      suggested_voice_id: resolveVoiceHint(targetLanguage.value),
      backend_note: "Map target_language to actual voice_id in DB automatically.",
    },
    production_steps: steps,
    backend_integration_notes: [
      "If no uploaded seed image exists, generate one via Text-to-Image first and reuse as ref_image.",
      "Always reuse appearance_anchor + scene_anchor for every shot to lock character and environment.",
      "Pricing UI should display: generation cost + service fee(10 CNY).",
    ],
  };

  expertSpecJson.value = safeJsonStringify(payload);
};

const copySpecJson = async () => {
  copyFeedback.value = "";
  try {
    await navigator.clipboard.writeText(expertSpecJson.value);
    copyFeedback.value = "已复制";
    window.setTimeout(() => {
      copyFeedback.value = "";
    }, 1600);
  } catch (error) {
    copyFeedback.value = "复制失败";
    console.error(error);
  }
};

onMounted(() => {
  generateExpertSpec();
});
</script>

<style scoped>
.field-input {
  width: 100%;
  min-height: 40px;
  padding: 0.55rem 0.75rem;
  border-radius: 0.65rem;
  border: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  color: hsl(var(--foreground));
  outline: none;
}

.field-input:focus {
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 3px hsl(var(--primary) / 0.15);
}

.action-btn {
  border-radius: 0.6rem;
  padding: 0.5rem 0.9rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn-primary {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.action-btn-primary:hover:not(:disabled) {
  background: hsl(var(--primary) / 0.92);
}

.action-btn-ghost {
  border: 1px solid hsl(var(--border));
  color: hsl(var(--foreground));
  background: hsl(var(--card));
}

.action-btn-ghost:hover:not(:disabled) {
  background: hsl(var(--muted));
}

.json-view {
  margin: 0;
  max-height: 360px;
  overflow: auto;
  padding: 0.85rem;
  border-radius: 0.75rem;
  border: 1px solid hsl(var(--border));
  background: hsl(var(--muted) / 0.4);
  color: hsl(var(--foreground));
  font-size: 0.75rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
