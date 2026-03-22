<template>
  <div class="novel-galaxy min-h-[calc(100vh-64px)] bg-slate-50 text-slate-900">
    <div class="novel-galaxy-inner container mx-auto px-4 py-8 space-y-5">
      <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h1 class="text-2xl font-bold">{{ t("novelStoryPage.title") }}</h1>
        <p class="text-sm text-slate-600 mt-1">
          {{ t("novelStoryPage.intro") }}
        </p>
        <div class="mt-3 inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1 text-sm">
          <button class="px-3 py-1.5 rounded" :class="tab === 'creation' ? 'bg-white shadow' : ''" @click="tab = 'creation'">{{ t("novelStoryPage.tabs.creation") }}</button>
          <button class="px-3 py-1.5 rounded" :class="tab === 'works' ? 'bg-white shadow' : ''" @click="tab = 'works'">{{ t("novelStoryPage.tabs.works") }}</button>
          <button class="px-3 py-1.5 rounded" :class="tab === 'sync' ? 'bg-white shadow' : ''" @click="tab = 'sync'">{{ t("novelStoryPage.tabs.sync") }}</button>
        </div>
      </section>

      <section v-if="tab === 'creation'" class="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div class="rounded-xl border bg-white p-4 space-y-3 transition-colors" :class="creationMode === 'professional' ? 'border-indigo-200' : 'border-emerald-200'">
          <div class="rounded-lg border p-2.5 transition-colors" :class="creationMode === 'professional' ? 'border-indigo-200 bg-indigo-50/70' : 'border-emerald-200 bg-emerald-50/70'">
            <div class="flex items-center justify-between gap-2 mb-2">
              <div class="text-xs font-semibold" :class="creationMode === 'professional' ? 'text-indigo-700' : 'text-emerald-700'">{{ t("novelStoryPage.creation.modeTitle") }}</div>
              <span class="text-[11px] px-2 py-0.5 rounded border"
                :class="creationMode === 'professional' ? 'border-indigo-300 text-indigo-700 bg-white' : 'border-emerald-300 text-emerald-700 bg-white'"
              >
                {{ t("novelStoryPage.creation.currentLabel") }}{{ creationMode === 'professional' ? t("novelStoryPage.creation.professional") : t("novelStoryPage.creation.light") }}
              </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                class="text-left rounded-lg border p-2 transition-colors"
                :class="creationMode === 'professional' ? 'border-indigo-500 bg-indigo-600 text-white' : 'border-indigo-200 bg-white text-indigo-700 hover:bg-indigo-50'"
                @click="creationMode = 'professional'"
              >
                <div class="text-xs font-semibold">{{ t("novelStoryPage.creation.professional") }}</div>
                <div class="text-[11px] mt-1 opacity-90">{{ t("novelStoryPage.creation.professionalDesc") }}</div>
                <div class="text-[11px] mt-1.5 leading-5">
                  {{ t("novelStoryPage.creation.professionalFlow") }}
                </div>
              </button>

              <button
                class="text-left rounded-lg border p-2 transition-colors"
                :class="creationMode === 'light' ? 'border-emerald-500 bg-emerald-600 text-white' : 'border-emerald-200 bg-white text-emerald-700 hover:bg-emerald-50'"
                @click="creationMode = 'light'"
              >
                <div class="text-xs font-semibold">{{ t("novelStoryPage.creation.light") }}</div>
                <div class="text-[11px] mt-1 opacity-90">{{ t("novelStoryPage.creation.lightDesc") }}</div>
                <div class="text-[11px] mt-1.5 leading-5">
                  {{ t("novelStoryPage.creation.lightFlow") }}
                </div>
              </button>
            </div>

            <p class="text-[11px] mt-2" :class="creationMode === 'professional' ? 'text-indigo-700' : 'text-emerald-700'">
              {{ creationMode === 'professional' ? t("novelStoryPage.creation.professionalHint") : t("novelStoryPage.creation.lightHint") }}
            </p>
          </div>

          <div>
            <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.ideaLabel") }}</label>
            <textarea v-model="idea" class="w-full h-24 mt-1 rounded border border-slate-200 px-3 py-2 text-sm resize-none"></textarea>
          </div>
          <div>
            <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.genreLabel") }}</label>
            <input v-model="genre" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.toneLabel") }}</label>
            <input v-model="tone" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.chapterCountLabel") }}</label>
            <input v-model.number="chapterCount" type="number" min="1" max="24" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.settingLabel") }}</label>
            <textarea v-model="setting" class="w-full h-20 mt-1 rounded border border-slate-200 px-3 py-2 text-sm resize-none"></textarea>
          </div>
          <div class="flex flex-wrap gap-2 pt-1">
            <button
              class="px-3 py-2 rounded text-white text-sm disabled:opacity-60"
              :class="creationMode === 'professional' ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-emerald-600 hover:bg-emerald-700'"
              :disabled="workshopLoading"
              @click="generatePlan"
            >
              {{ workshopLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.creation.generatePlan") }}
            </button>
            <button
              class="px-3 py-2 rounded border text-sm disabled:opacity-60"
              :class="creationMode === 'professional' ? 'border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50' : 'border-emerald-300 text-emerald-700 bg-white hover:bg-emerald-50'"
              :disabled="outlineLoading || !plan"
              @click="refinePlanOutlines"
            >
              {{ outlineLoading ? t("novelStoryPage.creation.optimizing") : creationMode === 'professional' ? t("novelStoryPage.creation.refineOutline") : t("novelStoryPage.creation.refineTitle") }}
            </button>
            <button
              class="px-3 py-2 rounded border text-sm"
              :class="creationMode === 'professional' ? 'border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50' : 'border-emerald-300 text-emerald-700 bg-white hover:bg-emerald-50'"
              @click="syncPlanToRoleplay"
              :disabled="!plan"
            >
              {{ t("novelStoryPage.creation.syncToTavern") }}
            </button>
          </div>
          <p v-if="workshopError" class="text-xs text-rose-600">{{ workshopError }}</p>
          <p class="text-xs text-slate-500">{{ t("novelStoryPage.creation.apiHint") }}</p>
          <p class="text-xs text-slate-500">{{ t("novelStoryPage.creation.autoSaveHint") }}</p>
          <p v-if="draftLoading" class="text-xs text-slate-500">{{ t("novelStoryPage.creation.loadingDraft") }}</p>
          <p v-else-if="draftSaving" class="text-xs text-slate-500">{{ t("novelStoryPage.creation.savingDraft") }}</p>
          <div class="pt-1">
            <button
              class="px-2.5 py-1.5 rounded border border-rose-200 text-rose-600 text-xs disabled:opacity-60"
              :disabled="draftLoading || draftSaving || workshopLoading || outlineLoading || chapterLoading || worksSaving || imageLoading || tavernImportGenerating"
              @click="clearDraftOneClick"
            >
              {{ t("novelStoryPage.creation.clearDraft") }}
            </button>
          </div>
          <p v-if="draftError" class="text-xs text-rose-600">{{ draftError }}</p>
          <p v-if="draftInfo" class="text-xs text-emerald-700">{{ draftInfo }}</p>

          <div class="border-t border-slate-200 pt-3 space-y-2">
            <h3 class="text-sm font-semibold">{{ t("novelStoryPage.creation.workArchiveTitle") }}</h3>
            <div class="flex flex-wrap gap-2">
              <button class="px-2.5 py-1.5 rounded bg-slate-900 text-white text-xs disabled:opacity-60" :disabled="worksSaving" @click="saveAsSerialDraft">
                {{ worksSaving ? t("novelStoryPage.creation.saving") : t("novelStoryPage.creation.saveSerial") }}
              </button>
              <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="chapterLoading || worksSaving" @click="completeBook">
                {{ chapterLoading ? t("novelStoryPage.creation.processing") : t("novelStoryPage.creation.completeAndSave") }}
              </button>
              <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="worksSaving" @click="saveAsNewWork">
                {{ worksSaving ? t("novelStoryPage.creation.saving") : t("novelStoryPage.creation.saveAsNewWork") }}
              </button>
              <button
                v-if="selectedWorkId"
                class="px-2.5 py-1.5 rounded border border-indigo-300 text-indigo-700 bg-indigo-50 text-xs disabled:opacity-60"
                :disabled="worksSaving"
                @click="saveCurrentWork({ successMessage: t('novelStoryPage.creation.currentWorkUpdated') })"
              >
                {{ worksSaving ? t("novelStoryPage.creation.saving") : t("novelStoryPage.creation.updateCurrentWork") }}
              </button>
              <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs" @click="startNewWork">{{ t("novelStoryPage.creation.newWork") }}</button>
              <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs" @click="tab = 'works'">{{ t("novelStoryPage.creation.gotoWorks") }}</button>
            </div>
            <p v-if="worksError" class="text-xs text-rose-600">{{ worksError }}</p>
            <p v-if="worksInfo" class="text-xs text-emerald-700">{{ worksInfo }}</p>
            <p class="text-xs" :class="bookStatus === 'completed' ? 'text-emerald-700' : 'text-slate-500'">
              {{ t("novelStoryPage.creation.currentStatus") }}{{ bookStatus === 'completed' ? t("novelStoryPage.creation.statusCompleted") : t("novelStoryPage.creation.statusSerial") }}
            </p>
            <p v-if="selectedWork" class="text-xs text-slate-500">
              {{ t("novelStoryPage.creation.currentWork") }}{{ selectedWork.title || t("novelStoryPage.creation.untitledWork") }}（{{ selectedWork.chapters.length }} {{ t("novelStoryPage.creation.chapterUnit") }}）
            </p>
          </div>

          <div class="border-t border-slate-200 pt-3 space-y-2">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-semibold">{{ t("novelStoryPage.creation.charactersTitle") }}</h3>
              <button class="px-2 py-1 rounded border border-slate-300 text-[11px]" @click="addCharacter">{{ t("novelStoryPage.creation.addCharacter") }}</button>
            </div>
            <div class="grid grid-cols-2 gap-1.5 max-h-28 overflow-auto">
              <button
                v-for="c in characters"
                :key="`creation_${c.id}`"
                class="text-left rounded border px-2 py-1 text-xs truncate"
                :class="activeId === c.id ? 'border-slate-900 bg-slate-100' : 'border-slate-200'"
                @click="activeId = c.id"
              >
                {{ c.name || t("novelStoryPage.creation.untitledCharacter") }}
              </button>
            </div>
            <div v-if="activeChar" class="space-y-1">
              <input v-model="activeChar.name" class="w-full rounded border border-slate-200 px-2 py-1.5 text-xs" :placeholder="t('novelStoryPage.creation.characterNamePlaceholder')" />
              <input v-model="activeChar.role" class="w-full rounded border border-slate-200 px-2 py-1.5 text-xs" :placeholder="t('novelStoryPage.creation.characterRolePlaceholder')" />
              <textarea v-model="activeChar.personality" class="w-full h-14 rounded border border-slate-200 px-2 py-1.5 text-xs resize-none" :placeholder="t('novelStoryPage.creation.characterPersonalityPlaceholder')"></textarea>
              <button class="w-full px-2 py-1.5 rounded border border-rose-200 text-rose-600 text-xs disabled:opacity-40" :disabled="characters.length <= 1" @click="removeCharacter">
                {{ t("novelStoryPage.creation.removeCurrentCharacter") }}
              </button>
            </div>
          </div>

          <div class="border-t border-slate-200 pt-3 space-y-2">
            <h3 class="text-sm font-semibold">{{ t("novelStoryPage.creation.aiImagesTitle") }}</h3>
            <p class="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1">
              {{ t("novelStoryPage.creation.complianceNotice") }}
            </p>
            <div class="space-y-1">
              <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.coverPromptLabel") }}</label>
              <textarea
                v-model="coverPrompt"
                class="w-full h-16 rounded border border-slate-200 px-2 py-1.5 text-xs resize-none"
                :placeholder="t('novelStoryPage.creation.coverPromptPlaceholder')"
              ></textarea>
              <div class="flex flex-wrap gap-1.5">
                <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="imageLoading || isUploadingCustomImage" @click="generateCoverImage">
                  {{ imageLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.creation.generateAICover") }}
                </button>
                <button class="px-2.5 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50 text-xs disabled:opacity-60" :disabled="imageLoading || isUploadingCustomImage" @click="openCreationCoverUploadPicker">
                  {{ isUploadingCustomImage ? t("novelStoryPage.creation.reviewUploading") : t("novelStoryPage.creation.uploadCustomCover") }}
                </button>
              </div>
              <input ref="creationCoverUploadInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="handleCreationCoverUpload" />
              <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60 hidden" :disabled="imageLoading" @click="generateCoverImage">
                {{ imageLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.creation.generateAICover") }}
              </button>
              <img v-if="coverImage" :src="coverImage" :alt="t('novelStoryPage.creation.aiCoverAlt')" class="w-full h-32 object-cover rounded border border-slate-200" />
            </div>

            <div class="space-y-1">
              <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.characterImageLabel") }}</label>
              <select v-model="characterImageTargetId" class="w-full rounded border border-slate-200 px-2 py-1.5 text-xs">
                <option value="">{{ t("novelStoryPage.creation.selectCharacter") }}</option>
                <option v-for="c in characters" :key="c.id" :value="c.id">{{ c.name || t("novelStoryPage.creation.untitledCharacter") }}</option>
              </select>
              <textarea
                v-model="characterImagePrompt"
                class="w-full h-14 rounded border border-slate-200 px-2 py-1.5 text-xs resize-none"
                :placeholder="t('novelStoryPage.creation.characterImagePromptPlaceholder')"
              ></textarea>
              <div class="flex flex-wrap gap-1.5">
                <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="imageLoading || isUploadingCustomImage" @click="generateCharacterImage">
                  {{ imageLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.creation.generateAICharacterImage") }}
                </button>
                <button class="px-2.5 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50 text-xs disabled:opacity-60" :disabled="imageLoading || isUploadingCustomImage" @click="openCreationCharacterUploadPicker">
                  {{ isUploadingCustomImage ? t("novelStoryPage.creation.reviewUploading") : t("novelStoryPage.creation.uploadCustomCharacterImage") }}
                </button>
              </div>
              <input ref="creationCharacterUploadInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="handleCreationCharacterUpload" />
              <div class="grid grid-cols-2 gap-2 max-h-40 overflow-auto">
                <div v-for="img in characterImages" :key="img.id" class="rounded border border-slate-200 p-1">
                  <img :src="img.image_url" :alt="img.character_name || t('novelStoryPage.creation.characterImageAlt')" class="w-full h-20 object-cover rounded" />
                  <p class="mt-1 text-[11px] text-slate-600 truncate">{{ img.character_name || t("novelStoryPage.creation.characterImageAlt") }}</p>
                </div>
              </div>
            </div>

            <div class="space-y-1">
              <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.chapterImageLabel") }}</label>
              <textarea
                v-model="chapterImagePrompt"
                class="w-full h-14 rounded border border-slate-200 px-2 py-1.5 text-xs resize-none"
                :placeholder="t('novelStoryPage.creation.chapterImagePromptPlaceholder')"
              ></textarea>
              <div class="flex flex-wrap gap-1.5">
                <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="imageLoading || isUploadingCustomImage" @click="generateChapterImage">
                  {{ imageLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.creation.generateChapterImage", { no: activeChapterNo }) }}
                </button>
                <button class="px-2.5 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50 text-xs disabled:opacity-60" :disabled="imageLoading || isUploadingCustomImage" @click="openCreationChapterUploadPicker">
                  {{ isUploadingCustomImage ? t("novelStoryPage.creation.reviewUploading") : t("novelStoryPage.creation.uploadChapterImage", { no: activeChapterNo }) }}
                </button>
              </div>
              <input ref="creationChapterUploadInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="handleCreationChapterUpload" />
              <div class="grid grid-cols-2 gap-2 max-h-40 overflow-auto">
                <div v-for="img in chapterImages" :key="img.id" class="rounded border border-slate-200 p-1">
                  <img :src="img.image_url" :alt="img.chapter_title || t('novelStoryPage.creation.chapterImageAlt')" class="w-full h-20 object-cover rounded" />
                  <p class="mt-1 text-[11px] text-slate-600 truncate">{{ t("novelStoryPage.creation.chapterPrefix", { no: img.chapter_no }) }} {{ img.chapter_title }}</p>
                </div>
              </div>
            </div>
            <p v-if="imageError" class="text-xs text-rose-600">{{ imageError }}</p>
            <p v-if="imageInfo" class="text-xs text-emerald-700">{{ imageInfo }}</p>
          </div>
        </div>

        <div class="xl:col-span-2 rounded-xl border bg-white p-4 space-y-4 transition-colors" :class="creationMode === 'professional' ? 'border-indigo-200 bg-indigo-50/20' : 'border-emerald-200 bg-emerald-50/20'">
          <div class="rounded-lg border px-3 py-2.5" :class="creationMode === 'professional' ? 'border-indigo-200 bg-indigo-50' : 'border-emerald-200 bg-emerald-50'">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h2 class="text-lg font-semibold" :class="creationMode === 'professional' ? 'text-indigo-800' : 'text-emerald-800'">
                {{ creationMode === 'professional' ? t("novelStoryPage.creation.professionalWorkspace") : t("novelStoryPage.creation.lightWorkspace") }}
              </h2>
              <div class="text-xs px-2 py-1 rounded border"
                :class="creationMode === 'professional' ? 'border-indigo-300 text-indigo-700 bg-white' : 'border-emerald-300 text-emerald-700 bg-white'"
              >
                {{ creationMode === 'professional' ? t("novelStoryPage.creation.chapterRefineMode") : t("novelStoryPage.creation.batchMode") }}
              </div>
            </div>
            <p class="text-xs mt-1.5" :class="creationMode === 'professional' ? 'text-indigo-700' : 'text-emerald-700'">
              {{ creationMode === 'professional'
                ? t("novelStoryPage.creation.professionalWorkspaceDesc")
                : t("novelStoryPage.creation.lightWorkspaceDesc") }}
            </p>
          </div>
          <div v-if="!plan" class="text-sm text-slate-500 mt-3">{{ t("novelStoryPage.creation.noResult") }}</div>
          <div v-else class="space-y-3 text-sm">
            <div><b>{{ t("novelStoryPage.creation.titleLabel") }}</b>{{ plan.title }}</div>
            <div><b>{{ t("novelStoryPage.creation.genreToneLabel") }}</b>{{ plan.genre || t("novelStoryPage.creation.notFilled") }} / {{ plan.tone || t("novelStoryPage.creation.notFilled") }}</div>
            <div><b>{{ t("novelStoryPage.creation.coreConflictLabel") }}</b>{{ plan.core_conflict || t("novelStoryPage.creation.notFilled") }}</div>
            <div><b>{{ t("novelStoryPage.creation.characterCountLabel") }}</b>{{ plan.characters.length }}</div>
            <div><b>{{ t("novelStoryPage.creation.chapterCountStatsLabel") }}</b>{{ plan.chapter_outlines.length }}</div>

            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 space-y-3">
              <h3 class="text-sm font-semibold text-slate-800">{{ t("novelStoryPage.creation.storyBlueprint") }}</h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div class="rounded-lg border border-slate-200 bg-white px-2 py-2">
                  <p class="text-[11px] text-slate-500">{{ t("novelStoryPage.creation.genreLabel") }}</p>
                  <p class="text-xs font-medium text-slate-800 mt-1">{{ plan.genre || t("novelStoryPage.creation.notSet") }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white px-2 py-2">
                  <p class="text-[11px] text-slate-500">{{ t("novelStoryPage.creation.toneLabel") }}</p>
                  <p class="text-xs font-medium text-slate-800 mt-1">{{ plan.tone || t("novelStoryPage.creation.notSet") }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white px-2 py-2">
                  <p class="text-[11px] text-slate-500">{{ t("novelStoryPage.creation.characterCount") }}</p>
                  <p class="text-xs font-medium text-slate-800 mt-1">{{ plan.characters.length }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white px-2 py-2">
                  <p class="text-[11px] text-slate-500">{{ t("novelStoryPage.creation.chapterCount") }}</p>
                  <p class="text-xs font-medium text-slate-800 mt-1">{{ plan.chapter_outlines.length }}</p>
                </div>
              </div>

              <div v-if="plan.setting" class="rounded-lg border border-slate-200 bg-white px-3 py-2">
                <p class="text-[11px] text-slate-500">{{ t("novelStoryPage.creation.settingLabel") }}</p>
                <p class="text-xs text-slate-700 mt-1 whitespace-pre-wrap break-words">{{ plan.setting }}</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="rounded-lg border border-slate-200 bg-white p-2">
                  <p class="text-[11px] text-slate-500 mb-1">{{ t("novelStoryPage.creation.mainCharacters") }}</p>
                  <div v-if="plan.characters.length === 0" class="text-xs text-slate-500">{{ t("novelStoryPage.creation.noCharacterSetting") }}</div>
                  <div v-else class="space-y-1 max-h-48 overflow-auto">
                    <div v-for="(c, idx) in plan.characters" :key="`${c.name}_${idx}`" class="rounded border border-slate-200 bg-slate-50 px-2 py-1.5">
                      <p class="text-xs font-medium text-slate-800">{{ c.name || t("novelStoryPage.creation.characterFallbackName", { index: idx + 1 }) }}</p>
                      <p class="text-[11px] text-slate-600 mt-0.5">{{ t("novelStoryPage.creation.identityLabel") }}{{ c.role || t("novelStoryPage.creation.notSet") }}</p>
                      <p v-if="c.goal" class="text-[11px] text-slate-600 mt-0.5">{{ t("novelStoryPage.creation.goalLabel") }}{{ compactText(c.goal, 60) }}</p>
                    </div>
                  </div>
                </div>

                <div class="rounded-lg border border-slate-200 bg-white p-2">
                  <p class="text-[11px] text-slate-500 mb-1">{{ t("novelStoryPage.creation.chapterRoadmap") }}</p>
                  <div v-if="plan.chapter_outlines.length === 0" class="text-xs text-slate-500">{{ t("novelStoryPage.creation.noChapterPlan") }}</div>
                  <div v-else class="space-y-1 max-h-48 overflow-auto">
                    <div v-for="outline in plan.chapter_outlines" :key="outline.chapter_no" class="rounded border border-slate-200 bg-slate-50 px-2 py-1.5">
                      <p class="text-xs font-medium text-slate-800">{{ t("novelStoryPage.creation.chapterPrefix", { no: outline.chapter_no }) }} · {{ outline.title || t("novelStoryPage.creation.chapterDefaultTitle", { no: outline.chapter_no }) }}</p>
                      <p class="text-[11px] text-slate-600 mt-0.5">{{ compactText(outline.summary || t("novelStoryPage.creation.noSummary"), 72) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="border-t pt-4 space-y-3" :class="creationMode === 'professional' ? 'border-indigo-200' : 'border-emerald-200'">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h3 class="font-semibold">{{ t("novelStoryPage.creation.chapterWriterTitle") }}</h3>
              <div class="text-xs px-2 py-1 rounded border" :class="bookStatus === 'completed' ? 'border-emerald-300 text-emerald-700 bg-emerald-50' : 'border-slate-300 text-slate-600 bg-slate-50'">
                {{ bookStatus === 'completed' ? t("novelStoryPage.creation.statusCompleted") : t("novelStoryPage.creation.statusSerial") }}
              </div>
            </div>
            <div v-if="!plan" class="text-sm text-slate-500">{{ t("novelStoryPage.creation.generatePlanBeforeWriting") }}</div>
            <div v-else class="space-y-3">
              <div v-if="characterImpactPending" class="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800 space-y-2">
                <p>{{ characterImpactMessage || t("novelStoryPage.creation.characterImpactPrompt") }}</p>
                <div class="flex flex-wrap gap-2">
                  <button class="px-2.5 py-1.5 rounded border border-amber-300 bg-white disabled:opacity-60" :disabled="chapterLoading" @click="regenerateImpactedChapters">
                    {{ chapterLoading ? t("novelStoryPage.creation.processing") : t("novelStoryPage.creation.autoUpdateImpacted") }}
                  </button>
                  <button class="px-2.5 py-1.5 rounded border border-amber-300 bg-white" @click="acceptCharacterChangesWithoutRewrite">
                    {{ t("novelStoryPage.creation.keepCurrentCharacters") }}
                  </button>
                </div>
              </div>

              <div>
                <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.continuationHintLabel") }}</label>
                <textarea
                  v-model="continuationHint"
                  class="w-full h-20 mt-1 rounded border border-slate-200 px-3 py-2 text-sm resize-none"
                  :placeholder="t('novelStoryPage.creation.continuationHintPlaceholder')"
                ></textarea>
              </div>

              <div v-if="creationMode === 'professional'" class="space-y-3 rounded-lg border border-indigo-200 bg-indigo-50/60 p-3">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <div>
                    <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.targetChapterLabel") }}</label>
                    <select v-model.number="activeChapterNo" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm">
                      <option v-for="outline in plan.chapter_outlines" :key="outline.chapter_no" :value="outline.chapter_no">
                        {{ t("novelStoryPage.creation.chapterPrefix", { no: outline.chapter_no }) }} - {{ outline.title || t("novelStoryPage.creation.chapterDefaultTitle", { no: outline.chapter_no }) }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.targetWordsLabel") }}</label>
                    <input v-model.number="targetWords" type="number" min="600" max="5000" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
                  </div>
                  <div class="flex items-end">
                    <button class="w-full px-3 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm disabled:opacity-60" :disabled="chapterLoading" @click="generateChapter(activeChapterNo)">
                      {{ chapterLoading ? t("novelStoryPage.creation.writing") : t("novelStoryPage.creation.generateCurrentChapter") }}
                    </button>
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button class="px-3 py-2 rounded border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100 text-sm disabled:opacity-60" :disabled="chapterLoading" @click="generateNextChapter">
                    {{ chapterLoading ? t("novelStoryPage.creation.writing") : t("novelStoryPage.creation.generateNextChapter") }}
                  </button>
                  <button class="px-3 py-2 rounded border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100 text-sm disabled:opacity-60" :disabled="chapterLoading" @click="continueCurrentChapter">
                    {{ chapterLoading ? t("novelStoryPage.creation.continuing") : t("novelStoryPage.creation.continueCurrentChapter") }}
                  </button>
                </div>
              </div>

              <div v-else class="space-y-3 rounded-lg border border-emerald-200 bg-emerald-50/60 p-3">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <div>
                    <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.oneClickChapterCountLabel") }}</label>
                    <input v-model.number="chapterCount" type="number" min="1" max="24" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
                  </div>
                  <div>
                    <label class="text-xs text-slate-600">{{ t("novelStoryPage.creation.lightContinuationCountLabel") }}</label>
                    <input v-model.number="lightContinuationCount" type="number" min="1" max="12" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
                  </div>
                  <div class="flex items-end">
                    <button class="w-full px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm disabled:opacity-60" :disabled="chapterLoading" @click="generateAllChaptersLight">
                      {{ chapterLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.creation.oneClickGenerate") }}
                    </button>
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button class="px-3 py-2 rounded border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100 text-sm disabled:opacity-60" :disabled="chapterLoading" @click="continueByLightBatch">
                    {{ chapterLoading ? t("novelStoryPage.creation.continuing") : t("novelStoryPage.creation.oneClickContinue", { count: lightContinuationCount }) }}
                  </button>
                </div>
              </div>

              <div class="flex flex-wrap gap-2">
                <button
                  class="px-3 py-2 rounded text-sm disabled:opacity-60"
                  :class="creationMode === 'professional' ? 'border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100' : 'border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100'"
                  :disabled="chapterHistory.length === 0 || chapterLoading"
                  @click="rollbackChapterGeneration"
                >
                  {{ t("novelStoryPage.creation.rollbackRecent") }}
                </button>
                <button
                  class="px-3 py-2 rounded text-sm disabled:opacity-60"
                  :class="creationMode === 'professional' ? 'border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100' : 'border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100'"
                  :disabled="chapterLoading || !chapterByNo(activeChapterNo)"
                  @click="deleteCurrentChapter"
                >
                  {{ t("novelStoryPage.creation.deleteCurrentChapter") }}
                </button>
                <button
                  class="px-3 py-2 rounded text-sm disabled:opacity-60"
                  :class="creationMode === 'professional' ? 'border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100' : 'border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100'"
                  :disabled="chapterLoading || chapters.length === 0"
                  @click="deleteLastChapter"
                >
                  {{ t("novelStoryPage.creation.deleteLastChapter") }}
                </button>
                <button
                  class="px-3 py-2 rounded text-sm disabled:opacity-60"
                  :class="creationMode === 'professional' ? 'border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100' : 'border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100'"
                  :disabled="chapterLoading || !chapterByNo(activeChapterNo)"
                  @click="trimCurrentChapterContent"
                >
                  {{ t("novelStoryPage.creation.trimCurrentChapter") }}
                </button>
                <button
                  class="px-3 py-2 rounded text-sm disabled:opacity-60"
                  :class="creationMode === 'professional' ? 'border border-indigo-300 bg-white text-indigo-700 hover:bg-indigo-100' : 'border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100'"
                  :disabled="chapterLoading || chapters.length === 0"
                  @click="copyAllChapters"
                >
                  {{ tr('复制整本草稿', 'Copy Full Draft') }}
                </button>
              </div>

              <p v-if="chapterError" class="text-xs text-rose-600">{{ chapterError }}</p>
              <p v-if="chapterInfo" class="text-xs text-emerald-700">{{ chapterInfo }}</p>

              <div class="space-y-3 max-h-[560px] overflow-auto">
                <div v-if="chapters.length === 0" class="text-sm text-slate-500 rounded border border-dashed border-slate-300 p-3">
                  {{ tr('还没有章节正文。可先点击“生成当前章正文”。', 'No chapter content yet. You can click \"Generate Current Chapter\" first.') }}
                </div>
                <article v-for="chapter in chapters" :key="chapter.chapter_no" class="rounded border border-slate-200 p-3 bg-slate-50">
                  <div class="flex items-center justify-between gap-2">
                    <div class="font-medium">{{ tr('第', 'Chapter ') }}{{ chapter.chapter_no }}{{ tr('章', '') }} · {{ chapter.title }}</div>
                    <div class="flex items-center gap-1">
                      <button class="text-xs px-2 py-1 rounded border border-slate-300 hover:bg-white" @click="activeChapterNo = chapter.chapter_no">
                        {{ tr('设为当前章', 'Set as Current') }}
                      </button>
                      <button class="text-xs px-2 py-1 rounded border border-slate-300 hover:bg-white" @click="copyChapter(chapter)">
                        {{ tr('复制本章', 'Copy Chapter') }}
                      </button>
                      <button class="text-xs px-2 py-1 rounded border border-rose-200 text-rose-600 hover:bg-rose-50" @click="deleteChapterByNo(chapter.chapter_no)">
                        {{ tr('删除', 'Delete') }}
                      </button>
                    </div>
                  </div>
                  <p v-if="chapter.summary" class="text-xs text-slate-500 mt-1">{{ tr('摘要：', 'Summary: ') }}{{ chapter.summary }}</p>
                  <pre class="mt-2 whitespace-pre-wrap break-words text-sm leading-7">{{ chapter.content }}</pre>
                </article>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="tab === 'works'" class="grid grid-cols-1 xl:grid-cols-[340px,1fr] gap-4">
        <div class="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
          <div class="flex items-center justify-between gap-2">
            <h2 class="font-semibold">{{ t("novelStoryPage.works.title") }}</h2>
            <button class="px-2 py-1 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="worksLoading" @click="loadWorks">
              {{ worksLoading ? t("novelStoryPage.works.refreshing") : t("novelStoryPage.works.refresh") }}
            </button>
          </div>
          <p class="text-[11px] text-slate-500">{{ t("novelStoryPage.works.desc") }}</p>
          <div class="flex flex-wrap gap-2">
            <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs" @click="startNewWork">{{ t("novelStoryPage.works.newWork") }}</button>
            <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs" @click="tab = 'creation'">{{ t("novelStoryPage.works.goCreation") }}</button>
          </div>
          <p v-if="worksError" class="text-xs text-rose-600">{{ worksError }}</p>
          <p v-if="worksInfo" class="text-xs text-emerald-700">{{ worksInfo }}</p>
          <div class="space-y-2 max-h-[680px] overflow-auto">
            <div v-if="!worksLoading && works.length === 0" class="text-xs text-slate-500 rounded border border-dashed border-slate-300 p-2">
              {{ t("novelStoryPage.works.emptyList") }}
            </div>
            <article
              v-for="work in works"
              :key="work.id"
              class="rounded-lg border p-2 cursor-pointer transition-colors"
              :class="selectedWorkId === work.id ? 'border-slate-900 bg-slate-100' : 'border-slate-200 bg-white hover:bg-slate-50'"
              @click="selectWork(work)"
            >
              <div class="flex items-start gap-2.5">
                <img
                  :src="work.cover_image || `https://api.dicebear.com/7.x/shapes/svg?seed=${encodeURIComponent(work.title || String(work.id))}&backgroundColor=e2e8f0`"
                  :alt="t('novelStoryPage.works.coverAlt')"
                  class="w-16 h-16 rounded object-cover border border-slate-200 shrink-0"
                />
                <div class="min-w-0">
                  <div class="flex items-center gap-1.5">
                    <div class="text-xs font-medium truncate">{{ work.title || t("novelStoryPage.works.untitledWork") }}</div>
                    <span class="text-[10px] px-1.5 py-0.5 rounded border border-slate-200 text-slate-500 bg-white">{{ t("novelStoryPage.works.workBadge") }}</span>
                  </div>
                  <div class="text-[11px] text-slate-500 mt-0.5 line-clamp-2">{{ work.summary || t("novelStoryPage.works.noSummary") }}</div>
                  <div class="mt-1 text-[11px] text-slate-500">
                    {{ t(workStatusKey(work.extra_meta?.completion_status)) }} · {{ formatTime(work.updated_at) }}
                  </div>
                </div>
              </div>
            </article>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-white p-4 space-y-3 min-h-[700px]">
          <div v-if="!selectedWork" class="text-sm text-slate-500">{{ t("novelStoryPage.works.selectWorkHint") }}</div>
          <template v-else>
            <div class="flex flex-wrap items-start justify-between gap-2 border-b border-slate-200 pb-3">
              <div>
                <h3 class="text-lg font-semibold">{{ selectedWork.title || t("novelStoryPage.works.untitledWork") }}</h3>
                <p class="text-xs text-slate-500 mt-1">{{ selectedWork.summary || t("novelStoryPage.works.noSummary") }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs" @click="openWorkInCreation(selectedWork)">{{ t("novelStoryPage.works.backToCreationEdit") }}</button>
                <button class="px-2.5 py-1.5 rounded border border-rose-200 text-rose-600 text-xs" @click="deleteWork(selectedWork)">{{ t("novelStoryPage.works.deleteWork") }}</button>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
              <div class="rounded border border-slate-200 p-2">{{ t("novelStoryPage.works.stats.chapters") }}{{ selectedWork.chapters.length }}</div>
              <div class="rounded border border-slate-200 p-2">{{ t("novelStoryPage.works.stats.characters") }}{{ workEditorCharacters.length }}</div>
              <div class="rounded border border-slate-200 p-2">{{ t("novelStoryPage.works.stats.characterImages") }}{{ workEditorCharacterImages.length }}</div>
              <div class="rounded border border-slate-200 p-2">{{ t("novelStoryPage.works.stats.status") }}{{ t(workStatusKey(selectedWorkCompletionStatus)) }}</div>
            </div>

            <div class="rounded border border-slate-200 p-3 space-y-3">
              <h4 class="text-sm font-semibold">{{ t("novelStoryPage.works.editInfoTitle") }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div class="md:col-span-2">
                  <label class="text-xs text-slate-600">{{ t("novelStoryPage.works.workTitleLabel") }}</label>
                  <input v-model="workEditorTitle" class="w-full mt-1 rounded border border-slate-200 px-3 py-2 text-sm" />
                </div>
                <div class="md:col-span-2">
                  <label class="text-xs text-slate-600">{{ t("novelStoryPage.works.workSummaryLabel") }}</label>
                  <textarea v-model="workEditorSummary" class="w-full h-20 mt-1 rounded border border-slate-200 px-3 py-2 text-sm resize-none"></textarea>
                </div>
                <div class="md:col-span-2">
                  <label class="text-xs text-slate-600">{{ t("novelStoryPage.works.workNotesLabel") }}</label>
                  <textarea v-model="workEditorNotes" class="w-full h-20 mt-1 rounded border border-slate-200 px-3 py-2 text-sm resize-none"></textarea>
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="workEditorLoading" @click="aiFillWorkInfo">
                  {{ workEditorLoading ? t("novelStoryPage.works.processing") : t("novelStoryPage.works.aiFillInfo") }}
                </button>
                <button class="px-2.5 py-1.5 rounded bg-slate-900 text-white text-xs disabled:opacity-60" :disabled="workEditorSaving" @click="saveWorkEditorChanges">
                  {{ workEditorSaving ? t("novelStoryPage.works.saving") : t("novelStoryPage.works.saveWorkInfo") }}
                </button>
              </div>
              <p v-if="workEditorError" class="text-xs text-rose-600">{{ workEditorError }}</p>
              <p v-if="workEditorInfo" class="text-xs text-emerald-700">{{ workEditorInfo }}</p>
            </div>

            <div class="rounded border border-slate-200 p-3 space-y-3">
              <h4 class="text-sm font-semibold">{{ t("novelStoryPage.works.coverAndCharacterTitle") }}</h4>
              <p class="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1">
                {{ t("novelStoryPage.creation.complianceNotice") }}
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="space-y-2">
                  <label class="text-xs text-slate-600">{{ t("novelStoryPage.works.coverPromptLabel") }}</label>
                  <textarea v-model="workEditorCoverPrompt" class="w-full h-20 rounded border border-slate-200 px-3 py-2 text-xs resize-none"></textarea>
                  <div class="flex flex-wrap gap-1.5">
                    <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="workEditorLoading || isUploadingCustomImage" @click="generateWorkEditorCover">
                      {{ workEditorLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.works.aiGenerateCover") }}
                    </button>
                    <button class="px-2.5 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50 text-xs disabled:opacity-60" :disabled="workEditorLoading || isUploadingCustomImage" @click="openWorkEditorCoverUploadPicker">
                      {{ isUploadingCustomImage ? t("novelStoryPage.creation.reviewUploading") : t("novelStoryPage.creation.uploadCustomCover") }}
                    </button>
                  </div>
                  <input ref="workEditorCoverUploadInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="handleWorkEditorCoverUpload" />
                  <img v-if="workEditorCoverImage" :src="workEditorCoverImage" :alt="t('novelStoryPage.works.workCoverAlt')" class="w-full h-40 object-cover rounded border border-slate-200" />
                </div>

                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <label class="text-xs text-slate-600">{{ t("novelStoryPage.works.characterSettingLabel") }}</label>
                    <button class="px-2 py-1 rounded border border-slate-300 text-[11px]" @click="addWorkEditorCharacter">{{ t("novelStoryPage.works.addCharacter") }}</button>
                  </div>
                  <div class="space-y-2 max-h-60 overflow-auto">
                    <div v-for="c in workEditorCharacters" :key="c.id" class="rounded border border-slate-200 p-2 space-y-1">
                      <div class="flex items-center gap-2">
                        <input v-model="c.name" class="flex-1 rounded border border-slate-200 px-2 py-1 text-xs" :placeholder="t('novelStoryPage.creation.characterNamePlaceholder')" />
                        <button class="px-2 py-1 rounded border border-rose-200 text-rose-600 text-[11px]" @click="removeWorkEditorCharacter(c.id)">{{ t("novelStoryPage.works.delete") }}</button>
                      </div>
                      <input v-model="c.role" class="w-full rounded border border-slate-200 px-2 py-1 text-xs" :placeholder="t('novelStoryPage.creation.characterRolePlaceholder')" />
                      <textarea v-model="c.personality" class="w-full h-12 rounded border border-slate-200 px-2 py-1 text-xs resize-none" :placeholder="t('novelStoryPage.creation.characterPersonalityPlaceholder')"></textarea>
                    </div>
                  </div>

                  <div class="rounded border border-slate-200 p-2 space-y-1">
                    <select v-model="workEditorCharacterTargetId" class="w-full rounded border border-slate-200 px-2 py-1 text-xs">
                      <option value="">{{ t("novelStoryPage.works.selectCharacterForImage") }}</option>
                      <option v-for="c in workEditorCharacters" :key="c.id" :value="c.id">{{ c.name || t("novelStoryPage.creation.untitledCharacter") }}</option>
                    </select>
                    <textarea v-model="workEditorCharacterPrompt" class="w-full h-12 rounded border border-slate-200 px-2 py-1 text-xs resize-none" :placeholder="t('novelStoryPage.works.workEditorCharacterPromptPlaceholder')"></textarea>
                    <div class="flex flex-wrap gap-1.5">
                      <button class="px-2.5 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="workEditorLoading || isUploadingCustomImage || !workEditorCharacterTargetId" @click="generateWorkEditorCharacterImage">
                        {{ workEditorLoading ? t("novelStoryPage.creation.generating") : t("novelStoryPage.works.aiGenerateCharacterImage") }}
                      </button>
                      <button class="px-2.5 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50 text-xs disabled:opacity-60" :disabled="workEditorLoading || isUploadingCustomImage || !workEditorCharacterTargetId" @click="openWorkEditorCharacterUploadPicker">
                        {{ isUploadingCustomImage ? t("novelStoryPage.creation.reviewUploading") : t("novelStoryPage.works.uploadCustomCharacterImage") }}
                      </button>
                    </div>
                    <input ref="workEditorCharacterUploadInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="handleWorkEditorCharacterUpload" />
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-5 gap-2" v-if="workEditorCharacterImages.length > 0">
                <div v-for="img in workEditorCharacterImages" :key="img.id" class="rounded border border-slate-200 p-1">
                  <img :src="img.image_url" :alt="img.character_name || t('novelStoryPage.creation.characterImageAlt')" class="w-full h-20 object-cover rounded" />
                  <p class="text-[11px] text-slate-600 mt-1 truncate">{{ img.character_name || t("novelStoryPage.creation.characterImageAlt") }}</p>
                </div>
              </div>
            </div>

            <div class="rounded border border-slate-200 p-3 space-y-3">
              <div class="flex items-center justify-between gap-2">
                <h4 class="text-sm font-semibold">{{ t("novelStoryPage.works.chaptersTitle") }}</h4>
                <span class="text-[11px] text-slate-500">{{ t("novelStoryPage.works.clickChapterToView") }}</span>
              </div>

              <div v-if="selectedWorkChapterList.length === 0" class="text-xs text-slate-500 rounded border border-dashed border-slate-300 p-2">
                {{ t("novelStoryPage.works.noChaptersYet") }}
              </div>

              <template v-else>
                <div class="flex flex-wrap gap-1.5 max-h-24 overflow-auto">
                  <button
                    v-for="chapter in selectedWorkChapterList"
                    :key="`work_chapter_${chapter.chapter_no}`"
                    class="px-2.5 py-1 rounded border text-xs"
                    :class="selectedWorkChapter?.chapter_no === chapter.chapter_no ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'"
                    @click="selectedWorkChapterNo = chapter.chapter_no"
                  >
                    {{ t("novelStoryPage.creation.chapterPrefix", { no: chapter.chapter_no }) }}
                  </button>
                </div>

                <article v-if="selectedWorkChapter" class="rounded border border-slate-200 bg-slate-50 p-3">
                  <div class="font-medium text-sm">{{ t("novelStoryPage.creation.chapterPrefix", { no: selectedWorkChapter.chapter_no }) }} · {{ selectedWorkChapter.title }}</div>
                  <p v-if="selectedWorkChapter.summary" class="text-xs text-slate-500 mt-1">{{ selectedWorkChapter.summary }}</p>
                  <pre class="text-xs whitespace-pre-wrap break-words mt-2">{{ selectedWorkChapter.content }}</pre>
                </article>
              </template>
            </div>
          </template>
        </div>
      </section>
      <section v-else class="grid grid-cols-1 xl:grid-cols-[300px,1fr] gap-4">
        <div class="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
          <div class="flex justify-between items-center">
            <h2 class="font-semibold">{{ t("novelStoryPage.sync.charactersTitle") }}</h2>
            <div class="flex items-center gap-1.5">
              <button class="px-2 py-1 rounded border border-rose-200 text-rose-600 text-xs" @click="clearRoleCharacters">
                {{ t("novelStoryPage.sync.clearCharacters") }}
              </button>
              <button class="px-2 py-1 rounded border border-slate-300 text-xs" @click="addCharacter">{{ t("novelStoryPage.sync.newCharacter") }}</button>
            </div>
          </div>
          <button class="w-full px-2 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60" :disabled="!plan" @click="syncPlanToRoleplay">
            {{ t("novelStoryPage.sync.importFromPlan") }}
          </button>
          <div class="space-y-2 max-h-[320px] overflow-auto">
            <button
              v-for="c in characters"
              :key="c.id"
              class="w-full text-left rounded border px-2 py-2 text-sm"
              :class="activeId === c.id ? 'border-slate-900 bg-slate-100' : 'border-slate-200'"
              @click="activeId = c.id"
            >
              {{ c.name || t("novelStoryPage.creation.untitledCharacter") }}
            </button>
          </div>
          <div v-if="activeChar" class="space-y-2 border-t border-slate-200 pt-2">
            <input v-model="activeChar.name" class="w-full rounded border border-slate-200 px-2 py-1.5 text-sm" :placeholder="t('novelStoryPage.creation.characterNamePlaceholder')" />
            <input v-model="activeChar.role" class="w-full rounded border border-slate-200 px-2 py-1.5 text-sm" :placeholder="t('novelStoryPage.creation.characterRolePlaceholder')" />
            <input v-model="activeChar.goal" class="w-full rounded border border-slate-200 px-2 py-1.5 text-sm" :placeholder="t('novelStoryPage.sync.characterGoalPlaceholder')" />
            <input v-model="activeChar.arc" class="w-full rounded border border-slate-200 px-2 py-1.5 text-sm" :placeholder="t('novelStoryPage.sync.characterArcPlaceholder')" />
            <textarea v-model="activeChar.personality" class="w-full h-16 rounded border border-slate-200 px-2 py-1.5 text-sm resize-none" :placeholder="t('novelStoryPage.creation.characterPersonalityPlaceholder')"></textarea>
            <button class="w-full px-2 py-1.5 rounded border border-rose-200 text-rose-600 text-xs disabled:opacity-40" :disabled="characters.length <= 1" @click="removeCharacter">
              {{ t("novelStoryPage.creation.removeCurrentCharacter") }}
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <div class="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h2 class="text-lg font-semibold">{{ t("novelStoryPage.sync.importTitle") }}</h2>
              <button
                class="px-3 py-1.5 rounded border border-slate-300 text-xs disabled:opacity-60"
                :disabled="tavernImportLoading"
                @click="loadTavernPersonasForImport"
              >
                {{ tavernImportLoading ? t("novelStoryPage.sync.loading") : t("novelStoryPage.sync.refreshTavernRoles") }}
              </button>
            </div>
            <p class="text-xs text-slate-500">{{ t("novelStoryPage.sync.importDesc") }}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <input
                v-model="tavernImportKeyword"
                class="rounded border border-slate-200 px-3 py-2 text-sm"
                :placeholder="t('novelStoryPage.sync.searchImportPlaceholder')"
              />
              <select v-model="tavernImportMode" class="rounded border border-slate-200 px-3 py-2 text-sm">
                <option value="append">{{ t("novelStoryPage.sync.importModeAppend") }}</option>
                <option value="replace">{{ t("novelStoryPage.sync.importModeReplace") }}</option>
              </select>
              <textarea
                v-model="tavernSecondaryPrompt"
                class="md:col-span-2 h-20 rounded border border-slate-200 px-3 py-2 text-sm resize-none"
                :placeholder="t('novelStoryPage.sync.secondaryPromptPlaceholder')"
              ></textarea>
            </div>
            <div class="flex flex-wrap gap-2">
              <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="filteredTavernImportList.length === 0" @click="selectAllFilteredTavernPersonas">
                {{ t("novelStoryPage.sync.selectAllFiltered") }}
              </button>
              <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="selectedTavernPersonaIds.length === 0" @click="clearSelectedTavernPersonas">
                {{ t("novelStoryPage.sync.clearSelection") }}
              </button>
              <button class="px-3 py-2 rounded border border-rose-200 text-rose-600 text-sm" @click="clearTavernImportPanel">
                {{ t("novelStoryPage.sync.clearImportPanel") }}
              </button>
              <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="selectedTavernPersonaIds.length === 0" @click="importSelectedTavernPersonas()">
                {{ t("novelStoryPage.sync.importOnlyRoles") }}
              </button>
              <button
                class="px-3 py-2 rounded bg-slate-900 text-white text-sm disabled:opacity-60"
                :disabled="selectedTavernPersonaIds.length === 0 || tavernImportGenerating"
                @click="importAndRegeneratePlanFromTavern"
              >
                {{ tavernImportGenerating ? t("novelStoryPage.creation.generating") : t("novelStoryPage.sync.importAndGeneratePlan") }}
              </button>
            </div>
            <p class="text-xs text-slate-500">{{ t("novelStoryPage.sync.selectedCount", { selected: selectedTavernImportList.length, total: filteredTavernImportList.length }) }}</p>
            <div class="max-h-64 overflow-auto rounded border border-slate-200 divide-y divide-slate-100">
              <label
                v-for="item in filteredTavernImportList"
                :key="`tavern_import_${item.id}`"
                class="flex items-start gap-2 p-2 hover:bg-slate-50 cursor-pointer"
              >
                <input v-model="selectedTavernPersonaIds" :value="item.id" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900" />
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-medium truncate">{{ item.name || t("novelStoryPage.creation.untitledCharacter") }}</div>
                  <p class="text-[11px] text-slate-500">{{ item.group || t("novelStoryPage.sync.ungrouped") }} · {{ item.source || 'custom' }}</p>
                  <p class="text-xs text-slate-700 mt-1">{{ compactText(item.description || item.systemPrompt || item.firstMessage || t("novelStoryPage.creation.noCharacterSetting"), 160) }}</p>
                </div>
              </label>
              <div v-if="filteredTavernImportList.length === 0" class="p-3 text-xs text-slate-500">
                {{ t("novelStoryPage.sync.noImportRoles") }}
              </div>
            </div>
            <p v-if="tavernImportError" class="text-xs text-rose-600">{{ tavernImportError }}</p>
            <p v-if="tavernImportInfo" class="text-xs text-emerald-700">{{ tavernImportInfo }}</p>
          </div>

          <div class="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
            <h2 class="text-lg font-semibold">{{ t("novelStoryPage.sync.cardSyncTitle") }}</h2>
            <p class="text-xs text-slate-500">{{ t("novelStoryPage.sync.cardSyncDesc") }}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <input v-model="storyTitle" class="rounded border border-slate-200 px-3 py-2 text-sm" :placeholder="t('novelStoryPage.sync.storyTitlePlaceholder')" />
              <input v-model="tavernGroup" class="rounded border border-slate-200 px-3 py-2 text-sm" :placeholder="t('novelStoryPage.sync.tavernGroupPlaceholder')" />
              <input v-model="currentSituation" class="rounded border border-slate-200 px-3 py-2 text-sm" :placeholder="t('novelStoryPage.sync.currentSituationPlaceholder')" />
              <input v-model="worldContext" class="rounded border border-slate-200 px-3 py-2 text-sm" :placeholder="t('novelStoryPage.sync.worldContextPlaceholder')" />
              <textarea v-model="worldBookNotes" class="md:col-span-2 h-20 rounded border border-slate-200 px-3 py-2 text-sm resize-none" :placeholder="t('novelStoryPage.sync.worldBookNotesPlaceholder')"></textarea>
            </div>
            <div class="flex flex-wrap gap-2">
              <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="!activeChar" @click="generateCharacterCard">
                {{ t("novelStoryPage.sync.generateCardJson") }}
              </button>
              <button class="px-3 py-2 rounded bg-slate-900 text-white text-sm disabled:opacity-60" :disabled="!activeChar" @click="syncActiveCharacterToTavern">
                {{ t("novelStoryPage.sync.syncCurrentCharacter") }}
              </button>
              <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="characters.length === 0" @click="syncAllCharactersToTavern">
                {{ t("novelStoryPage.sync.syncAllCharacters") }}
              </button>
              <button
                class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60"
                :disabled="!activeChar || imageLoading || isUploadingCustomImage"
                @click="generateSyncCharacterCardImage"
              >
                {{ imageLoading ? t("novelStoryPage.creation.generating") : tr("AI生成角色卡图片", "AI Generate Card Image") }}
              </button>
              <button
                class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60"
                :disabled="!activeChar || isUploadingCustomImage"
                @click="openSyncCharacterUploadPicker"
              >
                {{ tr("上传角色卡图片", "Upload Card Image") }}
              </button>
              <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="!activeChar" @click="downloadGeneratedCard">
                {{ t("novelStoryPage.sync.downloadCard") }}
              </button>
              <button class="px-3 py-2 rounded border border-rose-200 text-rose-600 text-sm" @click="clearTavernSyncPanel">
                {{ t("novelStoryPage.sync.clearSyncPanel") }}
              </button>
              <button class="px-3 py-2 rounded border border-slate-300 text-sm" @click="openTavernPage">{{ t("novelStoryPage.sync.openTavern") }}</button>
            </div>
            <input ref="syncCharacterUploadInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="handleSyncCharacterUpload" />
            <p v-if="tavernSyncError" class="text-xs text-rose-600">{{ tavernSyncError }}</p>
            <p v-if="tavernSyncInfo" class="text-xs text-emerald-700">{{ tavernSyncInfo }}</p>
            <details v-if="generatedCharacterCard" class="rounded border border-slate-200 p-2">
              <summary class="cursor-pointer text-sm">{{ t("novelStoryPage.sync.viewCardJsonPreview") }}</summary>
              <pre class="mt-2 text-xs whitespace-pre-wrap break-all">{{ JSON.stringify(generatedCharacterCard, null, 2) }}</pre>
            </details>
          </div>

          <div class="rounded-xl border border-slate-200 bg-white p-4 flex flex-col min-h-[640px]">
            <div class="flex-1 rounded border border-slate-200 bg-slate-50 p-3 overflow-auto space-y-2">
              <div v-if="messages.length === 0" class="text-sm text-slate-500">{{ t("novelStoryPage.sync.noConversation") }}</div>
              <div
                v-for="m in messages"
                :key="m.id"
                class="max-w-[85%] rounded px-3 py-2 text-sm whitespace-pre-wrap"
                :class="m.role === 'user' ? 'ml-auto bg-slate-900 text-white' : m.role === 'assistant' ? 'bg-white border border-slate-200' : 'mx-auto bg-amber-50 border border-amber-200 text-amber-800'"
              >
                {{ m.content }}
              </div>
            </div>

            <div class="mt-3 space-y-2">
              <textarea v-model="inputText" class="w-full h-20 rounded border border-slate-200 px-3 py-2 text-sm resize-none" :placeholder="t('novelStoryPage.sync.inputMessagePlaceholder')"></textarea>
              <div class="flex gap-2">
                <button class="px-3 py-2 rounded bg-slate-900 text-white text-sm disabled:opacity-60" :disabled="replyLoading" @click="sendMessage">
                  {{ replyLoading ? t("novelStoryPage.sync.replying") : t("novelStoryPage.sync.sendAndReply") }}
                </button>
                <button class="px-3 py-2 rounded border border-slate-300 text-sm disabled:opacity-60" :disabled="impactLoading || messages.length === 0" @click="analyzeImpact">
                  {{ impactLoading ? t("novelStoryPage.sync.analyzing") : t("novelStoryPage.sync.analyzeImpact") }}
                </button>
                <button class="px-3 py-2 rounded border border-slate-300 text-sm" @click="messages = []">{{ t("novelStoryPage.sync.clearConversation") }}</button>
              </div>
              <p v-if="roleplayError" class="text-xs text-rose-600">{{ roleplayError }}</p>
              <div v-if="plotInstruction" class="text-sm rounded border border-amber-200 bg-amber-50 p-2">{{ plotInstruction }}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import client from '../api/client'

type MsgRole = 'user' | 'assistant' | 'system'
type ChatMessagePayload = { role: MsgRole; content: string }
interface Character {
  id: string
  name: string
  role: string
  personality: string
  goal?: string
  arc?: string
}
interface Msg {
  id: string
  role: MsgRole
  content: string
}
interface Plan {
  title: string
  genre: string
  tone: string
  setting: string
  core_conflict: string
  characters: Array<{ name: string; role: string; goal: string; arc: string }>
  chapter_outlines: Array<{ chapter_no: number; title: string; summary: string; twist: string }>
}
interface DraftChapter {
  chapter_no: number
  title: string
  summary: string
  content: string
  updated_at: string
}
interface CharacterImageAsset {
  id: string
  character_id: string
  character_name: string
  prompt: string
  image_url: string
  created_at: string
}
interface ChapterImageAsset {
  id: string
  chapter_no: number
  chapter_title: string
  prompt: string
  image_url: string
  created_at: string
}
interface NovelWork {
  id: number
  title: string
  summary: string
  plan: Plan | null
  chapters: DraftChapter[]
  cover_image: string
  character_images: CharacterImageAsset[]
  chapter_images: ChapterImageAsset[]
  extra_meta: Record<string, any>
  created_at: string
  updated_at: string
}

interface ChapterHistorySnapshot {
  id: string
  reason: string
  created_at: string
  active_chapter_no: number
  chapters: DraftChapter[]
  plan: Plan | null
}

interface TavernPersonaItem {
  id: string
  name: string
  avatar: string
  description: string
  systemPrompt: string
  firstMessage: string
  group: string
  source: string
  meta: Record<string, any>
}

const { t, locale } = useI18n()
const isChineseLocale = computed(() => String(locale.value || '').toLowerCase().startsWith('zh'))
const tr = (zh: string, en: string): string => (isChineseLocale.value ? zh : en)

const tab = ref<'creation' | 'works' | 'sync'>('creation')
const creationMode = ref<'professional' | 'light'>('professional')
const idea = ref('')
const genre = ref('')
const tone = ref('')
const setting = ref('')
const chapterCount = ref(8)
const lightContinuationCount = ref(5)
const workshopLoading = ref(false)
const workshopError = ref('')
const outlineLoading = ref(false)
const plan = ref<Plan | null>(null)
const activeChapterNo = ref(1)
const targetWords = ref(1800)
const continuationHint = ref('')
const chapterLoading = ref(false)
const chapterError = ref('')
const chapterInfo = ref('')
const chapters = ref<DraftChapter[]>([])
const chapterHistory = ref<ChapterHistorySnapshot[]>([])
const bookStatus = ref<'draft' | 'completed'>('draft')
const characterImpactPending = ref(false)
const characterImpactMessage = ref('')
const characterImpactBaseSignature = ref('')

const storyTitle = ref(t('novelStoryPage.sync.defaultStoryTitle'))
const worldContext = ref('')
const currentSituation = ref('')
const characters = ref<Character[]>([
  {
    id: id('c'),
    name: t('novelStoryPage.sync.defaultCharacterName'),
    role: t('novelStoryPage.sync.defaultCharacterRole'),
    personality: t('novelStoryPage.sync.defaultCharacterPersonality'),
    goal: '',
    arc: '',
  },
])
const activeId = ref(characters.value[0].id)
const messages = ref<Msg[]>([])
const inputText = ref('')
const replyLoading = ref(false)
const impactLoading = ref(false)
const roleplayError = ref('')
const plotInstruction = ref('')
const draftLoading = ref(false)
const draftSaving = ref(false)
const draftError = ref('')
const draftInfo = ref('')
const draftHydrating = ref(false)
const works = ref<NovelWork[]>([])
const worksLoading = ref(false)
const worksSaving = ref(false)
const worksError = ref('')
const worksInfo = ref('')
const selectedWorkId = ref<number | null>(null)
const selectedWorkChapterNo = ref<number | null>(null)
const coverPrompt = ref('')
const coverImage = ref('')
const characterImagePrompt = ref('')
const characterImageTargetId = ref('')
const chapterImagePrompt = ref('')
const characterImages = ref<CharacterImageAsset[]>([])
const chapterImages = ref<ChapterImageAsset[]>([])
const imageLoading = ref(false)
const imageError = ref('')
const imageInfo = ref('')
const tavernGroup = ref(t('novelStoryPage.sync.defaultTavernGroup'))
const worldBookNotes = ref('')
const generatedCharacterCard = ref<any | null>(null)
const tavernSyncInfo = ref('')
const tavernSyncError = ref('')
const tavernImportList = ref<TavernPersonaItem[]>([])
const tavernImportLoading = ref(false)
const tavernImportKeyword = ref('')
const tavernImportMode = ref<'append' | 'replace'>('append')
const selectedTavernPersonaIds = ref<string[]>([])
const tavernSecondaryPrompt = ref('')
const tavernImportInfo = ref('')
const tavernImportError = ref('')
const tavernImportGenerating = ref(false)

const workEditorTitle = ref('')
const workEditorSummary = ref('')
const workEditorNotes = ref('')
const workEditorCoverPrompt = ref('')
const workEditorCoverImage = ref('')
const workEditorCharacters = ref<Character[]>([])
const workEditorCharacterImages = ref<CharacterImageAsset[]>([])
const workEditorCharacterTargetId = ref('')
const workEditorCharacterPrompt = ref('')
const workEditorLoading = ref(false)
const workEditorSaving = ref(false)
const workEditorInfo = ref('')
const workEditorError = ref('')
const isUploadingCustomImage = ref(false)
const creationCoverUploadInputRef = ref<HTMLInputElement | null>(null)
const creationCharacterUploadInputRef = ref<HTMLInputElement | null>(null)
const creationChapterUploadInputRef = ref<HTMLInputElement | null>(null)
const syncCharacterUploadInputRef = ref<HTMLInputElement | null>(null)
const workEditorCoverUploadInputRef = ref<HTMLInputElement | null>(null)
const workEditorCharacterUploadInputRef = ref<HTMLInputElement | null>(null)

const DRAFT_CLIENT_KEY = 'novel_story_client_id'
const TAVERN_CUSTOM_PERSONAS_KEY = 'cypher_tavern_custom_personas'
const TAVERN_CUSTOM_PERSONAS_KEY_V2 = 'cypher_tavern_custom_personas_v2'
const TAVERN_SETTINGS_KEY = 'cypher_tavern_settings'
const TAVERN_SETTINGS_KEY_V2 = 'cypher_tavern_settings_v2'
const CUSTOM_IMAGE_ALLOWED_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp', 'image/gif'])
const CUSTOM_IMAGE_MAX_SIZE_BYTES = 8 * 1024 * 1024
const CUSTOM_IMAGE_MAX_EDGE = 6144
const CUSTOM_IMAGE_MIN_EDGE = 96
const CARD_EXPORT_WIDTH = 768
const CARD_EXPORT_HEIGHT = 1024
const PNG_SIGNATURE = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10])
const CRC32_TABLE = (() => {
  const table = new Uint32Array(256)
  for (let index = 0; index < 256; index += 1) {
    let value = index
    for (let bit = 0; bit < 8; bit += 1) {
      value = (value & 1) !== 0 ? (0xedb88320 ^ (value >>> 1)) : (value >>> 1)
    }
    table[index] = value >>> 0
  }
  return table
})()
const CUSTOM_IMAGE_BLOCKED_KEYWORDS = [
  'porn',
  'nsfw',
  'sex',
  'nude',
  'naked',
  'hentai',
  'fetish',
  'r18',
  'smut',
  'violence',
  'drug',
  'weapon',
  'terror',
  '犯罪',
  '违法',
  '色情',
  '裸露',
  '低俗',
  '淫秽',
  '毒品',
  '枪支',
  '爆炸',
  '恐怖',
  '血腥',
]
const BACKEND_ORIGIN = (() => {
  const preferred = (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim()
  return (preferred || 'http://127.0.0.1:8000').replace(/\/+$/, '')
})()
let draftSaveTimer: ReturnType<typeof setTimeout> | null = null

const OUTPUT_LANGUAGE_NAME_MAP: Record<string, string> = {
  'zh-CN': '简体中文',
  'zh-TW': '繁體中文',
  en: 'English',
  ja: '日本語',
  ko: '한국어',
  th: 'ภาษาไทย',
  vi: 'Tiếng Việt',
  fr: 'Français',
  de: 'Deutsch',
}

function normalizePromptLocale(rawLocale: unknown): string {
  const raw = String(rawLocale || '').trim().toLowerCase()
  if (!raw) return 'zh-CN'
  if (raw.startsWith('zh')) {
    if (raw.includes('tw') || raw.includes('hk') || raw.includes('hant')) return 'zh-TW'
    return 'zh-CN'
  }
  if (raw.startsWith('ja')) return 'ja'
  if (raw.startsWith('ko')) return 'ko'
  if (raw.startsWith('th')) return 'th'
  if (raw.startsWith('vi')) return 'vi'
  if (raw.startsWith('fr')) return 'fr'
  if (raw.startsWith('de')) return 'de'
  if (raw.startsWith('en')) return 'en'
  return 'zh-CN'
}

function outputLanguageName(): string {
  const normalized = normalizePromptLocale(locale.value)
  return OUTPUT_LANGUAGE_NAME_MAP[normalized] || OUTPUT_LANGUAGE_NAME_MAP['zh-CN']
}

function outputLanguageConstraint(): string {
  const targetLang = outputLanguageName()
  return `【重要指令】：请务必使用 ${targetLang} 输出生成的小说正文、说明与分析内容，不要夹杂其他语言。`
}

function withOutputLanguageConstraint(messagesPayload: ChatMessagePayload[]): ChatMessagePayload[] {
  const next = (Array.isArray(messagesPayload) ? messagesPayload : []).map((item) => ({
    role: item.role,
    content: String(item.content || ''),
  }))
  if (next.length === 0) return next
  if (next.some((item) => item.content.includes('【重要指令】：请务必使用'))) return next

  const constraint = outputLanguageConstraint()
  for (let index = next.length - 1; index >= 0; index -= 1) {
    if (next[index].role !== 'user') continue
    const base = String(next[index].content || '').trim()
    next[index] = {
      ...next[index],
      content: base ? `${base}\n\n${constraint}` : constraint,
    }
    return next
  }

  const first = next[0]
  const head = String(first.content || '').trim()
  next[0] = {
    ...first,
    content: head ? `${head}\n\n${constraint}` : constraint,
  }
  return next
}

const activeChar = computed(() => characters.value.find((c) => c.id === activeId.value) || null)
const selectedImageCharacter = computed(() => characters.value.find((c) => c.id === characterImageTargetId.value) || null)
const selectedWork = computed(() => works.value.find((item) => item.id === selectedWorkId.value) || null)
const selectedWorkChapterList = computed(() => {
  if (!selectedWork.value) return []
  return [...selectedWork.value.chapters].sort((a, b) => a.chapter_no - b.chapter_no)
})
const selectedWorkChapter = computed(() => {
  const list = selectedWorkChapterList.value
  if (list.length === 0) return null
  const targetNo = Number(selectedWorkChapterNo.value || 0)
  if (targetNo > 0) {
    return list.find((item) => item.chapter_no === targetNo) || list[0]
  }
  return list[0]
})
const selectedWorkCompletionStatus = computed<'draft' | 'completed'>(() => {
  const status = String(selectedWork.value?.extra_meta?.completion_status || '').toLowerCase()
  return status === 'completed' ? 'completed' : 'draft'
})
const workStatusKey = (statusValue: unknown): string => {
  const status = String(statusValue || '').toLowerCase()
  return status === 'completed'
    ? 'novelStoryPage.works.status.completed'
    : 'novelStoryPage.works.status.ongoing'
}
const filteredTavernImportList = computed(() => {
  const keyword = String(tavernImportKeyword.value || '')
    .trim()
    .toLowerCase()
  if (!keyword) return tavernImportList.value
  return tavernImportList.value.filter((item) => {
    const haystack = [item.name, item.group, item.description, item.systemPrompt, item.firstMessage]
      .map((part) => String(part || '').toLowerCase())
      .join('\n')
    return haystack.includes(keyword)
  })
})
const selectedTavernImportList = computed(() => {
  const picked = new Set(selectedTavernPersonaIds.value)
  return tavernImportList.value.filter((item) => picked.has(item.id))
})

type MessageRef = { value: string }

function resolveBackendMediaUrl(rawUrl: string): string {
  const url = String(rawUrl || '').trim()
  if (!url) return ''
  if (url.startsWith('data:image/')) return url
  if (/^https?:\/\//i.test(url)) return url
  if (url.startsWith('/')) return `${BACKEND_ORIGIN}${url}`
  if (url.startsWith('media/')) return `${BACKEND_ORIGIN}/${url}`
  return url
}

function sanitizeUploadName(name: string): string {
  const raw = String(name || '').trim()
  const cleaned = raw.replace(/[^\w.\-\u4e00-\u9fa5]+/g, '_').slice(-120)
  return cleaned || `upload_${Date.now()}.png`
}

function findBlockedKeyword(text: string): string {
  const normalized = String(text || '').toLowerCase()
  if (!normalized) return ''
  for (const keyword of CUSTOM_IMAGE_BLOCKED_KEYWORDS) {
    if (normalized.includes(keyword.toLowerCase())) return keyword
  }
  return ''
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error(t('novelStoryPage.messages.readImageFailed')))
    reader.readAsDataURL(file)
  })
}

function readImageDimensions(src: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve({ width: Number(img.naturalWidth) || 0, height: Number(img.naturalHeight) || 0 })
    img.onerror = () => reject(new Error(t('novelStoryPage.messages.readImageSizeFailed')))
    img.src = src
  })
}

function extractUploadFile(event: Event): File | null {
  const input = event.target as HTMLInputElement | null
  const file = input?.files?.[0] || null
  if (input) input.value = ''
  return file
}

function parseComplianceResult(text: string): { allowed: boolean; reason: string } | null {
  const raw = String(text || '').trim()
  if (!raw) return null

  try {
    const parsed = parseObject(raw)
    const rawAllowed = parsed?.allowed ?? parsed?.pass ?? parsed?.safe ?? parsed?.ok
    const allowed =
      typeof rawAllowed === 'boolean'
        ? rawAllowed
        : typeof rawAllowed === 'string'
          ? ['true', 'allow', 'allowed', 'safe', 'pass', 'yes'].includes(rawAllowed.toLowerCase())
          : false
    const reason = String(parsed?.reason || parsed?.message || '').trim()
    return { allowed, reason }
  } catch {
    const allowByText = /"allowed"\s*:\s*true/i.test(raw)
    const blockByText = /"allowed"\s*:\s*false/i.test(raw)
    if (allowByText || blockByText) {
      return { allowed: allowByText && !blockByText, reason: '' }
    }
    return null
  }
}

async function reviewImageComplianceByAI(dataUrl: string, usageLabel: string, fileName: string): Promise<void> {
  const cfg = getApiConfig()
  if (!cfg.apiKey) {
    throw new Error(t('novelStoryPage.messages.moderationApiKeyMissing'))
  }

  const baseUrl = cfg.baseUrl.replace(/\/+$/, '')
  const candidateModels = Array.from(new Set([String(cfg.modelName || '').trim(), 'gpt-4.1-mini', 'gpt-4o-mini'].filter(Boolean)))
  const moderationPrompt = [
    t('novelStoryPage.prompts.imageModerationCheck'),
    t('novelStoryPage.prompts.imageModerationUsage', { usage: usageLabel }),
    t('novelStoryPage.prompts.imageModerationFileName', { fileName }),
    t('novelStoryPage.prompts.imageModerationRules'),
    t('novelStoryPage.prompts.imageModerationJsonOnly'),
  ].join('\n')

  let lastError = ''
  for (const model of candidateModels) {
    const response = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${cfg.apiKey}`,
      },
      body: JSON.stringify({
        model,
        temperature: 0,
        max_tokens: 120,
        messages: [
          { role: 'system', content: t('novelStoryPage.prompts.imageModerationSystem') },
          {
            role: 'user',
            content: [
              { type: 'text', text: moderationPrompt },
              { type: 'image_url', image_url: { url: dataUrl } },
            ],
          },
        ],
      }),
    })
    if (!response.ok) {
      lastError = await readResponseErrorMessage(response)
      continue
    }

    let payload: any = null
    try {
      payload = await response.json()
    } catch {
      lastError = t('novelStoryPage.messages.moderationResponseFormatInvalid')
      continue
    }

    const text = textFromPayload(payload)
    const result = parseComplianceResult(text)
    if (!result) {
      lastError = t('novelStoryPage.messages.moderationResultParseFailed')
      continue
    }
    if (!result.allowed) {
      throw new Error(
        t('novelStoryPage.messages.moderationRejected', {
          reason: result.reason || t('novelStoryPage.messages.suspectedViolation'),
        }),
      )
    }
    return
  }

  throw new Error(lastError || t('novelStoryPage.messages.moderationFailed'))
}

async function uploadImageFileToMedia(file: File, category: string, altText: string): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', sanitizeUploadName(file.name))
  formData.append('category', category || 'other')
  formData.append('alt_text', String(altText || '').slice(0, 255))

  const payload: any = await client.post('/media/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  const result = resolveBackendMediaUrl(String(payload?.url || payload?.thumbnail_url || ''))
  if (!result) throw new Error(t('novelStoryPage.messages.mediaUploadNoUrl'))
  return result
}

async function processCustomImageUpload(
  file: File,
  options: {
    usageLabel: string
    category: string
    altText: string
    keywordText?: string
    errorRef: MessageRef
    infoRef: MessageRef
  }
): Promise<string | null> {
  options.errorRef.value = ''
  options.infoRef.value = ''

  if (!file) return null
  if (!CUSTOM_IMAGE_ALLOWED_TYPES.has(String(file.type || '').toLowerCase())) {
    options.errorRef.value = t('novelStoryPage.messages.imageTypeUnsupported')
    return null
  }
  if (Number(file.size) > CUSTOM_IMAGE_MAX_SIZE_BYTES) {
    options.errorRef.value = t('novelStoryPage.messages.imageTooLarge', { maxMb: 8 })
    return null
  }

  const blocked = findBlockedKeyword(`${file.name} ${options.altText || ''} ${options.keywordText || ''}`)
  if (blocked) {
    options.errorRef.value = t('novelStoryPage.messages.blockedKeywordDetected', { keyword: blocked })
    return null
  }

  isUploadingCustomImage.value = true
  try {
    const dataUrl = await fileToDataUrl(file)
    if (!dataUrl.startsWith('data:image/')) {
      throw new Error(t('novelStoryPage.messages.invalidImageData'))
    }
    const dimensions = await readImageDimensions(dataUrl)
    if (!dimensions.width || !dimensions.height) {
      throw new Error(t('novelStoryPage.messages.imageDimensionReadFailed'))
    }
    if (dimensions.width < CUSTOM_IMAGE_MIN_EDGE || dimensions.height < CUSTOM_IMAGE_MIN_EDGE) {
      throw new Error(t('novelStoryPage.messages.imageTooSmall', { min: CUSTOM_IMAGE_MIN_EDGE }))
    }
    if (dimensions.width > CUSTOM_IMAGE_MAX_EDGE || dimensions.height > CUSTOM_IMAGE_MAX_EDGE) {
      throw new Error(t('novelStoryPage.messages.imageTooLargeDimension', { max: CUSTOM_IMAGE_MAX_EDGE }))
    }

    await reviewImageComplianceByAI(dataUrl, options.usageLabel, file.name)

    try {
      const uploaded = await uploadImageFileToMedia(file, options.category, options.altText)
      options.infoRef.value = t('novelStoryPage.messages.imageReviewedSaved')
      return uploaded
    } catch (e: any) {
      const status = Number(e?.response?.status || 0)
      if (status === 401 || status === 403) {
        options.infoRef.value = t('novelStoryPage.messages.imageReviewedLoginFallback')
        return dataUrl
      }
      const message =
        e?.response?.data?.error ||
        e?.response?.data?.detail ||
        e?.message ||
        t('novelStoryPage.messages.imageUploadFailed')
      throw new Error(message)
    }
  } catch (e: any) {
    options.errorRef.value = e?.message || t('novelStoryPage.messages.imageUploadFailed')
    return null
  } finally {
    isUploadingCustomImage.value = false
  }
}

function openUploadPicker(input: HTMLInputElement | null) {
  if (!input || isUploadingCustomImage.value) return
  input.value = ''
  input.click()
}

function openCreationCoverUploadPicker() {
  openUploadPicker(creationCoverUploadInputRef.value)
}

function openCreationCharacterUploadPicker() {
  openUploadPicker(creationCharacterUploadInputRef.value)
}

function openCreationChapterUploadPicker() {
  openUploadPicker(creationChapterUploadInputRef.value)
}

function openWorkEditorCoverUploadPicker() {
  openUploadPicker(workEditorCoverUploadInputRef.value)
}

function openWorkEditorCharacterUploadPicker() {
  openUploadPicker(workEditorCharacterUploadInputRef.value)
}

function openSyncCharacterUploadPicker() {
  openUploadPicker(syncCharacterUploadInputRef.value)
}

async function handleCreationCoverUpload(event: Event) {
  const file = extractUploadFile(event)
  if (!file) return

  const src = await processCustomImageUpload(file, {
    usageLabel: '小说封面',
    category: 'banner',
    altText: `${plan.value?.title || storyTitle.value || t('novelStoryPage.creation.untitledWork')}封面`,
    keywordText: coverPrompt.value || defaultCoverPrompt(),
    errorRef: imageError,
    infoRef: imageInfo,
  })
  if (!src) return
  coverImage.value = resolveBackendMediaUrl(src)
  imageInfo.value = t('novelStoryPage.messages.customCoverSaved')
}

async function handleCreationCharacterUpload(event: Event) {
  const file = extractUploadFile(event)
  if (!file) return
  const target = selectedImageCharacter.value || activeChar.value
  if (!target) {
    imageError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  characterImageTargetId.value = target.id

  const src = await processCustomImageUpload(file, {
    usageLabel: `小说角色图：${target.name || t('novelStoryPage.creation.untitledCharacter')}`,
    category: 'other',
    altText: `${target.name || t('novelStoryPage.creation.untitledCharacter')}角色图`,
    keywordText: characterImagePrompt.value || defaultCharacterPrompt(target),
    errorRef: imageError,
    infoRef: imageInfo,
  })
  if (!src) return

  const item: CharacterImageAsset = {
    id: id('char_upload'),
    character_id: target.id,
    character_name: target.name || t('novelStoryPage.creation.untitledCharacter'),
    prompt: characterImagePrompt.value.trim() || defaultCharacterPrompt(target),
    image_url: resolveBackendMediaUrl(src),
    created_at: new Date().toISOString(),
  }
  const currentIndex = characterImages.value.findIndex((x) => x.character_id === target.id)
  if (currentIndex >= 0) {
    characterImages.value.splice(currentIndex, 1, item)
  } else {
    characterImages.value.unshift(item)
  }
  imageInfo.value = t('novelStoryPage.messages.customCharacterImageSaved', { name: item.character_name })
}

async function handleSyncCharacterUpload(event: Event) {
  const file = extractUploadFile(event)
  if (!file) return
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  const target = activeChar.value
  if (!target) {
    tavernSyncError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  characterImageTargetId.value = target.id

  const prompt = characterImagePrompt.value.trim() || defaultCharacterPrompt(target)
  const src = await processCustomImageUpload(file, {
    usageLabel: `角色卡图片：${target.name || t('novelStoryPage.creation.untitledCharacter')}`,
    category: 'other',
    altText: `${target.name || t('novelStoryPage.creation.untitledCharacter')}角色卡图片`,
    keywordText: prompt,
    errorRef: tavernSyncError,
    infoRef: tavernSyncInfo,
  })
  if (!src) return

  const item: CharacterImageAsset = {
    id: id('sync_char_upload'),
    character_id: target.id,
    character_name: target.name || t('novelStoryPage.creation.untitledCharacter'),
    prompt,
    image_url: resolveBackendMediaUrl(src),
    created_at: new Date().toISOString(),
  }
  const currentIndex = characterImages.value.findIndex((x) => x.character_id === target.id)
  if (currentIndex >= 0) {
    characterImages.value.splice(currentIndex, 1, item)
  } else {
    characterImages.value.unshift(item)
  }
  generatedCharacterCard.value = null
  tavernSyncInfo.value = tr(`已更新「${item.character_name}」角色卡图片。`, `Updated card image for "${item.character_name}".`)
}

async function handleCreationChapterUpload(event: Event) {
  const file = extractUploadFile(event)
  if (!file) return
  const chapterNo = Math.max(1, Number(activeChapterNo.value) || 1)

  const src = await processCustomImageUpload(file, {
    usageLabel: `小说章节配图：第${chapterNo}章`,
    category: 'other',
    altText: `第${chapterNo}章配图`,
    keywordText: chapterImagePrompt.value || defaultChapterPrompt(chapterNo),
    errorRef: imageError,
    infoRef: imageInfo,
  })
  if (!src) return

  const item: ChapterImageAsset = {
    id: id('chapter_upload'),
    chapter_no: chapterNo,
    chapter_title: chapterTitle(chapterNo),
    prompt: chapterImagePrompt.value.trim() || defaultChapterPrompt(chapterNo),
    image_url: resolveBackendMediaUrl(src),
    created_at: new Date().toISOString(),
  }
  const currentIndex = chapterImages.value.findIndex((x) => x.chapter_no === chapterNo)
  if (currentIndex >= 0) {
    chapterImages.value.splice(currentIndex, 1, item)
  } else {
    chapterImages.value.unshift(item)
  }
  chapterImages.value = [...chapterImages.value].sort((a, b) => a.chapter_no - b.chapter_no)
  imageInfo.value = t('novelStoryPage.messages.customChapterImageSaved', { no: chapterNo })
}

async function handleWorkEditorCoverUpload(event: Event) {
  const file = extractUploadFile(event)
  if (!file) return
  const src = await processCustomImageUpload(file, {
    usageLabel: '作品库封面',
    category: 'banner',
    altText: `${workEditorTitle.value || selectedWork.value?.title || t('novelStoryPage.creation.untitledWork')}封面`,
    keywordText: workEditorCoverPrompt.value,
    errorRef: workEditorError,
    infoRef: workEditorInfo,
  })
  if (!src) return
  workEditorCoverImage.value = resolveBackendMediaUrl(src)
  workEditorInfo.value = t('novelStoryPage.messages.customWorkCoverSaved')
}

async function handleWorkEditorCharacterUpload(event: Event) {
  const file = extractUploadFile(event)
  if (!file) return
  const target = workEditorCharacters.value.find((item) => item.id === workEditorCharacterTargetId.value) || null
  if (!target) {
    workEditorError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }

  const src = await processCustomImageUpload(file, {
    usageLabel: `作品库人物图：${target.name || t('novelStoryPage.creation.untitledCharacter')}`,
    category: 'other',
    altText: `${target.name || t('novelStoryPage.creation.untitledCharacter')}人物图`,
    keywordText:
      workEditorCharacterPrompt.value.trim() ||
      `为小说《${workEditorTitle.value || selectedWork.value?.title || t('novelStoryPage.creation.untitledWork')}》角色“${target.name || t('novelStoryPage.creation.untitledCharacter')}”上传人物图`,
    errorRef: workEditorError,
    infoRef: workEditorInfo,
  })
  if (!src) return

  const item: CharacterImageAsset = {
    id: id('work_char_upload'),
    character_id: target.id,
    character_name: target.name || t('novelStoryPage.creation.untitledCharacter'),
    prompt: workEditorCharacterPrompt.value.trim(),
    image_url: resolveBackendMediaUrl(src),
    created_at: new Date().toISOString(),
  }
  const idx = workEditorCharacterImages.value.findIndex((x) => x.character_id === target.id)
  if (idx >= 0) {
    workEditorCharacterImages.value.splice(idx, 1, item)
  } else {
    workEditorCharacterImages.value.unshift(item)
  }
  workEditorInfo.value = t('novelStoryPage.messages.customCharacterImageSaved', { name: item.character_name })
}

function id(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

function randomClientId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID().replace(/-/g, '').slice(0, 32)
  }
  return `${Date.now()}${Math.random().toString(36).slice(2, 12)}`
}

function ensureDraftClientId(): string {
  let clientId = ''
  try {
    clientId = String(localStorage.getItem(DRAFT_CLIENT_KEY) || '').trim()
    if (!clientId) {
      clientId = randomClientId()
      localStorage.setItem(DRAFT_CLIENT_KEY, clientId)
    }
  } catch {
    clientId = randomClientId()
  }
  return clientId.slice(0, 64)
}

function deepClone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value ?? null)) as T
}

function characterSignature(list: Character[]): string {
  return list
    .map((item) => [item.name || '', item.role || '', item.personality || '', item.goal || '', item.arc || ''].join('|'))
    .join('||')
}

function normalizeCharacters(raw: any): Character[] {
  if (!Array.isArray(raw) || raw.length === 0) {
    return [{
      id: id('c'),
      name: t('novelStoryPage.sync.defaultCharacterName'),
      role: t('novelStoryPage.sync.defaultCharacterRole'),
      personality: t('novelStoryPage.sync.defaultCharacterPersonality'),
      goal: '',
      arc: '',
    }]
  }
  const normalized = raw.map((c: any) => ({
    id: String(c?.id || id('c')),
    name: String(c?.name || t('novelStoryPage.creation.untitledCharacter')),
    role: String(c?.role || ''),
    personality: String(c?.personality || ''),
    goal: String(c?.goal || ''),
    arc: String(c?.arc || ''),
  }))
  return normalized.length > 0
    ? normalized
    : [{
        id: id('c'),
        name: t('novelStoryPage.sync.defaultCharacterName'),
        role: t('novelStoryPage.sync.defaultCharacterRole'),
        personality: t('novelStoryPage.sync.defaultCharacterPersonality'),
        goal: '',
        arc: '',
      }]
}

function normalizeMessages(raw: any): Msg[] {
  if (!Array.isArray(raw)) return []
  const allowedRoles: MsgRole[] = ['user', 'assistant', 'system']
  return raw
    .map((m: any) => ({
      id: String(m?.id || id('m')),
      role: allowedRoles.includes(m?.role) ? m.role : 'user',
      content: String(m?.content || ''),
    }))
    .filter((m) => m.content.trim().length > 0)
    .slice(-60)
}

function normalizeDraftChapters(raw: any): DraftChapter[] {
  if (!Array.isArray(raw)) return []
  const normalized = raw
    .map((item: any, index: number) => ({
      chapter_no: Math.max(1, Number(item?.chapter_no) || index + 1),
      title: String(item?.title || `第${index + 1}章`),
      summary: String(item?.summary || ''),
      content: String(item?.content || ''),
      updated_at: String(item?.updated_at || ''),
    }))
    .filter((x) => x.content.trim().length > 0)
  return normalized.sort((a, b) => a.chapter_no - b.chapter_no)
}

function normalizeCharacterImages(raw: any): CharacterImageAsset[] {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item: any, index: number) => ({
      id: String(item?.id || id(`char_img_${index}`)),
      character_id: String(item?.character_id || item?.characterId || ''),
      character_name: String(item?.character_name || item?.characterName || item?.name || ''),
      prompt: String(item?.prompt || ''),
      image_url: resolveBackendMediaUrl(String(item?.image_url || item?.url || item?.src || '')),
      created_at: String(item?.created_at || ''),
    }))
    .filter((item: CharacterImageAsset) => item.image_url.trim().length > 0)
}

function normalizeChapterImages(raw: any): ChapterImageAsset[] {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item: any, index: number) => ({
      id: String(item?.id || id(`chapter_img_${index}`)),
      chapter_no: Math.max(1, Number(item?.chapter_no) || index + 1),
      chapter_title: String(item?.chapter_title || item?.chapterTitle || ''),
      prompt: String(item?.prompt || ''),
      image_url: resolveBackendMediaUrl(String(item?.image_url || item?.url || item?.src || '')),
      created_at: String(item?.created_at || ''),
    }))
    .filter((item: ChapterImageAsset) => item.image_url.trim().length > 0)
    .sort((a, b) => a.chapter_no - b.chapter_no)
}

function normalizeWork(raw: any): NovelWork {
  const outlineCount = Array.isArray(raw?.plan?.chapter_outlines) ? raw.plan.chapter_outlines.length : undefined
  const normalizedPlan = raw?.plan && typeof raw.plan === 'object' ? normalizePlan(raw.plan, outlineCount) : null
  return {
    id: Number(raw?.id) || 0,
    title: String(raw?.title || t('novelStoryPage.creation.untitledWork')),
    summary: String(raw?.summary || ''),
    plan: normalizedPlan,
    chapters: normalizeDraftChapters(raw?.chapters),
    cover_image: resolveBackendMediaUrl(String(raw?.cover_image || raw?.coverImage || '')),
    character_images: normalizeCharacterImages(raw?.character_images),
    chapter_images: normalizeChapterImages(raw?.chapter_images),
    extra_meta: raw?.extra_meta && typeof raw.extra_meta === 'object' ? raw.extra_meta : {},
    created_at: String(raw?.created_at || ''),
    updated_at: String(raw?.updated_at || ''),
  }
}

function formatTime(value: string): string {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function buildDraftState() {
  return {
    tab: tab.value,
    creationMode: creationMode.value,
    idea: idea.value,
    genre: genre.value,
    tone: tone.value,
    setting: setting.value,
    chapterCount: chapterCount.value,
    lightContinuationCount: lightContinuationCount.value,
    plan: plan.value || null,
    activeChapterNo: activeChapterNo.value,
    targetWords: targetWords.value,
    continuationHint: continuationHint.value,
    chapters: chapters.value,
    chapterHistory: chapterHistory.value.slice(-24),
    bookStatus: bookStatus.value,
    storyTitle: storyTitle.value,
    worldContext: worldContext.value,
    currentSituation: currentSituation.value,
    characters: characters.value.map((c) => ({
      id: c.id,
      name: c.name,
      role: c.role,
      personality: c.personality,
      goal: c.goal || '',
      arc: c.arc || '',
    })),
    activeId: activeId.value,
    messages: messages.value.slice(-60),
    selectedWorkId: selectedWorkId.value,
    coverPrompt: coverPrompt.value,
    coverImage: coverImage.value,
    characterImagePrompt: characterImagePrompt.value,
    characterImageTargetId: characterImageTargetId.value,
    chapterImagePrompt: chapterImagePrompt.value,
    characterImages: characterImages.value,
    chapterImages: chapterImages.value,
    tavernGroup: tavernGroup.value,
    worldBookNotes: worldBookNotes.value,
    tavernSecondaryPrompt: tavernSecondaryPrompt.value,
    tavernImportMode: tavernImportMode.value,
  }
}

function applyDraftState(rawState: any) {
  if (!rawState || typeof rawState !== 'object') return

  const restoredCount = Math.max(
    1,
    Math.min(
      24,
      Number(rawState.chapterCount) ||
        (Array.isArray(rawState.plan?.chapter_outlines) ? rawState.plan.chapter_outlines.length : chapterCount.value)
    )
  )

  idea.value = String(rawState.idea || '')
  genre.value = String(rawState.genre || '')
  tone.value = String(rawState.tone || '')
  setting.value = String(rawState.setting || '')
  creationMode.value = rawState.creationMode === 'light' ? 'light' : 'professional'
  chapterCount.value = restoredCount
  lightContinuationCount.value = Math.max(1, Math.min(12, Number(rawState.lightContinuationCount) || lightContinuationCount.value))
  plan.value = rawState.plan && typeof rawState.plan === 'object' ? normalizePlan(rawState.plan, restoredCount) : null

  storyTitle.value = String(rawState.storyTitle || storyTitle.value)
  worldContext.value = String(rawState.worldContext || '')
  currentSituation.value = String(rawState.currentSituation || '')
  targetWords.value = clampWords(Number(rawState.targetWords) || targetWords.value)
  continuationHint.value = String(rawState.continuationHint || '')
  chapters.value = normalizeDraftChapters(rawState.chapters)
  chapterHistory.value = Array.isArray(rawState.chapterHistory)
    ? rawState.chapterHistory
        .map((item: any) => ({
          id: String(item?.id || id('history')),
          reason: String(item?.reason || t('novelStoryPage.messages.historySnapshot')),
          created_at: String(item?.created_at || ''),
          active_chapter_no: Math.max(1, Number(item?.active_chapter_no) || 1),
          chapters: normalizeDraftChapters(item?.chapters),
          plan: item?.plan && typeof item.plan === 'object' ? normalizePlan(item.plan, Array.isArray(item.plan?.chapter_outlines) ? item.plan.chapter_outlines.length : undefined) : null,
        }))
        .slice(-24)
    : []
  bookStatus.value = rawState.bookStatus === 'completed' ? 'completed' : 'draft'
  activeChapterNo.value = Math.max(1, Math.min(chapterCount.value, Number(rawState.activeChapterNo) || 1))

  characters.value = normalizeCharacters(rawState.characters)
  activeId.value = characters.value.find((x) => x.id === rawState.activeId)?.id || characters.value[0].id
  messages.value = normalizeMessages(rawState.messages)
  selectedWorkId.value =
    rawState.selectedWorkId === null || rawState.selectedWorkId === undefined
      ? null
      : Math.max(1, Number(rawState.selectedWorkId) || 0) || null
  coverPrompt.value = String(rawState.coverPrompt || '')
  coverImage.value = resolveBackendMediaUrl(String(rawState.coverImage || ''))
  characterImagePrompt.value = String(rawState.characterImagePrompt || '')
  characterImageTargetId.value = String(rawState.characterImageTargetId || '')
  chapterImagePrompt.value = String(rawState.chapterImagePrompt || '')
  characterImages.value = normalizeCharacterImages(rawState.characterImages)
  chapterImages.value = normalizeChapterImages(rawState.chapterImages)
  tavernGroup.value = String(rawState.tavernGroup || tavernGroup.value || t('novelStoryPage.sync.defaultTavernGroup'))
  worldBookNotes.value = String(rawState.worldBookNotes || '')
  tavernSecondaryPrompt.value = String(rawState.tavernSecondaryPrompt || '')
  tavernImportMode.value = rawState.tavernImportMode === 'replace' ? 'replace' : 'append'
  if (!characterImageTargetId.value && characters.value.length > 0) {
    characterImageTargetId.value = characters.value[0].id
  }
  const rawTab = String(rawState.tab || '')
  if (rawTab === 'creation' || rawTab === 'works' || rawTab === 'sync') {
    tab.value = rawTab
  } else if (rawTab === 'roleplay') {
    tab.value = 'sync'
  } else {
    tab.value = 'creation'
  }
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)
}

function queueDraftSave() {
  if (draftHydrating.value || draftLoading.value) return
  if (draftSaveTimer) clearTimeout(draftSaveTimer)
  draftSaveTimer = setTimeout(() => {
    draftSaveTimer = null
    void saveDraft()
  }, 1200)
}

function buildEmptyDraftState() {
  const seedCharacter: Character = {
    id: id('c'),
    name: t('novelStoryPage.sync.defaultCharacterName'),
    role: t('novelStoryPage.sync.defaultCharacterRole'),
    personality: t('novelStoryPage.sync.defaultCharacterPersonality'),
    goal: '',
    arc: '',
  }
  return {
    tab: 'creation',
    creationMode: 'professional',
    idea: '',
    genre: '',
    tone: '',
    setting: '',
    chapterCount: 8,
    lightContinuationCount: 5,
    plan: null,
    activeChapterNo: 1,
    targetWords: 1800,
    continuationHint: '',
    chapters: [],
    chapterHistory: [],
    bookStatus: 'draft',
    storyTitle: t('novelStoryPage.sync.defaultStoryTitle'),
    worldContext: '',
    currentSituation: '',
    characters: [seedCharacter],
    activeId: seedCharacter.id,
    messages: [],
    selectedWorkId: null,
    coverPrompt: '',
    coverImage: '',
    characterImagePrompt: '',
    characterImageTargetId: seedCharacter.id,
    chapterImagePrompt: '',
    characterImages: [],
    chapterImages: [],
    tavernGroup: t('novelStoryPage.sync.defaultTavernGroup'),
    worldBookNotes: '',
    tavernSecondaryPrompt: '',
    tavernImportMode: 'append',
  }
}

async function clearDraftOneClick() {
  draftError.value = ''
  draftInfo.value = ''
  if (!window.confirm(t('novelStoryPage.messages.confirmClearDraft'))) return

  if (draftSaveTimer) {
    clearTimeout(draftSaveTimer)
    draftSaveTimer = null
  }

  draftHydrating.value = true
  try {
    applyDraftState(buildEmptyDraftState())
    workshopError.value = ''
    chapterError.value = ''
    chapterInfo.value = ''
    roleplayError.value = ''
    plotInstruction.value = ''
    imageError.value = ''
    imageInfo.value = ''
    worksError.value = ''
    worksInfo.value = ''
    tavernSyncError.value = ''
    tavernSyncInfo.value = ''
    tavernImportError.value = ''
    tavernImportInfo.value = ''
    generatedCharacterCard.value = null
  } finally {
    draftHydrating.value = false
  }

  draftSaving.value = true
  try {
    await client.post('/novel-drafts/current/', {
      client_id: ensureDraftClientId(),
      title: t('novelStoryPage.sync.defaultStoryTitle'),
      state: buildDraftState(),
    })
    draftInfo.value = t('novelStoryPage.messages.draftCleared')
  } catch (e: any) {
    draftError.value = e?.response?.data?.detail || e?.message || t('novelStoryPage.messages.clearDraftFailed')
  } finally {
    draftSaving.value = false
  }
}

async function loadDraft() {
  draftError.value = ''
  draftInfo.value = ''
  draftLoading.value = true
  draftHydrating.value = true
  try {
    const payload: any = await client.get('/novel-drafts/current/', {
      params: { client_id: ensureDraftClientId() },
    })
    if (payload?.state && typeof payload.state === 'object') {
      applyDraftState(payload.state)
    }
  } catch (e: any) {
    if (e?.response?.status !== 404) {
      draftError.value = e?.response?.data?.detail || e?.message || t('novelStoryPage.messages.loadDraftFailed')
    }
  } finally {
    draftHydrating.value = false
    draftLoading.value = false
  }
}

async function saveDraft() {
  if (draftHydrating.value || draftLoading.value) return
  draftSaving.value = true
  draftError.value = ''
  try {
    const title = String(plan.value?.title || storyTitle.value || t('novelStoryPage.sync.defaultStoryTitle')).slice(0, 200)
    await client.post('/novel-drafts/current/', {
      client_id: ensureDraftClientId(),
      title,
      state: buildDraftState(),
    })
  } catch (e: any) {
    draftError.value = e?.response?.data?.detail || e?.message || t('novelStoryPage.messages.saveDraftFailed')
  } finally {
    draftSaving.value = false
  }
}

function buildWorkPayload(statusOverride?: 'draft' | 'completed') {
  const title = String(plan.value?.title || storyTitle.value || t('novelStoryPage.creation.untitledWork')).slice(0, 200)
  const effectivePlan = plan.value ? deepClone(plan.value) : normalizePlan({ title, genre: genre.value, tone: tone.value, setting: setting.value, core_conflict: idea.value }, chapterCount.value)
  effectivePlan.characters = characters.value.map((c) => ({
    name: String(c.name || t('novelStoryPage.creation.untitledCharacter')),
    role: String(c.role || ''),
    goal: String(c.goal || ''),
    arc: String(c.arc || c.personality || ''),
  }))
  return {
    client_id: ensureDraftClientId(),
    title,
    summary: compactText(String(plan.value?.core_conflict || idea.value || worldContext.value || '')),
    plan: effectivePlan,
    chapters: chapters.value,
    cover_image: coverImage.value,
    character_images: characterImages.value,
    chapter_images: chapterImages.value,
    extra_meta: {
      draft_state: buildDraftState(),
      creation_mode: creationMode.value,
      completion_status: statusOverride || bookStatus.value,
      character_profiles: characters.value.map((c) => ({
        id: c.id,
        name: c.name,
        role: c.role,
        personality: c.personality,
        goal: c.goal || '',
        arc: c.arc || '',
      })),
      chapter_history: chapterHistory.value.slice(-24),
      last_saved_at: new Date().toISOString(),
    },
  }
}

function formatApiError(error: any, fallback = t('novelStoryPage.messages.requestFailed')): string {
  const data = error?.response?.data
  if (!data) return error?.message || fallback
  if (typeof data === 'string') return data
  if (typeof data?.detail === 'string') return data.detail
  if (typeof data?.message === 'string') return data.message
  if (Array.isArray(data)) return data.map((item: any) => String(item)).join('；')

  const chunks: string[] = []
  Object.entries(data).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      chunks.push(`${key}: ${value.map((item) => String(item)).join('、')}`)
      return
    }
    if (value && typeof value === 'object') {
      chunks.push(`${key}: ${JSON.stringify(value)}`)
      return
    }
    chunks.push(`${key}: ${String(value)}`)
  })
  return chunks.join('；') || error?.message || fallback
}

async function loadWorks() {
  worksError.value = ''
  worksLoading.value = true
  try {
    const payload: any = await client.get('/novel-works/', {
      params: { client_id: ensureDraftClientId() },
    })
    const rawItems = Array.isArray(payload) ? payload : (Array.isArray(payload?.results) ? payload.results : [])
    works.value = rawItems.map((item: any) => normalizeWork(item)).filter((item: NovelWork) => item.id > 0)
    if (selectedWorkId.value && !works.value.some((item) => item.id === selectedWorkId.value)) {
      selectedWorkId.value = null
      selectedWorkChapterNo.value = null
    }
  } catch (e: any) {
    worksError.value = e?.response?.data?.detail || e?.message || t('novelStoryPage.works.worksLoadFailed')
  } finally {
    worksLoading.value = false
  }
}

function startNewWork() {
  selectedWorkId.value = null
  selectedWorkChapterNo.value = null
  bookStatus.value = 'draft'
  chapterHistory.value = []
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)
  worksInfo.value = t('novelStoryPage.works.switchedToNewWork')
  workEditorTitle.value = ''
  workEditorSummary.value = ''
  workEditorNotes.value = ''
  workEditorCoverPrompt.value = ''
  workEditorCoverImage.value = ''
  workEditorCharacters.value = []
  workEditorCharacterImages.value = []
  workEditorCharacterTargetId.value = ''
  workEditorCharacterPrompt.value = ''
}

function selectWork(work: NovelWork) {
  selectedWorkId.value = work.id
  selectedWorkChapterNo.value = work.chapters[0]?.chapter_no || null
  hydrateWorkEditorFromWork(work)
  worksInfo.value = t('novelStoryPage.works.selectedWorkInfo', {
    title: work.title || t('novelStoryPage.works.untitledWork'),
  })
}

function openWork(work: NovelWork) {
  selectedWorkId.value = work.id
  selectedWorkChapterNo.value = work.chapters[0]?.chapter_no || null
  if (work.extra_meta?.draft_state && typeof work.extra_meta.draft_state === 'object') {
    applyDraftState(work.extra_meta.draft_state)
  } else {
    if (work.plan && typeof work.plan === 'object') {
      plan.value = normalizePlan(work.plan, Array.isArray(work.plan.chapter_outlines) ? work.plan.chapter_outlines.length : chapterCount.value)
      chapterCount.value = plan.value.chapter_outlines.length
    } else {
      plan.value = null
    }
    chapters.value = normalizeDraftChapters(work.chapters)
    storyTitle.value = work.title || storyTitle.value
    activeChapterNo.value = Math.max(1, Math.min(chapterCount.value, Number(activeChapterNo.value) || 1))
    const sourceCharacters =
      Array.isArray(work.extra_meta?.character_profiles) && work.extra_meta.character_profiles.length > 0
        ? work.extra_meta.character_profiles
        : work.plan?.characters || []
    if (Array.isArray(sourceCharacters) && sourceCharacters.length > 0) {
      characters.value = normalizeCharacters(sourceCharacters)
      activeId.value = characters.value[0]?.id || activeId.value
    }
  }
  selectedWorkId.value = work.id

  coverImage.value = resolveBackendMediaUrl(String(work.cover_image || ''))
  characterImages.value = normalizeCharacterImages(work.character_images)
  chapterImages.value = normalizeChapterImages(work.chapter_images)
  chapterHistory.value = Array.isArray(work.extra_meta?.chapter_history)
    ? work.extra_meta.chapter_history
        .map((item: any) => ({
          id: String(item?.id || id('history')),
          reason: String(item?.reason || t('novelStoryPage.messages.historySnapshot')),
          created_at: String(item?.created_at || ''),
          active_chapter_no: Math.max(1, Number(item?.active_chapter_no) || 1),
          chapters: normalizeDraftChapters(item?.chapters),
          plan: item?.plan && typeof item.plan === 'object' ? normalizePlan(item.plan, Array.isArray(item.plan?.chapter_outlines) ? item.plan.chapter_outlines.length : undefined) : null,
        }))
        .slice(-24)
    : chapterHistory.value
  creationMode.value = String(work.extra_meta?.creation_mode || '').toLowerCase() === 'light' ? 'light' : 'professional'
  bookStatus.value = String(work.extra_meta?.completion_status || '').toLowerCase() === 'completed' ? 'completed' : 'draft'
  if (!characterImageTargetId.value && characters.value.length > 0) {
    characterImageTargetId.value = characters.value[0].id
  }
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)
  hydrateWorkEditorFromWork(work)
  worksInfo.value = t('novelStoryPage.works.openedWorkInfo', {
    title: work.title || t('novelStoryPage.works.untitledWork'),
  })
}

function openWorkInCreation(work: NovelWork) {
  openWork(work)
  tab.value = 'creation'
}

async function saveCurrentWork(options?: { forceStatus?: 'draft' | 'completed'; successMessage?: string; forceCreate?: boolean }) {
  worksError.value = ''
  worksInfo.value = ''
  worksSaving.value = true
  const originalStatus = bookStatus.value
  const targetStatus = options?.forceStatus || originalStatus
  const shouldCreate = Boolean(options?.forceCreate) || !selectedWorkId.value
  const targetWorkId = Number(selectedWorkId.value || 0)
  if (options?.forceStatus) {
    bookStatus.value = options.forceStatus
  }
  try {
    const hasExisting = !shouldCreate && targetWorkId > 0
    const payload = buildWorkPayload(targetStatus)
    let saved: any
    if (hasExisting) {
      saved = await client.patch(`/novel-works/${targetWorkId}/`, payload)
    } else {
      saved = await client.post('/novel-works/', payload)
    }

    const normalized = normalizeWork(saved)
    if (normalized.id > 0) {
      const currentIndex = works.value.findIndex((item) => item.id === normalized.id)
      if (currentIndex >= 0) {
        works.value.splice(currentIndex, 1, normalized)
      } else {
        works.value.unshift(normalized)
      }
      works.value = [...works.value].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
      selectedWorkId.value = normalized.id
      hydrateWorkEditorFromWork(normalized)
    }

    worksInfo.value =
      options?.successMessage ||
      (hasExisting
        ? t('novelStoryPage.works.workUpdated')
        : t('novelStoryPage.works.workCreated'))
    return true
  } catch (e: any) {
    worksError.value = formatApiError(e, t('novelStoryPage.works.workSaveFailed'))
    if (options?.forceStatus) {
      bookStatus.value = originalStatus
    }
    return false
  } finally {
    worksSaving.value = false
    await loadWorks()
  }
}

async function saveAsSerialDraft() {
  const saved = await saveCurrentWork({
    forceStatus: 'draft',
    successMessage: selectedWorkId.value
      ? t('novelStoryPage.works.serialUpdatedSaved')
      : t('novelStoryPage.works.serialCreatedSaved'),
  })
  if (!saved && !worksError.value) {
    worksError.value = t('novelStoryPage.works.serialSaveFailed')
  }
}

async function saveAsNewWork() {
  const saved = await saveCurrentWork({
    forceCreate: true,
    successMessage: t('novelStoryPage.works.newWorkSaved'),
  })
  if (!saved && !worksError.value) {
    worksError.value = t('novelStoryPage.works.newWorkSaveFailed')
  }
}

async function deleteWork(work: NovelWork) {
  if (!work?.id) return
  if (
    !window.confirm(
      t('novelStoryPage.works.confirmDeleteWork', {
        title: work.title || t('novelStoryPage.works.untitledWork'),
      }),
    )
  )
    return

  worksError.value = ''
  worksInfo.value = ''
  try {
    await client.delete(`/novel-works/${work.id}/`, {
      params: { client_id: ensureDraftClientId() },
    })
    works.value = works.value.filter((item) => item.id !== work.id)
    if (selectedWorkId.value === work.id) {
      selectedWorkId.value = null
      selectedWorkChapterNo.value = null
    }
    worksInfo.value = t('novelStoryPage.works.workDeleted')
  } catch (e: any) {
    worksError.value =
      e?.response?.data?.detail ||
      e?.message ||
      t('novelStoryPage.works.workDeleteFailed')
  }
}

function clampWords(value: number): number {
  const numeric = Number(value) || 1800
  return Math.max(600, Math.min(5000, Math.round(numeric)))
}

function chapterOutline(chapterNo: number) {
  return plan.value?.chapter_outlines.find((x) => Number(x.chapter_no) === Number(chapterNo))
}

function chapterTitle(chapterNo: number): string {
  return String(
    chapterOutline(chapterNo)?.title ||
      t('novelStoryPage.creation.chapterDefaultTitle', {
        no: chapterNo,
      }),
  )
}

function compactText(text: string, max = 240): string {
  const oneLine = String(text || '').replace(/\s+/g, ' ').trim()
  if (!oneLine) return ''
  return oneLine.length > max ? `${oneLine.slice(0, max)}...` : oneLine
}

function syncPlanCharactersFromEditor() {
  if (!plan.value) return
  const nextCharacters = characters.value.map((c) => ({
    name: String(c.name || t('novelStoryPage.creation.untitledCharacter')),
    role: String(c.role || ''),
    goal: String(c.goal || ''),
    arc: String(c.arc || c.personality || ''),
  }))
  plan.value = {
    ...plan.value,
    characters: nextCharacters,
  }
}

function saveChapterSnapshot(reason: string) {
  const snapshot: ChapterHistorySnapshot = {
    id: id('chapter_snapshot'),
    reason: String(reason || t('novelStoryPage.messages.chapterOperation')),
    created_at: new Date().toISOString(),
    active_chapter_no: Math.max(1, Number(activeChapterNo.value) || 1),
    chapters: deepClone(chapters.value),
    plan: plan.value ? deepClone(plan.value) : null,
  }
  chapterHistory.value.push(snapshot)
  if (chapterHistory.value.length > 24) {
    chapterHistory.value.splice(0, chapterHistory.value.length - 24)
  }
}

function rollbackChapterGeneration() {
  chapterError.value = ''
  chapterInfo.value = ''
  const snapshot = chapterHistory.value.pop()
  if (!snapshot) {
    chapterError.value = t('novelStoryPage.messages.rollbackNoHistory')
    return
  }
  chapters.value = normalizeDraftChapters(snapshot.chapters)
  if (snapshot.plan) {
    const count = Array.isArray(snapshot.plan.chapter_outlines) ? snapshot.plan.chapter_outlines.length : chapterCount.value
    chapterCount.value = Math.max(1, Math.min(24, Number(count) || chapterCount.value))
    plan.value = normalizePlan(snapshot.plan, chapterCount.value)
  }
  activeChapterNo.value = Math.max(1, Number(snapshot.active_chapter_no) || 1)
  chapterInfo.value = t('novelStoryPage.messages.rollbackDone', {
    reason: snapshot.reason,
  })
}

function sortedChapters(): DraftChapter[] {
  return [...chapters.value].sort((a, b) => a.chapter_no - b.chapter_no)
}

function chapterByNo(chapterNo: number): DraftChapter | null {
  return chapters.value.find((x) => x.chapter_no === chapterNo) || null
}

function recentChapterContext(limit = 6): string {
  const recent = sortedChapters().slice(-limit)
  if (recent.length === 0) return t('novelStoryPage.messages.noCompletedChapterYet')
  return recent
    .map((c) => {
      const summary = c.summary || compactText(c.content, 200)
      return t('novelStoryPage.messages.chapterContextLine', {
        no: c.chapter_no,
        title: c.title,
        summary: summary || t('novelStoryPage.creation.noSummary'),
      })
    })
    .join('\n')
}

function applyChapter(chapterNo: number, content: string, append = false) {
  const cleaned = String(content || '').trim()
  if (!cleaned) return
  if (bookStatus.value === 'completed') {
    bookStatus.value = 'draft'
  }
  const title = chapterTitle(chapterNo)
  const now = new Date().toISOString()
  const existing = chapterByNo(chapterNo)
  if (!existing) {
    chapters.value.push({
      chapter_no: chapterNo,
      title,
      summary: compactText(cleaned, 220),
      content: cleaned,
      updated_at: now,
    })
    chapters.value = sortedChapters()
    return
  }

  const merged = append ? `${existing.content}\n\n${cleaned}` : cleaned
  const mergedTitle = title || existing.title
  chapters.value = chapters.value.map((x) =>
    x.chapter_no === chapterNo
      ? {
          ...x,
          title: mergedTitle,
          summary: compactText(merged, 220),
          content: merged,
          updated_at: now,
        }
      : x
  )
  chapters.value = sortedChapters()
}

function chapterWritingPrompt(chapterNo: number, mode: 'write' | 'continue'): string {
  const p = plan.value
  const outline = chapterOutline(chapterNo)
  const current = chapterByNo(chapterNo)
  const previous = chapterByNo(Math.max(1, chapterNo - 1))
  const words = clampWords(targetWords.value)
  targetWords.value = words
  const toneText = p?.tone || '中文网络小说风格'
  const extraHint = continuationHint.value.trim()
  const writingCast =
    characters.value.length > 0
      ? characters.value.map((x) => ({
          name: x.name || '',
          role: x.role || '',
          goal: x.goal || '',
          arc: x.arc || x.personality || '',
          personality: x.personality || '',
        }))
      : p?.characters || []
  const cast = writingCast
    .map((x: any) =>
      `- ${x.name || '未命名角色'}：${x.role || '未设定'}；性格：${x.personality || '未设定'}；目标：${x.goal || '未设定'}；人物弧线：${x.arc || '未设定'}`
    )
    .join('\n')

  if (mode === 'continue') {
    return [
      '请续写同一章节的小说正文。',
      '输出要求：仅输出续写正文，不要标题、不要分点、不要解释、不要 Markdown。',
      `续写目标字数：约 ${Math.max(500, Math.round(words * 0.65))} 字。`,
      `故事标题：${p?.title || storyTitle.value || '未命名作品'}`,
      `题材：${p?.genre || genre.value || '未设定'}`,
      `文风：${toneText}`,
      p?.setting ? `世界观：${p.setting}` : '',
      p?.core_conflict ? `核心冲突：${p.core_conflict}` : '',
      cast ? `主要角色：\n${cast}` : '',
      outline ? `当前章节：第${chapterNo}章《${outline.title || chapterTitle(chapterNo)}》` : `当前章节：第${chapterNo}章`,
      outline?.summary ? `本章目标：${outline.summary}` : '',
      outline?.twist ? `本章转折：${outline.twist}` : '',
      previous?.content ? `上一章结尾（节选）：${previous.content.slice(-600)}` : '',
      '以下是已写内容，请从最后一句自然衔接，不要复述前文。',
      current?.content || '',
      extraHint ? `附加续写要求：${extraHint}` : '',
    ]
      .filter(Boolean)
      .join('\n\n')
  }

  return [
    `请创作小说第${chapterNo}章的完整正文。`,
    '输出要求：只输出正文，不要解释写作思路，不要大纲，不要 Markdown。',
    `目标字数：约 ${words} 字（允许上下浮动约 15%）。`,
    `故事标题：${p?.title || storyTitle.value || '未命名作品'}`,
    `题材：${p?.genre || genre.value || '未设定'}`,
    `文风：${toneText}`,
    p?.setting ? `世界观：${p.setting}` : '',
    p?.core_conflict ? `核心冲突：${p.core_conflict}` : '',
    cast ? `主要角色：\n${cast}` : '',
    outline ? `当前章节：第${chapterNo}章《${outline.title || chapterTitle(chapterNo)}》` : `当前章节：第${chapterNo}章`,
    outline?.summary ? `本章目标：${outline.summary}` : '',
    outline?.twist ? `本章转折：${outline.twist}` : '',
    `已写章节摘要：\n${recentChapterContext()}`,
    previous?.content ? `上一章结尾（节选）：${previous.content.slice(-800)}` : '',
    extraHint ? `附加写作要求：${extraHint}` : '',
  ]
    .filter(Boolean)
    .join('\n\n')
}

async function ensurePlanChapterOutlines(requiredCount: number) {
  const target = Math.max(1, Math.min(24, Number(requiredCount) || 1))
  if (!plan.value) {
    plan.value = normalizePlan(
      {
        title: storyTitle.value || t('novelStoryPage.creation.untitledWork'),
        genre: genre.value || '',
        tone: tone.value || '',
        setting: setting.value || '',
        core_conflict: compactText(String(idea.value || worldContext.value || ''), 220),
        characters: characters.value.map((c) => ({
          name: c.name || t('novelStoryPage.creation.untitledCharacter'),
          role: c.role || '',
          goal: c.goal || '',
          arc: c.arc || c.personality || '',
        })),
        chapter_outlines: [],
      },
      target
    )
    chapterCount.value = target
    return
  }

  if (plan.value.chapter_outlines.length >= target) return
  const currentCount = plan.value.chapter_outlines.length
  chapterCount.value = target
  try {
    const prompt = [
      '请补全小说后续章节大纲，返回严格 JSON。',
      `当前已规划章节数：${currentCount}`,
      `目标章节数：${target}`,
      `故事标题：${plan.value.title || storyTitle.value || '未命名作品'}`,
      `题材：${plan.value.genre || genre.value || '未设定'}`,
      `文风：${plan.value.tone || tone.value || '未设定'}`,
      plan.value.core_conflict ? `核心冲突：${plan.value.core_conflict}` : '',
      `已有大纲：${JSON.stringify(plan.value.chapter_outlines)}`,
      '输出字段：chapter_outlines（每章包含 chapter_no,title,summary,twist）',
      '要求：保留已有章节不改动，只补充缺失章节，章节号连续。',
    ]
      .filter(Boolean)
      .join('\n')
    const rawText = await chatWithOutputLanguage(
      [
        { role: 'system', content: '你是职业小说策划编辑，只返回 JSON。' },
        { role: 'user', content: prompt },
      ],
      true
    )
    const parsed = parseObject(rawText)
    const appended = Array.isArray(parsed?.chapter_outlines) ? parsed.chapter_outlines : []
    const merged = [...plan.value.chapter_outlines]
    for (const outline of appended) {
      const no = Math.max(1, Number(outline?.chapter_no) || merged.length + 1)
      if (no <= 0 || no > target) continue
      const idx = no - 1
      merged[idx] = {
        chapter_no: no,
        title: String(outline?.title || t('novelStoryPage.creation.chapterDefaultTitle', { no })),
        summary: String(outline?.summary || ''),
        twist: String(outline?.twist || ''),
      }
    }
    while (merged.length < target) {
      const no = merged.length + 1
      merged.push({
        chapter_no: no,
        title: t('novelStoryPage.creation.chapterDefaultTitle', { no }),
        summary: t('novelStoryPage.prompts.defaultOutlineSummary'),
        twist: '',
      })
    }
    plan.value = normalizePlan({ ...plan.value, chapter_outlines: merged }, target)
  } catch {
    const merged = [...plan.value.chapter_outlines]
    while (merged.length < target) {
      const no = merged.length + 1
      merged.push({
        chapter_no: no,
        title: t('novelStoryPage.creation.chapterDefaultTitle', { no }),
        summary: t('novelStoryPage.prompts.defaultOutlineSummary'),
        twist: '',
      })
    }
    plan.value = normalizePlan({ ...plan.value, chapter_outlines: merged }, target)
  }
}

async function requestChapterText(chapterNo: number, mode: 'write' | 'continue'): Promise<string> {
  return chatWithOutputLanguage(
    [
      {
        role: 'system',
        content: mode === 'write' ? '你是职业小说作者，擅长连载写作。你必须仅输出小说正文文本。' : '你是职业小说作者，擅长保持上下文连贯。你必须仅输出续写正文文本。',
      },
      { role: 'user', content: chapterWritingPrompt(chapterNo, mode) },
    ],
    false
  )
}

async function generateChapter(chapterNo: number) {
  chapterError.value = ''
  chapterInfo.value = ''
  const no = Math.max(1, Number(chapterNo) || 1)
  syncPlanCharactersFromEditor()
  await ensurePlanChapterOutlines(Math.max(chapterCount.value, no))
  if (!plan.value) {
    chapterError.value = t('novelStoryPage.creation.generatePlanBeforeWriting')
    return
  }

  activeChapterNo.value = no
  chapterLoading.value = true
  saveChapterSnapshot(t('novelStoryPage.messages.snapshotGenerateChapter', { no }))
  try {
    const text = await requestChapterText(no, 'write')
    applyChapter(no, text, false)
    chapterInfo.value = t('novelStoryPage.messages.chapterGenerated', { no })
  } catch (e: any) {
    chapterError.value = e?.message || t('novelStoryPage.messages.chapterGenerateFailed')
  } finally {
    chapterLoading.value = false
  }
}

async function generateChaptersBatch(chapterNos: number[], reason: string) {
  const normalizedNos = Array.from(new Set(chapterNos.map((x) => Math.max(1, Number(x) || 1)))).sort((a, b) => a - b)
  if (normalizedNos.length === 0) return
  chapterError.value = ''
  chapterInfo.value = ''
  syncPlanCharactersFromEditor()
  await ensurePlanChapterOutlines(Math.max(...normalizedNos))
  if (!plan.value) {
    chapterError.value = t('novelStoryPage.creation.generatePlanBeforeWriting')
    return
  }

  chapterLoading.value = true
  saveChapterSnapshot(reason)
  try {
    for (let i = 0; i < normalizedNos.length; i += 1) {
      const no = normalizedNos[i]
      activeChapterNo.value = no
      chapterInfo.value = t('novelStoryPage.messages.batchGeneratingProgress', {
        reason,
        current: i + 1,
        total: normalizedNos.length,
        no,
      })
      const text = await requestChapterText(no, 'write')
      applyChapter(no, text, false)
    }
    chapterInfo.value = t('novelStoryPage.messages.batchGenerationCompleted', {
      reason,
      count: normalizedNos.length,
    })
  } catch (e: any) {
    chapterError.value = e?.message || t('novelStoryPage.messages.batchGenerationFailed', { reason })
  } finally {
    chapterLoading.value = false
  }
}

async function generateAllChaptersLight() {
  const count = Math.max(1, Math.min(24, Number(chapterCount.value) || 8))
  chapterCount.value = count
  const chapterNos = Array.from({ length: count }, (_, idx) => idx + 1)
  await generateChaptersBatch(chapterNos, t('novelStoryPage.messages.batchReasonLightGenerate'))
}

async function continueByLightBatch() {
  const plus = Math.max(1, Math.min(12, Number(lightContinuationCount.value) || 5))
  lightContinuationCount.value = plus
  const latestNo = sortedChapters().slice(-1)[0]?.chapter_no || 0
  const chapterNos = Array.from({ length: plus }, (_, idx) => latestNo + idx + 1)
  chapterCount.value = Math.max(chapterCount.value, latestNo + plus)
  await generateChaptersBatch(
    chapterNos,
    t('novelStoryPage.messages.batchReasonLightContinue', { count: plus }),
  )
}

async function completeBook() {
  chapterError.value = ''
  chapterInfo.value = ''
  if (!plan.value) {
    chapterError.value = t('novelStoryPage.messages.generatePlanBeforeComplete')
    return
  }
  syncPlanCharactersFromEditor()
  const total = Math.max(1, plan.value.chapter_outlines.length)
  const existingNos = new Set(chapters.value.map((x) => x.chapter_no))
  const missingNos = Array.from({ length: total }, (_, idx) => idx + 1).filter((no) => !existingNos.has(no))
  if (missingNos.length > 0) {
    const confirmed = window.confirm(
      t('novelStoryPage.messages.confirmAutoCompleteMissingChapters', { count: missingNos.length }),
    )
    if (!confirmed) return
    await generateChaptersBatch(missingNos, t('novelStoryPage.messages.batchReasonCompleteMissing'))
    if (chapterError.value) return
  }
  const saved = await saveCurrentWork({
    forceStatus: 'completed',
    successMessage: t('novelStoryPage.messages.completedAndSaved'),
  })
  if (!saved) {
    chapterError.value = worksError.value || t('novelStoryPage.messages.completeSaveFailed')
    return
  }
  chapterInfo.value = t('novelStoryPage.messages.completeSummary', {
    count: sortedChapters().length,
  })
}

async function generateNextChapter() {
  chapterError.value = ''
  chapterInfo.value = ''
  if (!plan.value) {
    chapterError.value = t('novelStoryPage.creation.generatePlanBeforeWriting')
    return
  }
  const chapterList = sortedChapters()
  const latest = chapterList.length > 0 ? chapterList[chapterList.length - 1].chapter_no : 0
  const nextNo = latest + 1
  if (nextNo > 24) {
    chapterError.value = t('novelStoryPage.messages.chapterLimitReached', { max: 24 })
    return
  }
  chapterCount.value = Math.max(chapterCount.value, nextNo)
  await generateChapter(nextNo)
}

async function continueCurrentChapter() {
  chapterError.value = ''
  chapterInfo.value = ''
  const no = Math.max(1, Number(activeChapterNo.value) || 1)
  const current = chapterByNo(no)
  if (!current?.content?.trim()) {
    chapterError.value = t('novelStoryPage.messages.chapterTextMissing')
    return
  }

  syncPlanCharactersFromEditor()
  await ensurePlanChapterOutlines(Math.max(chapterCount.value, no))
  chapterLoading.value = true
  saveChapterSnapshot(t('novelStoryPage.messages.snapshotContinueChapter', { no }))
  try {
    const text = await requestChapterText(no, 'continue')
    applyChapter(no, text, true)
    chapterInfo.value = t('novelStoryPage.messages.chapterContinued', { no })
  } catch (e: any) {
    chapterError.value = e?.message || t('novelStoryPage.messages.chapterContinueFailed')
  } finally {
    chapterLoading.value = false
  }
}

function deleteChapterByNo(chapterNo: number) {
  const no = Math.max(1, Number(chapterNo) || 1)
  const target = chapterByNo(no)
  if (!target) return
  saveChapterSnapshot(t('novelStoryPage.messages.snapshotDeleteChapter', { no }))
  chapters.value = chapters.value.filter((item) => item.chapter_no !== no)
  chapterImages.value = chapterImages.value.filter((item) => item.chapter_no !== no)
  bookStatus.value = 'draft'
  chapterInfo.value = t('novelStoryPage.messages.chapterDeleted', { no })
}

function deleteCurrentChapter() {
  const no = Math.max(1, Number(activeChapterNo.value) || 1)
  deleteChapterByNo(no)
}

function deleteLastChapter() {
  const latest = sortedChapters().slice(-1)[0]
  if (!latest) {
    chapterError.value = t('novelStoryPage.messages.noChapterToDelete')
    return
  }
  deleteChapterByNo(latest.chapter_no)
}

function trimCurrentChapterContent() {
  chapterError.value = ''
  chapterInfo.value = ''
  const no = Math.max(1, Number(activeChapterNo.value) || 1)
  const current = chapterByNo(no)
  if (!current) {
    chapterError.value = t('novelStoryPage.messages.currentChapterNotFound')
    return
  }
  const text = String(current.content || '').trim()
  if (!text) {
    chapterError.value = t('novelStoryPage.messages.currentChapterTrimEmpty')
    return
  }
  saveChapterSnapshot(t('novelStoryPage.messages.snapshotTrimChapter', { no }))
  const targetLength = Math.max(120, Math.floor(text.length * 0.78))
  const trimmed = text.slice(0, targetLength).replace(/\s+\S*$/, '').trim()
  applyChapter(no, trimmed, false)
  chapterInfo.value = t('novelStoryPage.messages.chapterTrimmed', { no })
}

async function regenerateImpactedChapters() {
  chapterError.value = ''
  chapterInfo.value = ''
  if (chapters.value.length === 0) {
    characterImpactPending.value = false
    characterImpactMessage.value = ''
    characterImpactBaseSignature.value = characterSignature(characters.value)
    chapterInfo.value = t('novelStoryPage.messages.noWrittenChapterYet')
    return
  }
  if (!window.confirm(t('novelStoryPage.messages.confirmRewriteImpactedChapters', { count: chapters.value.length }))) return
  syncPlanCharactersFromEditor()
  const targetChapters = sortedChapters()
  saveChapterSnapshot(t('novelStoryPage.messages.snapshotRewriteImpactedChapters'))
  chapterLoading.value = true
  try {
    for (let i = 0; i < targetChapters.length; i += 1) {
      const item = targetChapters[i]
      const no = item.chapter_no
      const outline = chapterOutline(no)
      const cast = characters.value
        .map((x) => `- ${x.name || '未命名角色'}：${x.role || '未设定'}；性格：${x.personality || '未设定'}；目标：${x.goal || '未设定'}；人物弧线：${x.arc || '未设定'}`)
        .join('\n')
      const prompt = [
        `请基于最新角色设定改写第${no}章正文。`,
        '要求：保留原章节主线事件和关键冲突，不要删减核心信息，不要改成大纲。',
        `故事标题：${plan.value?.title || storyTitle.value || '未命名作品'}`,
        `章节标题：${outline?.title || item.title || `第${no}章`}`,
        outline?.summary ? `本章目标：${outline.summary}` : '',
        cast ? `最新角色设定：\n${cast}` : '',
        continuationHint.value.trim() ? `用户后续创作要求：${continuationHint.value.trim()}` : '',
        `原章节正文：\n${item.content}`,
      ]
        .filter(Boolean)
        .join('\n\n')
      chapterInfo.value = t('novelStoryPage.messages.rewritingImpactedProgress', {
        current: i + 1,
        total: targetChapters.length,
      })
      const rewritten = await chatWithOutputLanguage(
        [
          { role: 'system', content: '你是职业小说修订编辑，只输出修订后的章节正文。' },
          { role: 'user', content: prompt },
        ],
        false
      )
      applyChapter(no, rewritten, false)
    }
    characterImpactPending.value = false
    characterImpactMessage.value = ''
    characterImpactBaseSignature.value = characterSignature(characters.value)
    chapterInfo.value = t('novelStoryPage.messages.rewriteImpactedDone', {
      count: targetChapters.length,
    })
  } catch (e: any) {
    chapterError.value = e?.message || t('novelStoryPage.messages.rewriteImpactedFailed')
  } finally {
    chapterLoading.value = false
  }
}

function acceptCharacterChangesWithoutRewrite() {
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)
  chapterInfo.value = t('novelStoryPage.messages.keepHistoryContinueWithLatestCharacters')
}

async function copyChapter(chapter: DraftChapter) {
  chapterError.value = ''
  chapterInfo.value = ''
  try {
    const titleLine = `${t('novelStoryPage.creation.chapterPrefix', { no: chapter.chapter_no })} ${chapter.title}`
    await navigator.clipboard.writeText(`${titleLine}\n\n${chapter.content}`)
    chapterInfo.value = t('novelStoryPage.messages.chapterCopied', { no: chapter.chapter_no })
  } catch {
    chapterError.value = t('novelStoryPage.messages.clipboardCopyFailed')
  }
}

async function copyAllChapters() {
  chapterError.value = ''
  chapterInfo.value = ''
  if (chapters.value.length === 0) return
  const book = sortedChapters()
    .map((c) => `${t('novelStoryPage.creation.chapterPrefix', { no: c.chapter_no })} ${c.title}\n\n${c.content}`)
    .join('\n\n')
  try {
    await navigator.clipboard.writeText(book)
    chapterInfo.value = t('novelStoryPage.messages.allDraftCopied')
  } catch {
    chapterError.value = t('novelStoryPage.messages.clipboardCopyFailed')
  }
}

function defaultWorldBookNotes(): string {
  const parts = [
    setting.value,
    worldContext.value,
    plan.value?.setting || '',
    plan.value?.core_conflict ? `核心冲突：${plan.value.core_conflict}` : '',
  ]
    .map((item) => String(item || '').trim())
    .filter(Boolean)
  return parts.join('\n').slice(0, 2000)
}

function characterAvatar(character: Character): string {
  const byId = characterImages.value.find((item) => item.character_id === character.id)
  if (byId?.image_url) return byId.image_url
  const byName = characterImages.value.find((item) => item.character_name === character.name)
  if (byName?.image_url) return byName.image_url
  const seed = encodeURIComponent(character.name || `novel-role-${character.id}`)
  return `https://api.dicebear.com/7.x/notionists/svg?seed=${seed}&backgroundColor=e0e7ff`
}

function worldBookEntries() {
  const entries: Array<{ key: string; content: string }> = []
  const pushEntry = (key: string, content: string) => {
    const normalized = String(content || '').trim()
    if (!normalized) return
    entries.push({ key, content: normalized })
  }

  pushEntry('世界观设定', setting.value || plan.value?.setting || '')
  pushEntry('故事上下文', worldContext.value)
  pushEntry('核心冲突', plan.value?.core_conflict || '')
  pushEntry('当前情境', currentSituation.value)
  pushEntry('世界书补充', worldBookNotes.value)
  sortedChapters()
    .slice(0, 12)
    .forEach((chapter) => {
      pushEntry(`第${chapter.chapter_no}章`, chapter.summary || compactText(chapter.content, 300))
    })

  return entries.slice(0, 24)
}

function normalizeTavernPersona(raw: any, index: number): TavernPersonaItem | null {
  if (!raw || typeof raw !== 'object') return null
  const seedId = pickFirstString(raw?.id, raw?.meta?.id, raw?.meta?.character_id, raw?.data?.id) || `tavern_import_${Date.now()}_${index}`
  const name =
    pickFirstString(raw?.name, raw?.data?.name, raw?.meta?.name) ||
    `酒馆角色${index + 1}`
  const description = pickFirstString(raw?.description, raw?.data?.description, raw?.persona, raw?.char_persona)
  const systemPrompt = pickFirstString(
    raw?.systemPrompt,
    raw?.system_prompt,
    raw?.data?.systemPrompt,
    raw?.data?.system_prompt,
    raw?.scenario,
    raw?.char_scenario
  )
  const firstMessage = pickFirstString(
    raw?.firstMessage,
    raw?.first_message,
    raw?.data?.firstMessage,
    raw?.data?.first_message,
    raw?.first_mes,
    raw?.mes_example
  )
  const group = pickFirstString(raw?.group, raw?.data?.group, raw?.meta?.group) || '酒馆角色'
  const source = pickFirstString(raw?.source, raw?.meta?.source) || (raw?.file ? 'imported' : 'custom')
  const avatar = resolveBackendMediaUrl(
    pickFirstString(raw?.avatar, raw?.avatar_url, raw?.data?.avatar, raw?.data?.avatar_url)
  )

  if (!name.trim() && !description.trim() && !systemPrompt.trim()) return null
  return {
    id: String(seedId),
    name: String(name || `酒馆角色${index + 1}`),
    avatar: String(avatar || ''),
    description: String(description || ''),
    systemPrompt: String(systemPrompt || ''),
    firstMessage: String(firstMessage || ''),
    group: String(group || '酒馆角色'),
    source: String(source || 'custom'),
    meta: raw?.meta && typeof raw.meta === 'object' ? raw.meta : {},
  }
}

async function loadBuiltinTavernPersonas(): Promise<any[]> {
  const candidates = ['/characters/index.json', './characters/index.json', 'characters/index.json']
  for (const url of candidates) {
    try {
      const response = await fetch(url, {
        cache: 'no-store',
        headers: { Accept: 'application/json' },
      })
      if (!response.ok) continue
      const payload = await response.json()
      if (Array.isArray(payload)) return payload
    } catch {
      // ignore and continue next candidate
    }
  }
  return []
}

async function loadTavernPersonasForImport() {
  tavernImportError.value = ''
  tavernImportInfo.value = ''
  tavernImportLoading.value = true
  try {
    const customSource = readCustomPersonas()
    const builtinSource = await loadBuiltinTavernPersonas()
    const source = [...customSource, ...builtinSource]
    const normalized: TavernPersonaItem[] = []
    const seen = new Set<string>()
    source.forEach((item: any, index: number) => {
      const persona = normalizeTavernPersona(item, index)
      if (!persona) return
      const key =
        String(persona.id || '').trim() ||
        `${String(persona.name || '').trim().toLowerCase()}|${String(persona.group || '').trim().toLowerCase()}`
      if (!key || seen.has(key)) return
      seen.add(key)
      normalized.push(persona)
    })
    normalized.sort((a, b) => {
      const sourceWeight = (value: string) => {
        if (value === 'custom') return 0
        if (value === 'novel_story') return 1
        return 2
      }
      const sourceDiff = sourceWeight(String(a.source || '')) - sourceWeight(String(b.source || ''))
      if (sourceDiff !== 0) return sourceDiff
      return String(a.name || '').localeCompare(String(b.name || ''), 'zh-Hans-CN')
    })
    tavernImportList.value = normalized
    selectedTavernPersonaIds.value = selectedTavernPersonaIds.value.filter((id) =>
      normalized.some((item) => item.id === id)
    )
    const customCount = normalized.filter((item) => item.source === 'custom' || item.source === 'novel_story').length
    const builtinCount = Math.max(0, normalized.length - customCount)
    tavernImportInfo.value =
      normalized.length > 0
        ? t('novelStoryPage.sync.importLoadedStats', {
            total: normalized.length,
            custom: customCount,
            builtin: builtinCount,
          })
        : t('novelStoryPage.sync.noImportRoles')
  } catch (e: any) {
    tavernImportError.value =
      e?.message || t('novelStoryPage.sync.loadTavernRolesFailed')
  } finally {
    tavernImportLoading.value = false
  }
}

function selectAllFilteredTavernPersonas() {
  selectedTavernPersonaIds.value = filteredTavernImportList.value.map((item) => item.id)
}

function clearSelectedTavernPersonas() {
  selectedTavernPersonaIds.value = []
}

function clearTavernImportPanel() {
  selectedTavernPersonaIds.value = []
  tavernImportKeyword.value = ''
  tavernSecondaryPrompt.value = ''
  tavernImportMode.value = 'append'
  tavernImportInfo.value = ''
  tavernImportError.value = ''
}

function extractLabeledValue(text: string, labels: string[]): string {
  const source = String(text || '')
  if (!source) return ''
  for (const label of labels) {
    const escaped = String(label).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const matched = source.match(new RegExp(`${escaped}\\s*[：:]\\s*([^\\n\\r]+)`, 'i'))
    const value = String(matched?.[1] || '').trim()
    if (value) return value
  }
  return ''
}

function personaToCharacter(persona: TavernPersonaItem): Character {
  const merged = [persona.description, persona.systemPrompt].filter(Boolean).join('\n')
  const role =
    extractLabeledValue(merged, ['身份关系', '身份', '角色定位', '职业']) ||
    persona.group ||
    '未设定身份'
  const personality =
    extractLabeledValue(merged, ['性格特征', '性格', '人格']) ||
    compactText(merged || `${persona.name}的人设待补充`, 180)
  const goal = extractLabeledValue(merged, ['角色目标', '目标', '动机'])
  const arc = extractLabeledValue(merged, ['人物弧线', '弧线', '成长线'])
  return {
    id: id('c'),
    name: String(persona.name || t('novelStoryPage.creation.untitledCharacter')),
    role: String(role || ''),
    personality: String(personality || ''),
    goal: String(goal || ''),
    arc: String(arc || ''),
  }
}

function mergeImportedCharacters(importedCharacters: Character[], mode: 'append' | 'replace') {
  const next = mode === 'replace' ? [] : characters.value.map((item) => ({ ...item }))
  const seen = new Set(
    next.map((item) => `${String(item.name || '').trim().toLowerCase()}|${String(item.role || '').trim().toLowerCase()}`)
  )
  let added = 0

  importedCharacters.forEach((item) => {
    const key = `${String(item.name || '').trim().toLowerCase()}|${String(item.role || '').trim().toLowerCase()}`
    if (mode === 'append' && seen.has(key)) return
    next.push(item)
    seen.add(key)
    added += 1
  })

  characters.value = normalizeCharacters(next)
  const firstImported = importedCharacters.find((item) => characters.value.some((saved) => saved.id === item.id))
  if (firstImported) {
    activeId.value = firstImported.id
    characterImageTargetId.value = firstImported.id
  } else if (characters.value.length > 0) {
    activeId.value = characters.value[0].id
    if (!characterImageTargetId.value || mode === 'replace') {
      characterImageTargetId.value = characters.value[0].id
    }
  }
  return added
}

function applyImportedPersonaContext(personas: TavernPersonaItem[], mode: 'append' | 'replace') {
  if (personas.length === 0) return
  const primary = personas[0]
  const titleHint = pickFirstString(primary.meta?.novel_title, primary.meta?.story_title, primary.group && `${primary.group}衍生故事`)
  if ((mode === 'replace' || !storyTitle.value.trim()) && titleHint) {
    storyTitle.value = titleHint
  }

  const contextParts = personas
    .slice(0, 8)
    .map((item) => {
      const detail = pickFirstString(item.description, item.systemPrompt)
      if (!detail) return ''
      return `角色：${item.name}\n${detail}`
    })
    .filter(Boolean)
  if (contextParts.length > 0 && (mode === 'replace' || !worldContext.value.trim())) {
    worldContext.value = compactText(contextParts.join('\n\n'), 2000)
  }

  if (primary.firstMessage && (mode === 'replace' || !currentSituation.value.trim())) {
    currentSituation.value = primary.firstMessage
  }
  if (mode === 'replace' || !worldBookNotes.value.trim()) {
    worldBookNotes.value = defaultWorldBookNotes()
  }
}

async function importSelectedTavernPersonas(modeOverride?: 'append' | 'replace') {
  tavernImportError.value = ''
  tavernImportInfo.value = ''
  if (tavernImportList.value.length === 0) {
    await loadTavernPersonasForImport()
  }
  if (selectedTavernPersonaIds.value.length === 0) {
    tavernImportError.value = t('novelStoryPage.sync.selectRolesFirst')
    return null
  }
  const mode = modeOverride || tavernImportMode.value
  const selectedSet = new Set(selectedTavernPersonaIds.value)
  const selected = tavernImportList.value.filter((item) => selectedSet.has(item.id))
  if (selected.length === 0) {
    tavernImportError.value = t('novelStoryPage.sync.selectedRolesNotFound')
    return null
  }

  const importedCharacters = selected.map((item) => personaToCharacter(item))
  const addedCount = mergeImportedCharacters(importedCharacters, mode)
  applyImportedPersonaContext(selected, mode)
  if (plan.value) {
    syncPlanCharactersFromEditor()
  }
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)

  const skippedCount = Math.max(0, importedCharacters.length - addedCount)
  if (addedCount > 0) {
    tavernImportInfo.value =
      skippedCount > 0
        ? t('novelStoryPage.sync.importedWithSkipped', {
            added: addedCount,
            skipped: skippedCount,
          })
        : t('novelStoryPage.sync.importedRoles', { count: addedCount })
  } else {
    tavernImportInfo.value = t('novelStoryPage.sync.noNewRolesImported')
  }

  return { selected, importedCharacters, mode }
}

async function importAndRegeneratePlanFromTavern() {
  tavernImportError.value = ''
  tavernImportInfo.value = ''
  const imported = await importSelectedTavernPersonas()
  if (!imported) return
  tavernImportGenerating.value = true
  try {
    const count = Math.max(1, Math.min(24, Number(chapterCount.value) || 8))
    chapterCount.value = count
    const roleMaterials = imported.selected.slice(0, 12).map((item) => ({
      name: item.name,
      group: item.group,
      description: item.description,
      systemPrompt: compactText(item.systemPrompt, 1200),
      firstMessage: item.firstMessage,
      meta: item.meta || {},
    }))
    const prompt = [
      '请基于酒馆角色设定生成一份新的小说剧情策划，返回严格 JSON。',
      `章节数：${count}`,
      `导入模式：${imported.mode === 'replace' ? '替换原角色集' : '追加扩展角色集'}`,
      tavernSecondaryPrompt.value
        ? `二改要求：${tavernSecondaryPrompt.value}`
        : '二改要求：保留角色核心特征，但需要重构主线冲突、人物关系和成长路径。',
      `角色资料：${JSON.stringify(roleMaterials)}`,
      '必须包含字段：title,genre,tone,setting,core_conflict,characters,chapter_outlines。',
      'chapter_outlines 每项必须包含 chapter_no,title,summary,twist。',
    ]
      .filter(Boolean)
      .join('\n')
    const rawText = await chatWithOutputLanguage(
      [
        { role: 'system', content: '你是 InkAI 小说总编，只返回可解析 JSON。' },
        { role: 'user', content: prompt },
      ],
      true
    )
    const normalized = normalizePlan(parseObject(rawText), count)
    const importedByName = new Map(
      imported.importedCharacters.map((item) => [String(item.name || '').trim().toLowerCase(), item])
    )
    const nextCharacters = normalizeCharacters(
      normalized.characters.length > 0
        ? normalized.characters.map((item) => {
            const linked = importedByName.get(String(item.name || '').trim().toLowerCase())
            return {
              id: linked?.id || id('c'),
              name: String(item.name || linked?.name || t('novelStoryPage.creation.untitledCharacter')),
              role: String(item.role || linked?.role || ''),
              personality: String(linked?.personality || ''),
              goal: String(item.goal || linked?.goal || ''),
              arc: String(item.arc || linked?.arc || ''),
            }
          })
        : imported.importedCharacters
    )

    plan.value = {
      ...normalized,
      characters: nextCharacters.map((item) => ({
        name: String(item.name || t('novelStoryPage.creation.untitledCharacter')),
        role: String(item.role || ''),
        goal: String(item.goal || ''),
        arc: String(item.arc || item.personality || ''),
      })),
    }
    characters.value = nextCharacters
    if (nextCharacters.length > 0) {
      activeId.value = nextCharacters[0].id
      characterImageTargetId.value = nextCharacters[0].id
    }

    storyTitle.value = plan.value.title || storyTitle.value
    if (plan.value.genre.trim()) genre.value = plan.value.genre
    if (plan.value.tone.trim()) tone.value = plan.value.tone
    if (plan.value.setting.trim()) setting.value = plan.value.setting
    if (plan.value.core_conflict.trim()) idea.value = plan.value.core_conflict
    worldContext.value = [plan.value.setting, plan.value.core_conflict ? `核心冲突：${plan.value.core_conflict}` : ''].filter(Boolean).join('\n')
    currentSituation.value = plan.value.chapter_outlines[0]?.summary || currentSituation.value
    if (!worldBookNotes.value.trim() || imported.mode === 'replace') {
      worldBookNotes.value = defaultWorldBookNotes()
    }

    activeChapterNo.value = 1
    chapters.value = []
    chapterHistory.value = []
    bookStatus.value = 'draft'
    chapterError.value = ''
    chapterInfo.value = ''
    continuationHint.value = ''
    characterImpactPending.value = false
    characterImpactMessage.value = ''
    characterImpactBaseSignature.value = characterSignature(characters.value)
    tab.value = 'creation'
    tavernImportInfo.value = t(
      'novelStoryPage.sync.importAndGenerateDone',
      { count: imported.selected.length },
    )
  } catch (e: any) {
    tavernImportError.value =
      e?.message || t('novelStoryPage.sync.importGeneratePlanFailed')
  } finally {
    tavernImportGenerating.value = false
  }
}

function buildTavernPersona(character: Character) {
  const name =
    String(character.name || t('novelStoryPage.creation.untitledCharacter')).trim() ||
    t('novelStoryPage.creation.untitledCharacter')
  const storyName =
    String(plan.value?.title || storyTitle.value || t('novelStoryPage.creation.untitledWork')).trim() ||
    t('novelStoryPage.creation.untitledWork')
  const description = [
    character.role ? `身份：${character.role}` : '',
    character.personality ? `性格：${character.personality}` : '',
    character.goal ? `目标：${character.goal}` : '',
    character.arc ? `人物弧线：${character.arc}` : '',
    plan.value?.core_conflict ? `剧情冲突：${plan.value.core_conflict}` : '',
  ]
    .filter(Boolean)
    .join('\n')
  const systemPrompt = [
    `你现在扮演角色：${name}`,
    `故事标题：${storyName}`,
    character.role ? `身份关系：${character.role}` : '',
    character.personality ? `性格特征：${character.personality}` : '',
    character.goal ? `角色目标：${character.goal}` : '',
    character.arc ? `人物弧线：${character.arc}` : '',
    (setting.value || plan.value?.setting) ? `世界观：${setting.value || plan.value?.setting}` : '',
    worldContext.value ? `世界上下文：${worldContext.value}` : '',
    currentSituation.value ? `当前情境：${currentSituation.value}` : '',
    '规则：保持角色一致性，禁止脱离设定，优先推动剧情。',
  ]
    .filter(Boolean)
    .join('\n')
  const firstMessage = currentSituation.value
    ? `*${name}注视着你。* ${currentSituation.value}`
    : `*${name}看向你，等待你开口。*`

  return {
    id: `custom_novel_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    name,
    avatar: characterAvatar(character),
    description,
    systemPrompt,
    firstMessage,
    group: tavernGroup.value.trim() || '小说同步角色',
    source: 'custom',
    meta: {
      source: 'novel_story',
      character_id: character.id,
      novel_title: storyName,
      updated_at: new Date().toISOString(),
    },
  }
}

function buildCharacterCard(character: Character) {
  const persona = buildTavernPersona(character)
  return {
    spec: 'novel_tavern_card_v1',
    generated_at: new Date().toISOString(),
    name: persona.name,
    description: persona.description,
    systemPrompt: persona.systemPrompt,
    firstMessage: persona.firstMessage,
    group: persona.group,
    avatar: persona.avatar,
    data: {
      name: persona.name,
      description: persona.description,
      systemPrompt: persona.systemPrompt,
      firstMessage: persona.firstMessage,
      group: persona.group,
      avatar: persona.avatar,
    },
    worldbook: {
      entries: worldBookEntries(),
    },
    novel_meta: {
      title: plan.value?.title || storyTitle.value || t('novelStoryPage.creation.untitledWork'),
      genre: plan.value?.genre || genre.value || '',
      tone: plan.value?.tone || tone.value || '',
      chapter_count: chapters.value.length,
    },
    character_meta: {
      id: character.id,
      role: character.role || '',
      personality: character.personality || '',
      goal: character.goal || '',
      arc: character.arc || '',
    },
    tavern_persona: persona,
  }
}

function readCustomPersonas() {
  try {
    const rawOld = localStorage.getItem(TAVERN_CUSTOM_PERSONAS_KEY)
    const rawV2 = localStorage.getItem(TAVERN_CUSTOM_PERSONAS_KEY_V2)
    const oldList = rawOld ? JSON.parse(rawOld) : []
    const v2List = rawV2 ? JSON.parse(rawV2) : []
    const merged = [...(Array.isArray(oldList) ? oldList : []), ...(Array.isArray(v2List) ? v2List : [])]
    const deduped: any[] = []
    const seen = new Set<string>()
    merged.forEach((item, index) => {
      const id = String(item?.id || `novel_sync_${index}`).trim()
      if (!id || seen.has(id)) return
      seen.add(id)
      deduped.push(item)
    })
    return deduped
  } catch {
    return []
  }
}

function saveCustomPersonas(items: any[]) {
  const payload = JSON.stringify(items)
  localStorage.setItem(TAVERN_CUSTOM_PERSONAS_KEY, payload)
  localStorage.setItem(TAVERN_CUSTOM_PERSONAS_KEY_V2, payload)
}

function upsertTavernPersona(persona: any) {
  const current = readCustomPersonas()
  const existingIndex = current.findIndex((item: any) => {
    const sameMeta =
      item?.meta?.source === 'novel_story' &&
      persona?.meta?.source === 'novel_story' &&
      String(item?.meta?.character_id || '') === String(persona?.meta?.character_id || '')
    const sameNameGroup = String(item?.name || '') === String(persona?.name || '') && String(item?.group || '') === String(persona?.group || '')
    return sameMeta || sameNameGroup
  })

  if (existingIndex >= 0) {
    persona.id = String(current[existingIndex]?.id || persona.id)
    current.splice(existingIndex, 1, { ...current[existingIndex], ...persona })
  } else {
    current.unshift(persona)
  }

  saveCustomPersonas(current)
}

function clearTavernSyncPanel() {
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  generatedCharacterCard.value = null
  tavernGroup.value = t('novelStoryPage.sync.defaultTavernGroup')
  currentSituation.value = ''
  worldContext.value = ''
  worldBookNotes.value = ''
  storyTitle.value = String(plan.value?.title || t('novelStoryPage.sync.defaultStoryTitle'))
  tavernSyncInfo.value = t('novelStoryPage.sync.syncPanelCleared')
}

function generateCharacterCard() {
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  const character = activeChar.value
  if (!character) {
    tavernSyncError.value = t('novelStoryPage.sync.selectCharacterBeforeCard')
    return
  }
  generatedCharacterCard.value = buildCharacterCard(character)
  tavernSyncInfo.value = t('novelStoryPage.sync.cardGenerated', {
    name: generatedCharacterCard.value.name,
  })
}

async function generateSyncCharacterCardImage() {
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  const target = activeChar.value
  if (!target) {
    tavernSyncError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  characterImageTargetId.value = target.id
  const prompt = characterImagePrompt.value.trim() || defaultCharacterPrompt(target)
  if (!prompt.trim()) {
    tavernSyncError.value = t('novelStoryPage.messages.fillCharacterPromptFirst')
    return
  }

  imageLoading.value = true
  try {
    const src = await generateImageByPrompt(prompt)
    const item: CharacterImageAsset = {
      id: id('sync_char_img'),
      character_id: target.id,
      character_name: target.name || t('novelStoryPage.creation.untitledCharacter'),
      prompt,
      image_url: resolveBackendMediaUrl(src),
      created_at: new Date().toISOString(),
    }
    const currentIndex = characterImages.value.findIndex((x) => x.character_id === target.id)
    if (currentIndex >= 0) {
      characterImages.value.splice(currentIndex, 1, item)
    } else {
      characterImages.value.unshift(item)
    }
    characterImagePrompt.value = prompt
    generatedCharacterCard.value = null
    tavernSyncInfo.value = tr(`已为「${item.character_name}」生成角色卡图片。`, `Generated card image for "${item.character_name}".`)
  } catch (e: any) {
    tavernSyncError.value = e?.message || tr('角色卡图片生成失败。', 'Failed to generate card image.')
  } finally {
    imageLoading.value = false
  }
}

function loadCardImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.decoding = 'async'
    if (!src.startsWith('data:')) {
      image.crossOrigin = 'anonymous'
    }
    image.onload = () => resolve(image)
    image.onerror = () => reject(new Error(tr('角色图片加载失败，请更换后重试。', 'Failed to load card image.')))
    image.src = src
  })
}

function canvasToPngBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    try {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
          return
        }
        reject(new Error(tr('角色卡图片导出失败。', 'Failed to export card image.')))
      }, 'image/png')
    } catch {
      reject(new Error(tr('角色卡图片导出失败。', 'Failed to export card image.')))
    }
  })
}

async function renderCardArtworkPng(card: any): Promise<Uint8Array> {
  const canvas = document.createElement('canvas')
  canvas.width = CARD_EXPORT_WIDTH
  canvas.height = CARD_EXPORT_HEIGHT
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    throw new Error(tr('浏览器不支持角色卡导出。', 'This browser does not support card export.'))
  }

  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, CARD_EXPORT_WIDTH, CARD_EXPORT_HEIGHT)

  const avatar = resolveBackendMediaUrl(String(card?.avatar || card?.data?.avatar || card?.tavern_persona?.avatar || ''))
  let imageDrawn = false
  if (avatar) {
    try {
      const image = await loadCardImage(avatar)
      const sourceWidth = Math.max(1, image.naturalWidth || image.width)
      const sourceHeight = Math.max(1, image.naturalHeight || image.height)
      const scale = Math.max(CARD_EXPORT_WIDTH / sourceWidth, CARD_EXPORT_HEIGHT / sourceHeight)
      const drawWidth = sourceWidth * scale
      const drawHeight = sourceHeight * scale
      const drawX = (CARD_EXPORT_WIDTH - drawWidth) / 2
      const drawY = (CARD_EXPORT_HEIGHT - drawHeight) / 2
      ctx.drawImage(image, drawX, drawY, drawWidth, drawHeight)
      imageDrawn = true
    } catch {
      imageDrawn = false
    }
  }

  if (!imageDrawn) {
    const fallbackGradient = ctx.createLinearGradient(0, 0, CARD_EXPORT_WIDTH, CARD_EXPORT_HEIGHT)
    fallbackGradient.addColorStop(0, '#1e293b')
    fallbackGradient.addColorStop(1, '#0f172a')
    ctx.fillStyle = fallbackGradient
    ctx.fillRect(0, 0, CARD_EXPORT_WIDTH, CARD_EXPORT_HEIGHT)

    const label = String(card?.name || t('novelStoryPage.creation.untitledCharacter')).trim().slice(0, 1).toUpperCase() || 'C'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.88)'
    ctx.font = 'bold 220px "Microsoft YaHei", "PingFang SC", sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(label, CARD_EXPORT_WIDTH / 2, CARD_EXPORT_HEIGHT / 2)
  }

  const topMask = ctx.createLinearGradient(0, 0, 0, CARD_EXPORT_HEIGHT * 0.35)
  topMask.addColorStop(0, 'rgba(15, 23, 42, 0.55)')
  topMask.addColorStop(1, 'rgba(15, 23, 42, 0)')
  ctx.fillStyle = topMask
  ctx.fillRect(0, 0, CARD_EXPORT_WIDTH, CARD_EXPORT_HEIGHT * 0.35)

  const bottomMask = ctx.createLinearGradient(0, CARD_EXPORT_HEIGHT * 0.5, 0, CARD_EXPORT_HEIGHT)
  bottomMask.addColorStop(0, 'rgba(2, 6, 23, 0)')
  bottomMask.addColorStop(1, 'rgba(2, 6, 23, 0.92)')
  ctx.fillStyle = bottomMask
  ctx.fillRect(0, CARD_EXPORT_HEIGHT * 0.5, CARD_EXPORT_WIDTH, CARD_EXPORT_HEIGHT * 0.5)

  const cardName = compactText(String(card?.name || t('novelStoryPage.creation.untitledCharacter')), 28)
  const cardRole = compactText(
    String(card?.character_meta?.role || card?.group || card?.tavern_persona?.group || ''),
    44,
  )
  const cardStory = compactText(String(card?.novel_meta?.title || storyTitle.value || ''), 44)

  ctx.textAlign = 'left'
  ctx.textBaseline = 'alphabetic'
  ctx.fillStyle = '#f8fafc'
  ctx.font = '700 56px "Microsoft YaHei", "PingFang SC", sans-serif'
  ctx.fillText(cardName, 42, CARD_EXPORT_HEIGHT - 150)

  ctx.fillStyle = 'rgba(241, 245, 249, 0.92)'
  ctx.font = '500 28px "Microsoft YaHei", "PingFang SC", sans-serif'
  if (cardRole) ctx.fillText(cardRole, 44, CARD_EXPORT_HEIGHT - 102)
  if (cardStory) ctx.fillText(cardStory, 44, CARD_EXPORT_HEIGHT - 62)

  ctx.strokeStyle = 'rgba(148, 163, 184, 0.65)'
  ctx.lineWidth = 2
  ctx.strokeRect(20, 20, CARD_EXPORT_WIDTH - 40, CARD_EXPORT_HEIGHT - 40)

  const blob = await canvasToPngBlob(canvas)
  return new Uint8Array(await blob.arrayBuffer())
}

function bytesToBase64(bytes: Uint8Array): string {
  let binary = ''
  const chunkSize = 0x8000
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    const chunk = bytes.subarray(offset, offset + chunkSize)
    binary += String.fromCharCode(...chunk)
  }
  return btoa(binary)
}

function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff
  for (let index = 0; index < bytes.length; index += 1) {
    crc = CRC32_TABLE[(crc ^ bytes[index]) & 0xff] ^ (crc >>> 8)
  }
  return (crc ^ 0xffffffff) >>> 0
}

function concatBytes(parts: Uint8Array[]): Uint8Array {
  const totalLength = parts.reduce((sum, part) => sum + part.length, 0)
  const merged = new Uint8Array(totalLength)
  let cursor = 0
  for (const part of parts) {
    merged.set(part, cursor)
    cursor += part.length
  }
  return merged
}

function createPngChunk(type: string, data: Uint8Array): Uint8Array {
  const typeBytes = new Uint8Array([type.charCodeAt(0), type.charCodeAt(1), type.charCodeAt(2), type.charCodeAt(3)])
  const lengthBytes = new Uint8Array(4)
  new DataView(lengthBytes.buffer).setUint32(0, data.length, false)
  const crcInput = concatBytes([typeBytes, data])
  const crcBytes = new Uint8Array(4)
  new DataView(crcBytes.buffer).setUint32(0, crc32(crcInput), false)
  return concatBytes([lengthBytes, typeBytes, data, crcBytes])
}

function embedCharaPayloadIntoPng(pngBytes: Uint8Array, payload: string): Uint8Array {
  if (pngBytes.length < PNG_SIGNATURE.length + 12) {
    throw new Error(tr('角色卡底图格式无效。', 'Invalid card image format.'))
  }
  for (let index = 0; index < PNG_SIGNATURE.length; index += 1) {
    if (pngBytes[index] !== PNG_SIGNATURE[index]) {
      throw new Error(tr('角色卡底图不是有效 PNG。', 'Card image is not a valid PNG.'))
    }
  }

  const view = new DataView(pngBytes.buffer, pngBytes.byteOffset, pngBytes.byteLength)
  let offset = PNG_SIGNATURE.length
  let iendStart = -1
  while (offset + 12 <= pngBytes.length) {
    const dataLength = view.getUint32(offset, false)
    const dataStart = offset + 8
    const dataEnd = dataStart + dataLength
    const chunkEnd = dataEnd + 4
    if (chunkEnd > pngBytes.length) break
    const chunkType = String.fromCharCode(
      pngBytes[offset + 4],
      pngBytes[offset + 5],
      pngBytes[offset + 6],
      pngBytes[offset + 7],
    )
    if (chunkType === 'IEND') {
      iendStart = offset
      break
    }
    offset = chunkEnd
  }
  if (iendStart < 0) {
    throw new Error(tr('角色卡底图缺少 PNG 结束标记。', 'Card image is missing PNG end marker.'))
  }

  const keyword = new TextEncoder().encode('chara')
  const payloadBytes = new TextEncoder().encode(payload)
  const textData = new Uint8Array(keyword.length + 1 + payloadBytes.length)
  textData.set(keyword, 0)
  textData[keyword.length] = 0
  textData.set(payloadBytes, keyword.length + 1)
  const textChunk = createPngChunk('tEXt', textData)

  return concatBytes([pngBytes.slice(0, iendStart), textChunk, pngBytes.slice(iendStart)])
}

async function buildCardPngWithPayload(card: any): Promise<Uint8Array> {
  const cardJson = JSON.stringify(card)
  const payloadBase64 = bytesToBase64(new TextEncoder().encode(cardJson))
  const artworkBytes = await renderCardArtworkPng(card)
  return embedCharaPayloadIntoPng(artworkBytes, payloadBase64)
}

async function downloadGeneratedCard() {
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  const character = activeChar.value
  if (!character) {
    tavernSyncError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  const card = buildCharacterCard(character)
  generatedCharacterCard.value = card
  const fileNameSeed = String(card?.name || 'novel_character').replace(/[\\/:*?"<>|]/g, '_')
  try {
    const pngBytes = await buildCardPngWithPayload(card)
    const blob = new Blob([pngBytes], { type: 'image/png' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${fileNameSeed}_card.png`
    document.body.appendChild(anchor)
    anchor.click()
    document.body.removeChild(anchor)
    URL.revokeObjectURL(url)
    tavernSyncInfo.value = tr('角色卡图片已下载，可直接在酒馆导入。', 'Card image downloaded and ready to import in Tavern.')
  } catch (e: any) {
    tavernSyncError.value = e?.message || tr('角色卡下载失败，请稍后重试。', 'Failed to download card image.')
  }
}

function syncActiveCharacterToTavern() {
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  const character = activeChar.value
  if (!character) {
    tavernSyncError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }

  try {
    const card = buildCharacterCard(character)
    generatedCharacterCard.value = card
    upsertTavernPersona(card.tavern_persona)
    tavernSyncInfo.value = t('novelStoryPage.sync.syncedCurrentCharacter', {
      name: card.name,
    })
  } catch (e: any) {
    tavernSyncError.value = e?.message || t('novelStoryPage.sync.syncToTavernFailed')
  }
}

function syncAllCharactersToTavern() {
  tavernSyncError.value = ''
  tavernSyncInfo.value = ''
  if (characters.value.length === 0) {
    tavernSyncError.value = t('novelStoryPage.sync.noCharactersToSync')
    return
  }

  try {
    let synced = 0
    for (const character of characters.value) {
      const card = buildCharacterCard(character)
      upsertTavernPersona(card.tavern_persona)
      synced += 1
    }
    tavernSyncInfo.value = t('novelStoryPage.sync.syncedAllCharacters', {
      count: synced,
    })
  } catch (e: any) {
    tavernSyncError.value = e?.message || t('novelStoryPage.sync.batchSyncFailed')
  }
}

function openTavernPage() {
  window.location.href = '/tavern'
}

type ImageApiType = 'gemini_native' | 'openai_compatible'

function normalizeImageApiType(value: unknown): ImageApiType {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'gemini_native' || normalized === 'gemini' || normalized === 'google_native' || normalized === 'google') {
    return 'gemini_native'
  }
  return 'openai_compatible'
}

function inferImageApiTypeFromModel(modelName: unknown): ImageApiType {
  return /gemini/i.test(String(modelName || '')) ? 'gemini_native' : 'openai_compatible'
}

function defaultImageModelByApiType(imageApiType: ImageApiType): string {
  return imageApiType === 'gemini_native' ? 'gemini-2.5-flash-image-preview' : 'gpt-image-1'
}

function getApiConfig() {
  const parsePayload = (raw: string | null) => {
    if (!raw) return {}
    try {
      const parsed = JSON.parse(raw)
      if (parsed?.apiSettings && typeof parsed.apiSettings === 'object') return parsed.apiSettings
      return parsed || {}
    } catch {
      return {}
    }
  }
  const oldParsed: any = parsePayload(localStorage.getItem(TAVERN_SETTINGS_KEY))
  const v2Parsed: any = parsePayload(localStorage.getItem(TAVERN_SETTINGS_KEY_V2))
  const baseUrl = String(oldParsed?.baseUrl || v2Parsed?.baseUrl || 'https://api.openai.com/v1').replace(/\/+$/, '')
  const apiKey = String(oldParsed?.apiKey || v2Parsed?.apiKey || '')
  const modelName = String(oldParsed?.modelName || oldParsed?.chatModel || v2Parsed?.modelName || v2Parsed?.chatModel || 'gpt-4o-mini')
  const resolvedImageApiType = normalizeImageApiType(
    oldParsed?.imageApiType ||
    oldParsed?.image_api_type ||
    oldParsed?.imageProvider ||
    oldParsed?.image_provider ||
    v2Parsed?.imageApiType ||
    v2Parsed?.image_api_type ||
    v2Parsed?.imageProvider ||
    v2Parsed?.image_provider ||
    inferImageApiTypeFromModel(oldParsed?.imageModelName || oldParsed?.imageModel || v2Parsed?.imageModelName || v2Parsed?.imageModel || modelName)
  )
  const resolvedImageModelName = String(
    oldParsed?.imageModelName ||
    oldParsed?.imageModel ||
    v2Parsed?.imageModelName ||
    v2Parsed?.imageModel ||
    modelName ||
    defaultImageModelByApiType(resolvedImageApiType)
  )

  return {
    baseUrl,
    apiKey,
    modelName,
    imageBaseUrl: String(oldParsed?.imageBaseUrl || v2Parsed?.imageBaseUrl || baseUrl).replace(/\/+$/, ''),
    imageApiKey: String(oldParsed?.imageApiKey || v2Parsed?.imageApiKey || apiKey),
    imageModelName: resolvedImageModelName || defaultImageModelByApiType(resolvedImageApiType),
    imageApiType: resolvedImageApiType,
  }
}

function pickFirstString(...values: any[]): string {
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) return value.trim()
  }
  return ''
}

function decodeImageDataFromResponse(payload: any): string {
  const first = payload?.data?.[0] || payload?.output?.[0] || null
  if (first && typeof first === 'object') {
    const imageUrl = pickFirstString(first.url, first.image_url, first.output_url)
    if (imageUrl) return imageUrl

    const b64 = pickFirstString(first.b64_json, first.base64, first.image_base64, first.image?.b64_json, first.image?.base64)
    if (b64) {
      if (b64.startsWith('data:image/')) return b64
      const mimeType = pickFirstString(first.mime_type, first.image?.mime_type) || 'image/png'
      return `data:${mimeType};base64,${b64}`
    }
  }

  const candidates = Array.isArray(payload?.candidates) ? payload.candidates : []
  for (const candidate of candidates) {
    const parts = Array.isArray(candidate?.content?.parts) ? candidate.content.parts : []
    for (const part of parts) {
      const inlineData = part?.inline_data || part?.inlineData || null
      const imageUrl = pickFirstString(part?.url, part?.image_url)
      if (imageUrl) return imageUrl

      const b64 = pickFirstString(inlineData?.data, part?.data)
      if (!b64) continue
      if (b64.startsWith('data:image/')) return b64

      const mimeType =
        pickFirstString(inlineData?.mime_type, inlineData?.mimeType, part?.mime_type, part?.mimeType) || 'image/png'
      return `data:${mimeType};base64,${b64}`
    }
  }

  return ''
}

async function readResponseErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json()
    const message = pickFirstString(data?.error?.message, data?.message, typeof data?.error === 'string' ? data.error : '')
    if (message) return message
  } catch {
    // ignore JSON parse error
  }
  return `HTTP ${response.status}`
}

function resolveGeminiNativeBase(baseUrl: string): string {
  const trimmed = String(baseUrl || '').trim().replace(/\/+$/, '')
  return trimmed.replace(/\/v1(?:beta)?$/i, '')
}

async function requestImageByModel(
  cfg: ReturnType<typeof getApiConfig>,
  model: string,
  prompt: string
): Promise<string> {
  const trimmedModel = String(model || '').trim()
  if (!trimmedModel) throw new Error(t('novelStoryPage.messages.imageModelMissing'))

  if (cfg.imageApiType === 'gemini_native') {
    const geminiBase = resolveGeminiNativeBase(String(cfg.imageBaseUrl || ''))
    const endpoint = `${geminiBase}/v1beta/models/${encodeURIComponent(trimmedModel)}:generateContent`
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: String(cfg.imageApiKey || ''),
      },
      body: JSON.stringify({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: { responseModalities: ['TEXT', 'IMAGE'] },
      }),
    })

    if (!response.ok) throw new Error(await readResponseErrorMessage(response))
    const data = await response.json()
    const src = decodeImageDataFromResponse(data)
    if (!src) throw new Error(t('novelStoryPage.messages.imageApiNoData'))
    return src
  }

  const baseUrl = String(cfg.imageBaseUrl || '').replace(/\/+$/, '')
  const response = await fetch(`${baseUrl}/images/generations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${cfg.imageApiKey}`,
    },
    body: JSON.stringify({
      model: trimmedModel,
      prompt,
      size: '1024x1024',
      n: 1,
    }),
  })

  if (!response.ok) throw new Error(await readResponseErrorMessage(response))
  const data = await response.json()
  const src = decodeImageDataFromResponse(data)
  if (!src) throw new Error(t('novelStoryPage.messages.imageApiNoData'))
  return src
}

async function generateImageByPrompt(prompt: string): Promise<string> {
  const cfg = getApiConfig()
  if (!cfg.imageApiKey) throw new Error(t('novelStoryPage.messages.imageApiKeyMissing'))
  const fallbackModel = defaultImageModelByApiType(cfg.imageApiType)
  const candidateModels = Array.from(new Set([String(cfg.imageModelName || '').trim(), fallbackModel].filter(Boolean)))
  let lastError = ''

  for (const model of candidateModels) {
    try {
      const src = await requestImageByModel(cfg, model, prompt)
      if (src) return src
      lastError = t('novelStoryPage.messages.imageApiNoData')
    } catch (error: any) {
      lastError = error?.message || t('novelStoryPage.messages.imageGenerateFailed')
    }
  }

  throw new Error(lastError || t('novelStoryPage.messages.imageGenerateFailedWithHint'))
}

function defaultCoverPrompt(): string {
  const title = plan.value?.title || storyTitle.value || '小说作品'
  const style = tone.value || plan.value?.tone || '电影感插画风'
  const type = genre.value || plan.value?.genre || '剧情向'
  return `为小说《${title}》生成封面，${type}题材，${style}，主体清晰，构图完整，无文字无水印，高质量`
}

function defaultCharacterPrompt(target: Character | null): string {
  if (!target) return ''
  const title = plan.value?.title || storyTitle.value || '小说'
  return `为小说《${title}》角色“${target.name || '未命名角色'}”生成人物图，身份：${target.role || '未设定'}，性格：${target.personality || '未设定'}，半身或全身立绘，画面干净，无文字`
}

function defaultChapterPrompt(chapterNo: number): string {
  const title = plan.value?.title || storyTitle.value || '小说作品'
  const outline = chapterOutline(chapterNo)
  const summary = outline?.summary || chapterByNo(chapterNo)?.summary || ''
  return `为小说《${title}》第${chapterNo}章生成章节插图，章节标题：${chapterTitle(chapterNo)}，剧情要点：${summary || '突出戏剧冲突'}，镜头感强，无文字`
}

async function generateCoverImage() {
  imageError.value = ''
  imageInfo.value = ''
  const prompt = coverPrompt.value.trim() || defaultCoverPrompt()
  if (!prompt.trim()) {
    imageError.value = t('novelStoryPage.messages.fillCoverPromptFirst')
    return
  }

  imageLoading.value = true
  try {
    const src = await generateImageByPrompt(prompt)
    coverPrompt.value = prompt
    coverImage.value = src
    imageInfo.value = t('novelStoryPage.messages.aiCoverGenerated')
  } catch (e: any) {
    imageError.value = e?.message || t('novelStoryPage.messages.coverGenerateFailed')
  } finally {
    imageLoading.value = false
  }
}

async function generateCharacterImage() {
  imageError.value = ''
  imageInfo.value = ''
  const target = selectedImageCharacter.value || activeChar.value
  if (!target) {
    imageError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  characterImageTargetId.value = target.id
  const prompt = characterImagePrompt.value.trim() || defaultCharacterPrompt(target)
  if (!prompt.trim()) {
    imageError.value = t('novelStoryPage.messages.fillCharacterPromptFirst')
    return
  }

  imageLoading.value = true
  try {
    const src = await generateImageByPrompt(prompt)
    const item: CharacterImageAsset = {
      id: id('char_img'),
      character_id: target.id,
      character_name: target.name || t('novelStoryPage.creation.untitledCharacter'),
      prompt,
      image_url: src,
      created_at: new Date().toISOString(),
    }
    const currentIndex = characterImages.value.findIndex((x) => x.character_id === target.id)
    if (currentIndex >= 0) {
      characterImages.value.splice(currentIndex, 1, item)
    } else {
      characterImages.value.unshift(item)
    }
    characterImagePrompt.value = prompt
    imageInfo.value = t('novelStoryPage.messages.characterImageGenerated', { name: item.character_name })
  } catch (e: any) {
    imageError.value = e?.message || t('novelStoryPage.messages.characterImageGenerateFailed')
  } finally {
    imageLoading.value = false
  }
}

async function generateChapterImage() {
  imageError.value = ''
  imageInfo.value = ''
  const chapterNo = Math.max(1, Number(activeChapterNo.value) || 1)
  const prompt = chapterImagePrompt.value.trim() || defaultChapterPrompt(chapterNo)
  if (!prompt.trim()) {
    imageError.value = t('novelStoryPage.messages.fillChapterPromptFirst')
    return
  }

  imageLoading.value = true
  try {
    const src = await generateImageByPrompt(prompt)
    const item: ChapterImageAsset = {
      id: id('chapter_img'),
      chapter_no: chapterNo,
      chapter_title: chapterTitle(chapterNo),
      prompt,
      image_url: src,
      created_at: new Date().toISOString(),
    }
    const currentIndex = chapterImages.value.findIndex((x) => x.chapter_no === chapterNo)
    if (currentIndex >= 0) {
      chapterImages.value.splice(currentIndex, 1, item)
    } else {
      chapterImages.value.unshift(item)
    }
    chapterImages.value = [...chapterImages.value].sort((a, b) => a.chapter_no - b.chapter_no)
    chapterImagePrompt.value = prompt
    imageInfo.value = t('novelStoryPage.messages.chapterImageGenerated', { no: chapterNo })
  } catch (e: any) {
    imageError.value = e?.message || t('novelStoryPage.messages.chapterImageGenerateFailed')
  } finally {
    imageLoading.value = false
  }
}

function hydrateWorkEditorFromWork(work: NovelWork | null) {
  if (!work) return
  workEditorTitle.value = String(work.title || '')
  workEditorSummary.value = String(work.summary || '')
  workEditorNotes.value = String(work.extra_meta?.library_notes || work.extra_meta?.notes || '')
  workEditorCoverPrompt.value = String(work.extra_meta?.cover_prompt || '')
  workEditorCoverImage.value = resolveBackendMediaUrl(String(work.cover_image || ''))
  const profiles =
    Array.isArray(work.extra_meta?.character_profiles) && work.extra_meta.character_profiles.length > 0
      ? work.extra_meta.character_profiles
      : Array.isArray(work.plan?.characters)
        ? work.plan?.characters
        : []
  workEditorCharacters.value = normalizeCharacters(profiles)
  workEditorCharacterImages.value = normalizeCharacterImages(work.character_images)
  workEditorCharacterTargetId.value = workEditorCharacters.value[0]?.id || ''
  workEditorCharacterPrompt.value = ''
  workEditorError.value = ''
  workEditorInfo.value = ''
}

function addWorkEditorCharacter() {
  const c: Character = {
    id: id('work_char'),
    name: t('novelStoryPage.creation.characterFallbackName', {
      index: workEditorCharacters.value.length + 1,
    }),
    role: '',
    personality: '',
    goal: '',
    arc: '',
  }
  workEditorCharacters.value.push(c)
  workEditorCharacterTargetId.value = c.id
}

function removeWorkEditorCharacter(characterId: string) {
  if (workEditorCharacters.value.length <= 1) return
  workEditorCharacters.value = workEditorCharacters.value.filter((item) => item.id !== characterId)
  workEditorCharacterImages.value = workEditorCharacterImages.value.filter((item) => item.character_id !== characterId)
  if (workEditorCharacterTargetId.value === characterId) {
    workEditorCharacterTargetId.value = workEditorCharacters.value[0]?.id || ''
  }
}

async function aiFillWorkInfo() {
  workEditorError.value = ''
  workEditorInfo.value = ''
  const work = selectedWork.value
  if (!work) return
  workEditorLoading.value = true
  try {
    const prompt = [
      '请基于以下作品信息，补全作品简介与补充设定，返回 JSON。',
      `标题：${workEditorTitle.value || work.title || '未命名作品'}`,
      `题材：${work.plan?.genre || genre.value || '未设定'}`,
      `文风：${work.plan?.tone || tone.value || '未设定'}`,
      `核心冲突：${work.plan?.core_conflict || work.summary || ''}`,
      `角色：${JSON.stringify(workEditorCharacters.value.map((c) => ({ name: c.name, role: c.role, personality: c.personality })))} `,
      `已有简介：${workEditorSummary.value || ''}`,
      `已有补充设定：${workEditorNotes.value || ''}`,
      '输出 JSON：{"summary":"...","notes":"..."}',
    ].join('\n')
    const raw = await chatWithOutputLanguage(
      [
        { role: 'system', content: '你是小说编辑助手，只返回 JSON。' },
        { role: 'user', content: prompt },
      ],
      true
    )
    const parsed = parseObject(raw)
    const nextSummary = String(parsed?.summary || '').trim()
    const nextNotes = String(parsed?.notes || '').trim()
    if (nextSummary) workEditorSummary.value = nextSummary
    if (nextNotes) workEditorNotes.value = nextNotes
    workEditorInfo.value = t('novelStoryPage.works.aiFillCompleted')
  } catch (e: any) {
    workEditorError.value = e?.message || t('novelStoryPage.works.aiFillFailed')
  } finally {
    workEditorLoading.value = false
  }
}

async function generateWorkEditorCover() {
  workEditorError.value = ''
  workEditorInfo.value = ''
  const prompt =
    workEditorCoverPrompt.value.trim() ||
    `为小说《${workEditorTitle.value || selectedWork.value?.title || '未命名作品'}》生成封面，主体清晰，构图完整，无文字无水印，高质量`
  if (!prompt.trim()) {
    workEditorError.value = t('novelStoryPage.messages.fillCoverPromptFirst')
    return
  }
  workEditorLoading.value = true
  try {
    const src = await generateImageByPrompt(prompt)
    workEditorCoverPrompt.value = prompt
    workEditorCoverImage.value = src
    workEditorInfo.value = t('novelStoryPage.works.workCoverGenerated')
  } catch (e: any) {
    workEditorError.value = e?.message || t('novelStoryPage.messages.coverGenerateFailed')
  } finally {
    workEditorLoading.value = false
  }
}

async function generateWorkEditorCharacterImage() {
  workEditorError.value = ''
  workEditorInfo.value = ''
  const target = workEditorCharacters.value.find((item) => item.id === workEditorCharacterTargetId.value) || null
  if (!target) {
    workEditorError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  const prompt =
    workEditorCharacterPrompt.value.trim() ||
    `为小说《${workEditorTitle.value || selectedWork.value?.title || '未命名作品'}》角色“${target.name || '未命名角色'}”生成人物图，身份：${target.role || '未设定'}，性格：${target.personality || '未设定'}，半身或全身立绘，无文字`
  workEditorLoading.value = true
  try {
    const src = await generateImageByPrompt(prompt)
    const item: CharacterImageAsset = {
      id: id('work_char_img'),
      character_id: target.id,
      character_name: target.name || t('novelStoryPage.creation.untitledCharacter'),
      prompt,
      image_url: src,
      created_at: new Date().toISOString(),
    }
    const idx = workEditorCharacterImages.value.findIndex((x) => x.character_id === target.id)
    if (idx >= 0) {
      workEditorCharacterImages.value.splice(idx, 1, item)
    } else {
      workEditorCharacterImages.value.unshift(item)
    }
    workEditorCharacterPrompt.value = prompt
    workEditorInfo.value = t('novelStoryPage.messages.characterImageGenerated', {
      name: item.character_name,
    })
  } catch (e: any) {
    workEditorError.value = e?.message || t('novelStoryPage.messages.characterImageGenerateFailed')
  } finally {
    workEditorLoading.value = false
  }
}

async function saveWorkEditorChanges() {
  workEditorError.value = ''
  workEditorInfo.value = ''
  const work = selectedWork.value
  if (!work?.id) return
  workEditorSaving.value = true
  try {
    const originalPlan = work.plan ? deepClone(work.plan) : {}
    const outlineCount = Array.isArray((originalPlan as any)?.chapter_outlines)
      ? (originalPlan as any).chapter_outlines.length
      : Math.max(1, Math.min(24, work.chapters.length || chapterCount.value))
    const mergedPlan = normalizePlan(
      {
        ...originalPlan,
        title: String(workEditorTitle.value || work.title || t('novelStoryPage.creation.untitledWork')),
        characters: workEditorCharacters.value.map((c) => ({
          name: String(c.name || t('novelStoryPage.creation.untitledCharacter')),
          role: String(c.role || ''),
          goal: String(c.goal || ''),
          arc: String(c.arc || c.personality || ''),
        })),
      },
      outlineCount
    )

    const payload = {
      client_id: ensureDraftClientId(),
      title: String(workEditorTitle.value || work.title || t('novelStoryPage.creation.untitledWork')).slice(0, 200),
      summary: String(workEditorSummary.value || work.summary || '').slice(0, 1000),
      cover_image: workEditorCoverImage.value || '',
      character_images: workEditorCharacterImages.value,
      plan: mergedPlan,
      extra_meta: {
        ...(work.extra_meta || {}),
        library_notes: String(workEditorNotes.value || ''),
        cover_prompt: String(workEditorCoverPrompt.value || ''),
        character_profiles: workEditorCharacters.value.map((c) => ({
          id: c.id,
          name: c.name,
          role: c.role,
          personality: c.personality,
          goal: c.goal || '',
          arc: c.arc || '',
        })),
        completion_status: work.extra_meta?.completion_status || 'draft',
      },
    }

    const saved: any = await client.patch(`/novel-works/${work.id}/`, payload)
    const normalized = normalizeWork(saved)
    const index = works.value.findIndex((item) => item.id === normalized.id)
    if (index >= 0) {
      works.value.splice(index, 1, normalized)
    } else {
      works.value.unshift(normalized)
    }
    works.value = [...works.value].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    selectedWorkId.value = normalized.id
    hydrateWorkEditorFromWork(normalized)
    workEditorInfo.value = t('novelStoryPage.works.workInfoSaved')
  } catch (e: any) {
    workEditorError.value =
      e?.response?.data?.detail ||
      e?.message ||
      t('novelStoryPage.works.workInfoSaveFailed')
  } finally {
    workEditorSaving.value = false
  }
}

function textFromPayload(payload: any): string {
  const content = payload?.choices?.[0]?.message?.content
  if (typeof content === 'string') return content.trim()
  if (Array.isArray(content)) return content.map((x: any) => String(x?.text || '')).join('\n').trim()
  return ''
}

function parseObject(text: string): any {
  try {
    return JSON.parse(text)
  } catch {
    const left = text.indexOf('{')
    const right = text.lastIndexOf('}')
    if (left >= 0 && right > left) return JSON.parse(text.slice(left, right + 1))
    throw new Error(t('novelStoryPage.messages.parseJsonFailed'))
  }
}

async function chat(messagesPayload: ChatMessagePayload[], responseJson = false): Promise<string> {
  const cfg = getApiConfig()
  if (!cfg.apiKey) throw new Error(t('novelStoryPage.messages.apiKeyMissing'))
  const payload: any = { model: cfg.modelName, messages: messagesPayload, temperature: 0.7 }
  if (responseJson) payload.response_format = { type: 'json_object' }
  const res = await fetch(`${cfg.baseUrl}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${cfg.apiKey}` },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(t('novelStoryPage.messages.apiError', { status: res.status }))
  const data = await res.json()
  const text = textFromPayload(data)
  if (!text) throw new Error(t('novelStoryPage.messages.emptyApiText'))
  return text
}

async function chatWithOutputLanguage(messagesPayload: ChatMessagePayload[], responseJson = false): Promise<string> {
  return chat(withOutputLanguageConstraint(messagesPayload), responseJson)
}

function normalizePlan(raw: any, forcedCount?: number): Plan {
  const count = Math.max(1, Math.min(24, Number(forcedCount) || Number(chapterCount.value) || 8))
  const outlines = Array.isArray(raw?.chapter_outlines) ? raw.chapter_outlines : []
  const fixed = outlines.slice(0, count).map((x: any, i: number) => ({
    chapter_no: Number(x?.chapter_no) || i + 1,
    title: String(x?.title || t('novelStoryPage.creation.chapterDefaultTitle', { no: i + 1 })),
    summary: String(x?.summary || ''),
    twist: String(x?.twist || ''),
  }))
  while (fixed.length < count) {
    fixed.push({
      chapter_no: fixed.length + 1,
      title: t('novelStoryPage.creation.chapterDefaultTitle', { no: fixed.length + 1 }),
      summary: '',
      twist: '',
    })
  }
  return {
    title: String(raw?.title || t('novelStoryPage.creation.untitledWork')),
    genre: String(raw?.genre || ''),
    tone: String(raw?.tone || ''),
    setting: String(raw?.setting || ''),
    core_conflict: String(raw?.core_conflict || ''),
    characters: Array.isArray(raw?.characters)
      ? raw.characters.map((c: any) => ({
          name: String(c?.name || ''),
          role: String(c?.role || ''),
          goal: String(c?.goal || ''),
          arc: String(c?.arc || ''),
        }))
      : [],
    chapter_outlines: fixed,
  }
}

async function generatePlan() {
  workshopError.value = ''
  if (!idea.value.trim()) {
    workshopError.value = t('novelStoryPage.messages.fillCoreIdeaFirst')
    return
  }
  workshopLoading.value = true
  try {
    const count = Math.max(1, Math.min(24, Number(chapterCount.value) || 8))
    chapterCount.value = count
    const prompt = `请基于以下输入生成小说策划 JSON。\n核心创意：${idea.value}\n题材：${genre.value}\n文风：${tone.value}\n设定：${setting.value}\n章节数：${count}\n字段必须包含 title,genre,tone,setting,core_conflict,characters,chapter_outlines。`
    const rawText = await chatWithOutputLanguage(
      [
        { role: 'system', content: '你是 InkAI 小说工坊，返回严格 JSON。' },
        { role: 'user', content: prompt },
      ],
      true
    )
    plan.value = normalizePlan(parseObject(rawText))
    if (plan.value.characters.length > 0) {
      characters.value = normalizeCharacters(
        plan.value.characters.map((c) => ({
          id: id('c'),
          name: c.name || t('novelStoryPage.creation.untitledCharacter'),
          role: c.role || '',
          personality: '',
          goal: c.goal || '',
          arc: c.arc || '',
        }))
      )
      activeId.value = characters.value[0]?.id || activeId.value
      characterImageTargetId.value = characters.value[0]?.id || ''
    }
    characterImpactPending.value = false
    characterImpactMessage.value = ''
    characterImpactBaseSignature.value = characterSignature(characters.value)
    activeChapterNo.value = 1
    chapters.value = []
    chapterHistory.value = []
    bookStatus.value = 'draft'
    chapterError.value = ''
    chapterInfo.value = ''
    continuationHint.value = ''
  } catch (e: any) {
    workshopError.value = e?.message || t('novelStoryPage.messages.generateFailed')
  } finally {
    workshopLoading.value = false
  }
}

async function refinePlanOutlines() {
  workshopError.value = ''
  chapterInfo.value = ''
  if (!plan.value) {
    workshopError.value = t('novelStoryPage.messages.generatePlanBeforeRefine')
    return
  }
  outlineLoading.value = true
  try {
    const count = Math.max(1, Math.min(24, Number(plan.value.chapter_outlines.length) || Number(chapterCount.value) || 8))
    chapterCount.value = count
    const prompt = [
      '请优化以下小说策划的大纲与章节标题，并返回 JSON。',
      `章节数固定：${count}`,
      `故事标题：${plan.value.title || storyTitle.value || '未命名作品'}`,
      `题材：${plan.value.genre || genre.value || '未设定'}`,
      `文风：${plan.value.tone || tone.value || '未设定'}`,
      plan.value.setting ? `世界观：${plan.value.setting}` : '',
      plan.value.core_conflict ? `核心冲突：${plan.value.core_conflict}` : '',
      `角色：${JSON.stringify(plan.value.characters)}`,
      `当前大纲：${JSON.stringify(plan.value.chapter_outlines)}`,
      '输出字段至少包含：title,chapter_outlines。',
    ]
      .filter(Boolean)
      .join('\n')
    const rawText = await chatWithOutputLanguage(
      [
        { role: 'system', content: '你是资深小说总编，只返回 JSON。' },
        { role: 'user', content: prompt },
      ],
      true
    )
    const parsed = parseObject(rawText)
    const merged = {
      ...plan.value,
      title: String(parsed?.title || plan.value.title || storyTitle.value || t('novelStoryPage.creation.untitledWork')),
      chapter_outlines: Array.isArray(parsed?.chapter_outlines) ? parsed.chapter_outlines : plan.value.chapter_outlines,
    }
    plan.value = normalizePlan(merged, count)
    storyTitle.value = plan.value.title || storyTitle.value
    chapterInfo.value = t('novelStoryPage.messages.outlineOptimized')
  } catch (e: any) {
    workshopError.value = e?.message || t('novelStoryPage.messages.outlineOptimizeFailed')
  } finally {
    outlineLoading.value = false
  }
}

function syncPlanToRoleplay() {
  if (!plan.value) return
  storyTitle.value = plan.value.title || storyTitle.value
  worldContext.value = [plan.value.setting, `核心冲突：${plan.value.core_conflict}`].filter(Boolean).join('\n')
  currentSituation.value = plan.value.chapter_outlines[0]?.summary || currentSituation.value
  if (plan.value.characters.length > 0) {
    characters.value = plan.value.characters.map((c) => ({
      id: id('c'),
      name: c.name || t('novelStoryPage.creation.untitledCharacter'),
      role: c.role || '',
      personality: '',
      goal: c.goal || '',
      arc: c.arc || '',
    }))
    activeId.value = characters.value[0].id
    characterImageTargetId.value = characters.value[0].id
  }
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)
  if (!worldBookNotes.value.trim()) {
    worldBookNotes.value = [plan.value.setting, `核心冲突：${plan.value.core_conflict}`].filter(Boolean).join('\n')
  }
  tab.value = 'sync'
}

function clearRoleCharacters() {
  if (!window.confirm(t('novelStoryPage.messages.confirmClearCharacters'))) return
  const resetCharacters = normalizeCharacters([])
  characters.value = resetCharacters
  activeId.value = resetCharacters[0]?.id || ''
  characterImageTargetId.value = resetCharacters[0]?.id || ''
  characterImages.value = []
  generatedCharacterCard.value = null
  tavernSyncError.value = ''
  tavernSyncInfo.value = t('novelStoryPage.messages.charactersReset')
  if (plan.value) {
    syncPlanCharactersFromEditor()
  }
  characterImpactPending.value = false
  characterImpactMessage.value = ''
  characterImpactBaseSignature.value = characterSignature(characters.value)
}

function addCharacter() {
  const c: Character = {
    id: id('c'),
    name: t('novelStoryPage.creation.characterFallbackName', {
      index: characters.value.length + 1,
    }),
    role: '',
    personality: '',
    goal: '',
    arc: '',
  }
  characters.value.push(c)
  activeId.value = c.id
  if (!characterImageTargetId.value) characterImageTargetId.value = c.id
}

function removeCharacter() {
  if (characters.value.length <= 1) return
  const idx = characters.value.findIndex((c) => c.id === activeId.value)
  if (idx < 0) return
  const removingId = characters.value[idx].id
  characters.value.splice(idx, 1)
  characterImages.value = characterImages.value.filter((item) => item.character_id !== removingId)
  activeId.value = characters.value[Math.max(0, idx - 1)]?.id || characters.value[0].id
  if (characterImageTargetId.value === removingId) {
    characterImageTargetId.value = characters.value[0]?.id || ''
  }
}

function roleplaySystemPrompt(c: Character): string {
  return [
    `你现在扮演角色：${c.name}`,
    `身份关系：${c.role || '未设定'}`,
    c.personality ? `性格：${c.personality}` : '',
    c.goal ? `角色目标：${c.goal}` : '',
    c.arc ? `人物弧线：${c.arc}` : '',
    `故事标题：${storyTitle.value || t('novelStoryPage.sync.defaultStoryTitle')}`,
    worldContext.value ? `世界上下文：${worldContext.value}` : '',
    currentSituation.value ? `当前情境：${currentSituation.value}` : '',
    '规则：必须保持角色口吻，不以 AI 身份回答，优先推动剧情。',
  ]
    .filter(Boolean)
    .join('\n')
}

async function sendMessage() {
  roleplayError.value = ''
  const c = activeChar.value
  const text = inputText.value.trim()
  if (!c) {
    roleplayError.value = t('novelStoryPage.messages.selectCharacterFirst')
    return
  }
  if (!text) {
    roleplayError.value = t('novelStoryPage.messages.inputMessageFirst')
    return
  }
  messages.value.push({ id: id('m'), role: 'user', content: text })
  inputText.value = ''
  replyLoading.value = true
  try {
    const history = messages.value.slice(-12).map((m) => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content }))
    const reply = await chatWithOutputLanguage([{ role: 'system', content: roleplaySystemPrompt(c) }, ...history])
    messages.value.push({ id: id('m'), role: 'assistant', content: reply })
  } catch (e: any) {
    roleplayError.value = e?.message || t('novelStoryPage.messages.replyFailed')
  } finally {
    replyLoading.value = false
  }
}

async function analyzeImpact() {
  roleplayError.value = ''
  plotInstruction.value = ''
  const c = activeChar.value
  if (!c || messages.value.length === 0) return
  impactLoading.value = true
  try {
    const dialogue = messages.value.slice(-8).map((m) => `${m.role === 'user' ? '用户' : c.name}：${m.content}`).join('\n')
    const result = await chatWithOutputLanguage([
      { role: 'system', content: '你是剧情影响分析器。' },
      { role: 'user', content: `分析以下对话对后续剧情的影响。\n${dialogue}\n如果无显著变化仅输出 NO_CHANGE，否则输出1-3条剧情干预建议。` },
    ])
    plotInstruction.value = /NO_CHANGE/i.test(result)
      ? t('novelStoryPage.messages.noPlotTurningPoint')
      : result
  } catch (e: any) {
    roleplayError.value = e?.message || t('novelStoryPage.messages.analyzeFailed')
  } finally {
    impactLoading.value = false
  }
}

watch(
  () => characterSignature(characters.value),
  (nextSignature) => {
    if (draftHydrating.value) return
    if (!characterImpactBaseSignature.value) {
      characterImpactBaseSignature.value = nextSignature
      return
    }
    if (nextSignature !== characterImpactBaseSignature.value) {
      characterImpactPending.value = true
      characterImpactMessage.value = t('novelStoryPage.messages.characterSettingChanged')
      if (plan.value) {
        syncPlanCharactersFromEditor()
      }
    }
  }
)

watch(
  selectedWork,
  (work) => {
    if (!work) return
    hydrateWorkEditorFromWork(work)
  },
  { immediate: false }
)

watch(
  selectedWorkChapterList,
  (list) => {
    if (list.length === 0) {
      selectedWorkChapterNo.value = null
      return
    }
    const currentNo = Number(selectedWorkChapterNo.value || 0)
    if (!list.some((item) => item.chapter_no === currentNo)) {
      selectedWorkChapterNo.value = list[0].chapter_no
    }
  },
  { immediate: true }
)

watch(
  tab,
  (nextTab) => {
    if (nextTab === 'sync' && tavernImportList.value.length === 0 && !tavernImportLoading.value) {
      loadTavernPersonasForImport()
    }
  },
  { immediate: false }
)

watch(
  [
    tab,
    creationMode,
    idea,
    genre,
    tone,
    setting,
    chapterCount,
    lightContinuationCount,
    plan,
    activeChapterNo,
    targetWords,
    continuationHint,
    chapters,
    chapterHistory,
    bookStatus,
    storyTitle,
    worldContext,
    currentSituation,
    characters,
    activeId,
    messages,
    selectedWorkId,
    coverPrompt,
    coverImage,
    characterImagePrompt,
    characterImageTargetId,
    chapterImagePrompt,
    characterImages,
    chapterImages,
    tavernGroup,
    worldBookNotes,
    tavernSecondaryPrompt,
    tavernImportMode,
  ],
  () => {
    queueDraftSave()
  },
  { deep: true }
)

onMounted(async () => {
  await loadDraft()
  await loadWorks()
  if (selectedWorkId.value) {
    const work = works.value.find((item) => item.id === selectedWorkId.value) || null
    if (work) {
      hydrateWorkEditorFromWork(work)
      bookStatus.value = String(work.extra_meta?.completion_status || '').toLowerCase() === 'completed' ? 'completed' : bookStatus.value
    }
  }
  if (!characterImageTargetId.value && characters.value.length > 0) {
    characterImageTargetId.value = characters.value[0].id
  }
  if (!worldBookNotes.value.trim()) {
    worldBookNotes.value = defaultWorldBookNotes()
  }
  loadTavernPersonasForImport()
  characterImpactBaseSignature.value = characterSignature(characters.value)
})
</script>

<style scoped>
.novel-galaxy {
  background:
    radial-gradient(circle at 8% 0%, color-mix(in srgb, var(--primary-color) 16%, transparent) 0%, transparent 32%),
    radial-gradient(circle at 92% 2%, color-mix(in srgb, #22c55e 14%, transparent) 0%, transparent 30%),
    linear-gradient(180deg, #f8fbff 0%, #f5f9ff 100%);
}

.novel-galaxy-inner {
  max-width: 1520px;
}

.novel-galaxy section {
  border-color: #d6e2f3 !important;
  background:
    radial-gradient(120% 90% at 0% -16%, color-mix(in srgb, var(--primary-color) 10%, transparent) 0%, transparent 58%),
    linear-gradient(160deg, #ffffff 0%, #f7fbff 100%) !important;
  box-shadow: 0 20px 38px -30px rgba(15, 23, 42, 0.3);
}

.novel-galaxy :deep(.rounded-xl),
.novel-galaxy :deep(.rounded-2xl) {
  border-radius: 20px !important;
}

.novel-galaxy :deep(.rounded-lg) {
  border-radius: 14px !important;
}

.novel-galaxy :deep(button) {
  border-radius: 12px;
  border: 1px solid #cfe0f3;
  background: linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
  color: #0f172a;
  font-weight: 600;
  box-shadow: 0 12px 26px -24px rgba(15, 23, 42, 0.42);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.novel-galaxy :deep(button:hover:not(:disabled)) {
  transform: translateY(-1px);
  border-color: #9ed6ff;
  box-shadow: 0 16px 30px -22px rgba(14, 116, 144, 0.42);
}

.novel-galaxy :deep(button:disabled) {
  opacity: 0.58;
  cursor: not-allowed;
}

.novel-galaxy :deep(.bg-slate-900),
.novel-galaxy :deep(.bg-indigo-600),
.novel-galaxy :deep(.bg-emerald-600),
.novel-galaxy :deep(.bg-cyan-600) {
  background: linear-gradient(180deg, #22b1f0 0%, #0284c7 100%) !important;
  color: #ffffff !important;
  border-color: transparent !important;
}

.novel-galaxy :deep(input),
.novel-galaxy :deep(textarea),
.novel-galaxy :deep(select) {
  border-color: #cfe0f3 !important;
  background: linear-gradient(180deg, #ffffff 0%, #f6faff 100%);
  color: #0f172a;
  border-radius: 12px !important;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}

.novel-galaxy :deep(input:focus),
.novel-galaxy :deep(textarea:focus),
.novel-galaxy :deep(select:focus) {
  outline: none;
  border-color: #7dd3fc !important;
  box-shadow: 0 0 0 4px rgba(125, 211, 252, 0.2);
}

.novel-galaxy :deep(.text-slate-500),
.novel-galaxy :deep(.text-slate-600) {
  color: #516178 !important;
}

.novel-galaxy :deep(.text-slate-700),
.novel-galaxy :deep(.text-slate-800),
.novel-galaxy :deep(.text-slate-900) {
  color: #0f172a !important;
}

.novel-galaxy code {
  background: rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 0.35rem;
  padding: 0.05rem 0.3rem;
}
</style>

