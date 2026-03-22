<template>
  <div 
    id="tavern-root"
    class="tavern-galaxy w-full flex font-sans relative overflow-hidden selection:bg-green-100 selection:text-green-900 bg-[#f5f5f5] text-slate-800"
  >
    <!-- Left Sidebar (Chat List) -->
    <aside 
      class="sidebar-panel flex flex-col border-r border-[#dcdcdc] bg-[#f7f7f7] w-80 shrink-0 transition-transform duration-300 absolute z-40 inset-y-0 left-0 lg:relative lg:translate-x-0"
      :class="showMobileSidebar ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- User Profile / Top Bar -->
      <div class="h-16 px-4 flex items-center justify-between bg-[#f5f5f5] border-b border-[#e7e7e7] shrink-0">
         <div class="flex items-center gap-3">
           <div
             class="w-9 h-9 rounded-lg bg-slate-200 overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
             @click="openUserProfileEditor"
             :title="tr('编辑用户设定', 'Edit Profile')"
           >
             <img :src="userAvatarDisplay" class="w-full h-full object-cover" />
           </div>
           <span class="text-sm font-medium text-slate-700 truncate max-w-[10rem]">{{ userDisplayName }}</span>
         </div>
         <div class="flex gap-3 text-slate-500">
           <button
             class="p-1.5 hover:bg-[#e0e0e0] rounded-md transition-colors"
             @click="openPersonaCreator"
             :title="tr('创建自定义角色', 'Create Custom Role')"
           >
             <Plus class="w-4 h-4" />
           </button>
           <button class="p-1.5 hover:bg-[#e0e0e0] rounded-md transition-colors" @click="openSettingsPanel" :title="tr('设置', 'Settings')"><Settings class="w-4 h-4" /></button>
           <button class="lg:hidden p-1.5 hover:bg-[#e0e0e0] rounded-md" @click="showMobileSidebar = false"><X class="w-4 h-4" /></button>
         </div>
      </div>
      
      <!-- Search -->
      <div class="px-3 py-3 bg-[#f7f7f7] border-b border-[#e7e7e7]">
        <div class="relative bg-[#e2e2e2] rounded-md flex items-center px-2 py-1.5 focus-within:bg-white focus-within:ring-1 focus-within:ring-[#07c160] transition-all">
          <Search class="w-3.5 h-3.5 text-slate-400 shrink-0 mr-2" />
          <input
            v-model="personaSearchQuery"
            type="text"
            :placeholder="tr('搜索', 'Search')"
            class="w-full bg-transparent border-none p-0 text-xs focus:ring-0 text-slate-700 placeholder:text-slate-400"
          >
        </div>
      </div>
      
      <!-- Friend List -->
      <div class="flex-1 overflow-y-auto custom-scrollbar">
        <div v-for="(groupList, groupName) in groupedPersonas" :key="groupName">
           <!-- Group Header -->
           <div 
             @click="toggleGroup(String(groupName))"
             class="px-3 py-2 text-xs font-bold text-slate-500 uppercase bg-[#f0f0f0] border-y border-[#e7e7e7] cursor-pointer flex justify-between items-center select-none"
             v-if="groupList.length > 0"
           >
             {{ getPersonaGroupLabel(String(groupName)) }} ({{ groupList.length }})
             <ChevronDown class="w-3 h-3 transition-transform" :class="collapsedGroups[String(groupName)] ? '-rotate-90' : ''" />
           </div>

           <!-- Group Items -->
           <div v-show="!collapsedGroups[String(groupName)]">
             <div 
               v-for="persona in groupList" 
               :key="persona.id"
               @click="switchPersona(persona)"
               class="px-3 py-3 cursor-pointer flex items-center gap-3 transition-colors relative group border-b border-slate-100 last:border-0"
               :class="[
                 currentPersona.id === persona.id 
                   ? 'bg-[#cce9ff]' 
                   : 'hover:bg-[#e9e9e9]'
               ]"
             >
                <div class="w-10 h-10 rounded-md overflow-hidden shrink-0 relative">
                  <img :src="persona.avatar" :alt="persona.name" class="w-full h-full object-cover" @error="onPersonaAvatarError(persona)" />
                  <div v-if="currentPersona.id === persona.id" class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#07c160] border-2 border-white rounded-full"></div>
                </div>
                
                 <div class="flex-1 min-w-0">
                   <div class="flex justify-between items-center mb-0.5">
                     <div class="font-medium text-sm text-slate-800 truncate">{{ persona.name }}</div>
                     <button
                       v-if="persona.source === 'custom'"
                       @click.stop="removeCustomPersona(persona)"
                       class="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded text-red-500 hover:bg-red-50"
                       :title="tr('删除自定义角色', 'Delete Custom Role')"
                     >
                       <Trash2 class="w-3.5 h-3.5" />
                     </button>
                     <div v-else class="text-[10px] text-slate-400">12:30</div>
                   </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col min-w-0 bg-[#f5f5f5] relative">
      <!-- Chat Header -->
      <header class="h-16 px-6 border-b border-[#e7e7e7] flex items-center justify-between bg-[#f5f5f5] shrink-0">
        <div class="flex items-center gap-4">
          <button class="lg:hidden p-2 text-slate-500 hover:bg-[#e0e0e0] rounded-lg transition-colors" @click="showMobileSidebar = !showMobileSidebar">
            <Menu class="w-5 h-5" />
          </button>
          <div>
            <h2 class="text-base font-bold text-slate-800 flex items-center gap-2">
              {{ currentPersona.name }}
              <span class="w-2 h-2 rounded-full bg-[#07c160]" title="Online"></span>
            </h2>
            <div class="text-xs text-slate-400 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
              <span class="inline-flex items-center gap-1">
                <span>{{ tr('手机在线 -', 'Online -') }}</span>
                <span class="inline-block h-4 overflow-hidden align-middle min-w-[2.75rem]">
                  <Transition name="status-roll" mode="out-in">
                    <span :key="networkStatusLabel" class="inline-block">{{ networkStatusLabel }}</span>
                  </Transition>
                </span>
              </span>
              <span class="text-slate-300">·</span>
              <span class="truncate max-w-[11rem]" :title="currentPersonaAddressStatus">
                {{ currentPersonaAddressStatus }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-4 text-slate-500">
           <button
             @click="openMediaGenerator('audio')"
             class="hover:text-slate-800 transition-colors"
             :class="showMediaGenerator && activeMediaType === 'audio' ? 'text-[#07c160]' : ''"
             :title="tr('生成角色语音', 'Generate Voice')"
           >
             <Volume2 class="w-5 h-5" />
           </button>
           <button
             @click="openMediaGenerator('video')"
             class="hover:text-slate-800 transition-colors"
             :class="showMediaGenerator && activeMediaType === 'video' ? 'text-[#07c160]' : ''"
             :title="tr('生成角色视频', 'Generate Video')"
           >
             <Video class="w-5 h-5" />
           </button>
           <div class="w-px h-4 bg-slate-300 mx-1"></div>
           <button 
            @click="showGameSelector = !showGameSelector"
            class="flex items-center gap-1 hover:text-slate-800 transition-colors relative"
           >
             <Gamepad2 class="w-5 h-5" />
             <div v-if="showGameSelector" class="absolute top-full right-0 mt-2 w-48 bg-white border border-slate-200 rounded-lg shadow-xl py-1 z-50 animate-in fade-in zoom-in-95 duration-200">
               <button v-for="game in games" :key="game.id" @click="switchGame(game)" class="w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center gap-2">
                 <span class="w-2 h-2 rounded-full" :style="{ background: game.themeColor }"></span>
                 {{ game.name }}
               </button>
             </div>
           </button>
           <button
            @click="openMomentsPanel"
            class="relative hover:text-slate-800 transition-colors"
            :title="tr('朋友圈', 'Moments')"
           >
             <Heart class="w-5 h-5" />
             <span
               v-if="momentsUnreadCount > 0"
               class="absolute -top-1.5 -right-2 min-w-[1rem] h-4 px-1 rounded-full bg-[#07c160] text-white text-[10px] leading-4 text-center"
             >
               {{ momentsUnreadCount > 99 ? '99+' : momentsUnreadCount }}
             </span>
           </button>
           <button
            @click="openNovelStoryPage"
            class="px-2 py-1 rounded border border-indigo-200 text-indigo-700 text-xs hover:bg-indigo-50 transition-colors"
            :title="tr('打开小说剧情', 'Open Novel Story')"
           >
            {{ tr('小说', 'Novel') }}
           </button>
           <button
            @click="openPlazaPage"
            class="px-2 py-1 rounded border border-emerald-200 text-emerald-700 text-xs hover:bg-emerald-50 transition-colors"
            :title="tr('打开广场', 'Open Plaza')"
           >
            {{ tr('广场', 'Plaza') }}
           </button>
           <button @click="clearHistory" class="hover:text-red-500 transition-colors" :title="tr('清空聊天记录', 'Clear Chat History')"><Trash2 class="w-5 h-5" /></button>
        </div>
      </header>

      <!-- Messages Area -->
      <section class="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 scroll-smooth bg-[#f5f5f5]" ref="chatContainer">
        <!-- Default Empty State -->
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full select-none text-slate-400">
           <div class="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center mb-4">
             <MessageSquare class="w-8 h-8 text-slate-400" />
           </div>
           <p class="text-sm">{{ tr('暂无消息，开始聊天吧', 'No messages yet. Start chatting.') }}</p>
        </div>

        <div 
          v-for="(msg, idx) in messages" 
          :key="idx" 
          class="flex w-full mb-4"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
           <!-- Assistant Avatar (Left) -->
           <div v-if="msg.role !== 'user'" class="w-9 h-9 rounded-md overflow-hidden shrink-0 mr-3 self-start cursor-pointer hover:opacity-90">
              <img :src="currentPersona.avatar" class="w-full h-full object-cover" />
           </div>

           <!-- Bubble -->
           <div class="max-w-[70%] min-w-[20px]">
              <!-- Name & Time (Optional, for group chat feel) -->
              <div v-if="msg.role !== 'user'" class="text-[10px] text-slate-400 mb-1 ml-1">{{ currentPersona.name }}</div>
              
              <div 
                class="relative px-3 py-2.5 rounded-lg text-[15px] leading-relaxed shadow-sm break-words"
                :class="[
                  msg.role === 'user' 
                    ? 'bg-[#95ec69] text-black rounded-tr-none' 
                    : 'bg-white text-slate-800 border border-[#e7e7e7] rounded-tl-none'
                ]"
              >
                 <!-- Bubble Tail (CSS Triangle) -->
                 <div v-if="msg.role === 'user'" class="absolute top-3 -right-1.5 w-3 h-3 bg-[#95ec69] transform rotate-45 rounded-sm"></div>
                 <div v-else class="absolute top-3 -left-1.5 w-3 h-3 bg-white border-l border-b border-[#e7e7e7] transform rotate-45 rounded-sm"></div>

                 <!-- Quest Card -->
                 <div v-if="msg.questData" class="mb-2 p-2 bg-white/50 rounded border border-black/5 text-xs">
                    <div class="font-bold mb-1 flex items-center gap-1 text-[#07c160]">
                      {{ currentGame.questIcon || '📜' }} {{ msg.questData.quest }}
                    </div>
                    <p class="mb-1 opacity-80">{{ msg.questData.description }}</p>
                    <a v-if="msg.questData.link" :href="msg.questData.link" target="_blank" class="text-blue-600 underline">{{ tr('查看详情', 'View Details') }}</a>
                 </div>

                 <!-- Character Card -->
                 <div v-if="msg.cardData" 
                      @click="openCharacterModal(msg.cardData!)"
                      class="rounded-lg overflow-hidden border border-slate-100 shadow-sm max-w-[280px] bg-white mt-1 mb-1 relative group cursor-pointer hover:shadow-md transition-shadow">
                    <!-- Image Area -->
                    <div class="relative h-48 w-full overflow-hidden">
                      <img :src="msg.cardData.avatar" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                      <!-- Gradient Overlay -->
                      <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent flex flex-col justify-end p-4">
                         <h3 class="text-white font-bold text-xl drop-shadow-md leading-tight mb-0.5">{{ msg.cardData.name }}</h3>
                         <div class="w-8 h-0.5 bg-[#07c160] rounded-full mb-1"></div>
                      </div>
                    </div>
                    
                    <!-- Content Area -->
                    <div class="p-4 bg-white relative">
                       <!-- Tag -->
                       <div class="absolute -top-3 right-4 bg-[#07c160] text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm">
                         {{ tr('角色档案', 'Role Card') }}
                       </div>
                       
                       <p class="text-xs text-slate-500 leading-relaxed line-clamp-3 mb-2 opacity-90">
                         {{ msg.cardData.description }}
                       </p>
                       
                       <div class="flex items-center gap-2 mt-3 pt-3 border-t border-slate-50">
                          <div class="flex -space-x-1.5">
                            <div class="w-4 h-4 rounded-full bg-slate-100 border border-white"></div>
                            <div class="w-4 h-4 rounded-full bg-slate-200 border border-white"></div>
                            <div class="w-4 h-4 rounded-full bg-slate-300 border border-white flex items-center justify-center text-[8px] text-slate-500">+</div>
                          </div>
                          <span class="text-[10px] text-slate-400">{{ tr('查看详细设定 >', 'View Full Setup >') }}</span>
                       </div>
                    </div>
                 </div>

                 <div v-if="msg.mediaData" class="rounded-lg overflow-hidden border border-slate-200 bg-white/90 mt-1 mb-2 p-2">
                   <img
                     v-if="msg.mediaData.type === 'image'"
                     :src="msg.mediaData.src"
                     :alt="msg.mediaData.name || 'uploaded image'"
                     class="block w-full max-w-[520px] rounded-md border border-slate-100"
                   />
                   <video
                     v-else-if="msg.mediaData.type === 'video'"
                     controls
                     playsinline
                     :src="msg.mediaData.src"
                     class="block w-full max-w-[520px] rounded-md border border-slate-100 bg-black"
                   ></video>
                   <audio
                     v-else
                     controls
                     :src="msg.mediaData.src"
                     class="block w-full max-w-[520px]"
                   ></audio>
                   <div class="mt-1 text-[11px] text-slate-500 flex flex-wrap items-center gap-2">
                     <span>{{ msg.mediaData.origin === 'user_upload' ? tr('用户上传', 'Uploaded') : tr('AI生成', 'AI') }}{{ mediaLabelByType(msg.mediaData.type) }}</span>
                     <span v-if="msg.mediaData.name">{{ msg.mediaData.name }}</span>
                     <span v-if="msg.mediaData.sizeLabel">{{ msg.mediaData.sizeLabel }}</span>
                   </div>
                 </div>

                 <!-- Content -->
                 <template v-if="msg.content">
                   <div
                     v-if="hasIsolatedHtmlSnippet(msg.content)"
                     class="mt-1 rounded-lg overflow-hidden border border-slate-200 bg-white"
                   >
                     <iframe
                       class="w-full border-0 bg-white"
                       :sandbox="'allow-scripts allow-forms'"
                       :srcdoc="getMessageHtmlSrcdoc(msg, idx)"
                       :style="{ height: `${getMessageFrameHeight(idx)}px` }"
                     ></iframe>
                   </div>
                   <template v-else>
                     <div 
                       class="prose prose-sm max-w-none break-words relative z-10"
                       :class="{'animate-pulse': msg.isTyping}"
                       v-html="renderMarkdown(getRenderableMessageContent(msg))"
                     ></div>
                     <button
                       v-if="isMessageCollapsible(msg)"
                       @click="toggleMessageExpanded(msg)"
                       class="mt-2 text-[11px] text-slate-500 hover:text-slate-700 underline underline-offset-2"
                     >
                       {{ msg.expanded ? tr('收起', 'Collapse') : tr('展开全文', 'Expand') }}
                     </button>
                   </template>
                 </template>
              </div>
           </div>

           <!-- User Avatar (Right) -->
           <div v-if="msg.role === 'user'" class="w-9 h-9 rounded-md overflow-hidden shrink-0 ml-3 self-start cursor-pointer hover:opacity-90">
              <img :src="userAvatarDisplay" class="w-full h-full object-cover" />
           </div>
        </div>
        
        <!-- Loading -->
        <div v-if="isTyping && !isStreaming" class="flex w-full justify-start mb-4">
           <div class="w-9 h-9 rounded-md overflow-hidden shrink-0 mr-3 bg-slate-200"></div>
           <div class="bg-white border border-[#e7e7e7] px-4 py-3 rounded-lg rounded-tl-none flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-100"></span>
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-200"></span>
           </div>
        </div>
      </section>

      <!-- Input Area -->
      <div class="h-auto min-h-[140px] bg-[#f5f5f5] border-t border-[#e7e7e7] flex flex-col relative z-20">
         <!-- Toolbar -->
         <div class="h-10 px-4 flex items-center gap-4 text-slate-500">
            <button
              @click="openMediaGenerator('image')"
              class="hover:text-slate-800 transition-colors"
              :class="showMediaGenerator && activeMediaType === 'image' ? 'text-[#07c160]' : ''"
              :title="tr('AI生成图片', 'AI Generate Image')"
            >
              <Image class="w-5 h-5" />
            </button>
            <button
              @click="openMediaGenerator('video')"
              class="hover:text-slate-800 transition-colors"
              :class="showMediaGenerator && activeMediaType === 'video' ? 'text-[#07c160]' : ''"
              :title="tr('AI生成视频', 'AI Generate Video')"
            >
              <Video class="w-5 h-5" />
            </button>
            <button
              @click="openMediaGenerator('audio')"
              class="hover:text-slate-800 transition-colors"
              :class="showMediaGenerator && activeMediaType === 'audio' ? 'text-[#07c160]' : ''"
              :title="tr('AI生成语音', 'AI Generate Voice')"
            >
              <Volume2 class="w-5 h-5" />
            </button>
            <button @click="showVariablePicker = !showVariablePicker" class="hover:text-slate-800 transition-colors"><Braces class="w-5 h-5" /></button>
            <button
              @click="openUserMediaPicker"
              class="hover:text-slate-800 transition-colors"
              :title="tr('上传图片/视频/语音', 'Upload Image/Video/Audio')"
            >
              <Upload class="w-5 h-5" />
            </button>
            <input
              ref="userMediaInputRef"
              type="file"
              accept="image/*,video/*,audio/*"
              class="hidden"
              @change="handleUserMediaUpload"
            >
            <div class="flex-1"></div>
            <button class="hover:text-slate-800 transition-colors" :title="tr('聊天记录', 'Chat History')"><MessageSquare class="w-5 h-5" /></button>
         </div>

         <div v-if="showMediaGenerator" class="px-4 pb-2">
           <div class="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
             <div class="flex items-center justify-between">
               <div class="text-xs font-semibold text-slate-700">{{ tr('AI', 'AI') }}{{ activeMediaLabel }}{{ tr('生成', ' Generate') }}</div>
               <button @click="showMediaGenerator = false" class="text-slate-400 hover:text-slate-600">
                 <X class="w-4 h-4" />
               </button>
             </div>
             <textarea
               v-model="mediaPromptInput"
               class="w-full h-16 border border-slate-200 rounded px-3 py-2 text-xs resize-none"
               :placeholder="mediaPromptPlaceholder"
             ></textarea>
              <div v-if="activeMediaType === 'audio'" class="space-y-2">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div class="flex items-center gap-2">
                    <label class="text-xs text-slate-500 shrink-0">{{ tr('语音音色', 'Voice') }}</label>
                    <select v-model="mediaVoice" class="text-xs border border-slate-200 rounded px-2 py-1 bg-white w-full">
                      <option v-for="voice in MEDIA_VOICE_OPTIONS" :key="voice.value" :value="voice.value">
                        {{ voice.label }}
                      </option>
                    </select>
                  </div>
                  <div class="flex items-center gap-2">
                    <label class="text-xs text-slate-500 shrink-0">{{ tr('语音风格', 'Style') }}</label>
                    <select v-model="mediaVoiceStylePreset" class="text-xs border border-slate-200 rounded px-2 py-1 bg-white w-full">
                      <option v-for="preset in mediaVoiceStyleOptions" :key="preset.value" :value="preset.value">
                        {{ preset.label }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div class="flex items-center gap-2">
                    <label class="text-xs text-slate-500 shrink-0">{{ tr('情绪', 'Emotion') }}</label>
                    <select v-model="mediaVoiceEmotion" class="text-xs border border-slate-200 rounded px-2 py-1 bg-white w-full">
                      <option v-for="emotion in mediaVoiceEmotionOptions" :key="emotion.value" :value="emotion.value">
                        {{ emotion.label }}
                      </option>
                    </select>
                  </div>
                  <div class="flex items-center gap-2">
                    <label class="text-xs text-slate-500 shrink-0">{{ tr('语速', 'Speed') }}</label>
                    <input
                      v-model.number="mediaSpeechRate"
                      type="range"
                      min="0.75"
                      max="1.35"
                      step="0.05"
                      class="w-full"
                    >
                    <span class="text-[11px] text-slate-500 min-w-[2.5rem] text-right">{{ mediaSpeechRate.toFixed(2) }}x</span>
                  </div>
                </div>
                <input
                  v-model="mediaVoiceCustomStyle"
                  type="text"
                  :placeholder="tr('可选：补充个性化声音描述（如：低沉磁性、轻快少女感、电台播音腔）', 'Optional: add custom voice style hints')"
                  class="w-full border border-slate-200 rounded px-3 py-2 text-xs"
                >
                <p class="text-[11px] text-slate-500">
                  {{ tr('工具箱推荐音色：', 'Toolbox recommended voice: ') }}{{ getVoiceLabel(resolvePrimaryVoiceForPersona(currentPersona)) }}（{{ tr('模式', 'Mode') }}：{{ voiceToolboxModeOptions.find((item) => item.value === voiceToolboxSettings.mode)?.label || tr('严格自动', 'Auto Strict') }}）
                </p>
              </div>
             <div class="flex flex-wrap items-center gap-2">
               <button
                 @click="generateMediaFromContext()"
                 :disabled="isGeneratingMedia || (activeMediaType === 'image' ? !isImageConnected : activeMediaType === 'audio' ? !isAudioConnected : !isConnected)"
                 class="px-3 py-1.5 rounded text-xs font-medium border border-[#07c160]/40 text-[#07c160] hover:bg-[#07c160]/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
               >
                 {{ isGeneratingMedia ? tr('生成中...', 'Generating...') : `${tr('生成', 'Generate ')}${activeMediaLabel}` }}
               </button>
               <span class="text-[11px] text-slate-500">{{ tr('自动结合当前角色卡与最近对话上下文。', 'Automatically uses current role card and recent chat context.') }}</span>
             </div>
             <div v-if="mediaGenerateInfo" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
               {{ mediaGenerateInfo }}
             </div>
             <div v-if="mediaGenerateError" class="text-xs text-red-500 bg-red-50 border border-red-200 rounded px-3 py-2">
               {{ mediaGenerateError }}
             </div>
           </div>
         </div>

         <div v-if="userMediaUploadInfo || userMediaUploadError" class="px-4 pb-2">
           <div
             class="text-xs rounded px-3 py-2 border"
             :class="userMediaUploadError ? 'text-red-600 bg-red-50 border-red-200' : 'text-emerald-700 bg-emerald-50 border-emerald-200'"
           >
             {{ userMediaUploadError || userMediaUploadInfo }}
           </div>
         </div>
         
         <!-- Textarea -->
         <div class="flex-1 px-4 pb-2">
            <textarea
              v-model="inputMessage"
              @keydown.enter.prevent="handleEnter"
              ref="inputTextarea"
              class="w-full h-full bg-transparent border-none p-0 resize-none focus:ring-0 text-sm leading-relaxed text-slate-800 placeholder:text-slate-400 custom-scrollbar"
              :disabled="isTyping"
            ></textarea>
         </div>
         
         <!-- Bottom Actions -->
         <div class="h-12 px-4 flex items-center justify-between pb-2">
            <div class="text-xs text-slate-400">{{ tr('按 Enter 发送', 'Press Enter to send') }}</div>
            <button 
              @click="sendMessage"
              :disabled="!inputMessage.trim() || isTyping"
              class="px-6 py-1.5 bg-[#e9e9e9] hover:bg-[#d2d2d2] text-[#07c160] font-medium rounded text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
               {{ tr('发送 (S)', 'Send (S)') }}
            </button>
         </div>

         <!-- Variable Picker Popup -->
         <div v-if="showVariablePicker" class="absolute bottom-full left-4 mb-2 w-40 bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden z-50">
            <button v-for="v in availableVariables" :key="v" @click="insertVariable(v)" 
                    class="w-full text-left px-3 py-2 text-xs hover:bg-slate-50 border-b border-slate-100 last:border-0"
            >{{ v }}</button>
         </div>
      </div>
    </main>
    <!-- Persona Creator Modal -->
    <div v-if="showPersonaCreator" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-5xl overflow-hidden flex flex-col max-h-[92vh]">
        <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-[#f8f8f8]">
          <div>
            <h3 class="font-semibold text-slate-800">{{ tr('创建自定义角色', 'Create Custom Role') }}</h3>
            <p class="text-xs text-slate-500 mt-1">{{ tr('填写角色卡并上传头像后，可立即加入左侧角色列表。', 'Fill in the role card and upload an avatar to add it to the left list instantly.') }}</p>
          </div>
          <button @click="closePersonaCreator" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div ref="personaCreatorBodyRef" class="flex-1 overflow-y-auto p-5 md:p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section class="space-y-3">
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2">
              <div>
                <h4 class="text-sm font-semibold text-slate-800">{{ tr('角色卡导入（JSON / PNG）', 'Role Card Import (JSON / PNG)') }}</h4>
                <p class="text-xs text-slate-500 mt-1">{{ tr('上传角色卡后将自动填充名称、简介、系统提示词、首条消息与分组。', 'After upload, name, bio, system prompt, first message, and group will be auto-filled.') }}</p>
              </div>
              <input
                type="file"
                accept=".json,image/png"
                @change="handlePersonaCardUpload"
                class="block w-full text-xs text-slate-500 file:mr-3 file:px-3 file:py-1.5 file:rounded file:border-0 file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
              >
              <p class="text-[11px] text-slate-500 leading-relaxed">
                {{ tr('支持 Tavern 角色卡 JSON 与内嵌 PNG 角色卡。导入后可继续手动编辑，再点击右下角“创建角色”。', 'Supports Tavern JSON cards and PNG cards with embedded metadata. You can continue editing manually, then click Create Role.') }}
              </p>
              <div class="flex flex-wrap items-center gap-2">
                <button
                  @click="autoCompletePersonaForm"
                  :disabled="isAutoCompletingPersona || !isConnected || personaMissingFieldKeys.length === 0"
                  class="px-3 py-1.5 rounded text-xs font-medium border border-[#07c160]/40 text-[#07c160] hover:bg-[#07c160]/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                >
                  {{ isAutoCompletingPersona ? tr('AI补全中...', 'AI filling...') : tr('AI自动补全未填写项', 'AI Fill Empty Fields') }}
                </button>
                <span class="text-[11px] text-slate-500">{{ tr('仅补充空字段，不覆盖已填写内容（需已配置可用 API）。', 'Only fills empty fields and does not overwrite existing values (requires configured API).') }}</span>
              </div>
              <div v-if="personaCardImportInfo" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
                {{ personaCardImportInfo }}
              </div>
              <div v-if="personaCardImportError" class="text-xs text-red-500 bg-red-50 border border-red-200 rounded px-3 py-2">
                {{ personaCardImportError }}
              </div>
              <div v-if="personaAutoFillInfo" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
                {{ personaAutoFillInfo }}
              </div>
              <div v-if="personaAutoFillError" class="text-xs text-red-500 bg-red-50 border border-red-200 rounded px-3 py-2">
                {{ personaAutoFillError }}
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('角色名称（必填）', 'Role Name (Required)') }}</label>
              <input
                ref="personaNameInputRef"
                v-model="personaForm.name"
                type="text"
                :placeholder="tr('例如：庄闻', 'e.g. Zhuang Wen')"
                class="w-full border border-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#07c160]/40"
              >
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('昵称', 'Nickname') }}</label>
                <input v-model="personaForm.nickname" type="text" :placeholder="tr('例如：庄教授', 'e.g. Professor Zhuang')" class="w-full border border-slate-200 rounded px-3 py-2 text-sm">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('分组', 'Group') }}</label>
                <input v-model="personaForm.group" type="text" :placeholder="tr('默认：自定义角色', 'Default: Custom Roles')" class="w-full border border-slate-200 rounded px-3 py-2 text-sm">
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('年龄', 'Age') }}</label>
                <input v-model="personaForm.age" type="text" placeholder="28" class="w-full border border-slate-200 rounded px-3 py-2 text-sm">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('性别', 'Gender') }}</label>
                <input v-model="personaForm.gender" type="text" :placeholder="tr('男', 'male')" class="w-full border border-slate-200 rounded px-3 py-2 text-sm">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('头衔', 'Title') }}</label>
                <input v-model="personaForm.title" type="text" :placeholder="tr('法学天才', 'Law prodigy')" class="w-full border border-slate-200 rounded px-3 py-2 text-sm">
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('角色简介（推荐）', 'Role Bio (Recommended)') }}</label>
              <textarea
                v-model="personaForm.description"
                class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                :placeholder="tr('显示在角色列表和角色卡预览中', 'Shown in the role list and role-card preview')"
              ></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('性格', 'Personality') }}</label>
                <textarea
                  v-model="personaForm.personality"
                  class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                  :placeholder="tr('冷静、精准、理性', 'calm, precise, rational')"
                ></textarea>
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('背景', 'Background') }}</label>
                <textarea
                  v-model="personaForm.background"
                  class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                  :placeholder="tr('临城大学副教授', 'Associate professor at Linyu University')"
                ></textarea>
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('首条消息（推荐）', 'First Message (Recommended)') }}</label>
              <textarea
                v-model="personaForm.firstMessage"
                class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                :placeholder="tr('用户切换到该角色时自动发送', 'Auto-sent when user switches to this role')"
              ></textarea>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('系统提示词（必填）', 'System Prompt (Required)') }}</label>
              <textarea
                ref="personaSystemPromptRef"
                v-model="personaForm.systemPrompt"
                class="w-full h-28 border border-slate-200 rounded px-3 py-2 text-sm resize-none font-mono"
                :placeholder="tr('定义角色行为、语气和边界', 'Define role behavior, tone, and boundaries')"
              ></textarea>
            </div>

            <div class="space-y-2">
              <label class="block text-xs font-semibold text-slate-500">{{ tr('头像上传（PNG/JPG/WebP）', 'Avatar Upload (PNG/JPG/WebP)') }}</label>
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                @change="handlePersonaAvatarUpload"
                class="block w-full text-xs text-slate-500 file:mr-3 file:px-3 file:py-1.5 file:rounded file:border-0 file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
              >
              <input
                v-model="personaForm.avatarUrl"
                type="text"
                :placeholder="tr('或填写头像 URL', 'or enter avatar URL')"
                class="w-full border border-slate-200 rounded px-3 py-2 text-sm"
              >
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2">
                <label class="block text-xs font-semibold text-slate-600">{{ tr('AI 头像生成提示词（可选）', 'AI Avatar Prompt (Optional)') }}</label>
                <textarea
                  v-model="avatarGeneratePrompt"
                  class="w-full h-16 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                  :placeholder="tr('例如：二次元角色头像，银发，温和表情，干净背景，半身构图，细节清晰', 'e.g. anime character portrait, silver hair, gentle expression, clean background, half-body framing, clear details')"
                ></textarea>
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    @click="generatePersonaAvatarWithAI"
                    :disabled="isGeneratingAvatar || !isImageConnected"
                    class="px-3 py-1.5 rounded text-xs font-medium border border-[#07c160]/40 text-[#07c160] hover:bg-[#07c160]/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                  >
                    {{ isGeneratingAvatar ? tr('生成中...', 'Generating...') : tr('AI自动生成头像', 'AI Generate Avatar') }}
                  </button>
                  <span class="text-[11px] text-slate-500">{{ tr('使用“AI 生图接口”生成头像（支持 Gemini v1beta 与 images/generations）。', 'Generate avatar using AI Image API (supports Gemini v1beta and images/generations).') }}</span>
                </div>
                <div v-if="avatarGenerateInfo" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
                  {{ avatarGenerateInfo }}
                </div>
                <div v-if="avatarGenerateError" class="text-xs text-red-500 bg-red-50 border border-red-200 rounded px-3 py-2">
                  {{ avatarGenerateError }}
                </div>
              </div>
              <div v-if="personaForm.avatarPreview" class="flex items-center gap-3">
                <img :src="personaForm.avatarPreview" class="w-14 h-14 rounded-md object-cover border border-slate-200" alt="avatar preview">
                <button @click="clearPersonaAvatar" class="text-xs text-red-500 hover:text-red-600">{{ tr('移除头像', 'Remove Avatar') }}</button>
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <h4 class="text-sm font-semibold text-slate-800 mb-2">{{ tr('角色卡字段说明', 'Role Card Field Guide') }}</h4>
              <ul class="text-xs text-slate-600 space-y-1 leading-relaxed">
                <li><span class="font-semibold text-slate-700">name</span>{{ tr('：角色显示名，用于列表、头部与聊天。', ': display name used in list, header, and chats.') }}</li>
                <li><span class="font-semibold text-slate-700">description</span>{{ tr('：角色简介，用于侧边栏与卡片预览。', ': short bio shown in sidebar and card preview.') }}</li>
                <li><span class="font-semibold text-slate-700">systemPrompt</span>{{ tr('：核心人设定义，决定模型输出风格。', ': core persona instruction that shapes output style.') }}</li>
                <li><span class="font-semibold text-slate-700">firstMessage</span>{{ tr('：切换角色时自动发送的开场白。', ': opening line auto-sent when switching roles.') }}</li>
                <li><span class="font-semibold text-slate-700">group</span>{{ tr('：侧边栏分组，便于管理角色。', ': sidebar grouping for role management.') }}</li>
                <li><span class="font-semibold text-slate-700">avatar</span>{{ tr('：角色头像，强化视觉识别与沉浸感。', ': role avatar for stronger visual identity.') }}</li>
              </ul>
            </div>

            <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <h4 class="text-sm font-semibold text-slate-800 mb-2">{{ tr('推荐 JSON 示例', 'Recommended JSON Example') }}</h4>
              <pre v-if="isChineseLocale" class="text-[11px] leading-relaxed text-slate-700 bg-white border border-slate-200 rounded p-3 overflow-x-auto">{
  "name": "庄闻",
  "description": "法学副教授，冷静克制，逻辑严谨。",
  "systemPrompt": "你是庄闻，请保持回答克制、简洁、严谨。",
  "firstMessage": "*他透过镜片看向你，微微点头。*",
  "group": "自定义角色",
  "avatar": "https://example.com/avatar.webp"
}</pre>
              <pre v-else class="text-[11px] leading-relaxed text-slate-700 bg-white border border-slate-200 rounded p-3 overflow-x-auto">{
  "name": "Zhuang Wen",
  "description": "Associate law professor. Calm, restrained, and rigorous.",
  "systemPrompt": "You are Zhuang Wen. Keep responses concise, restrained, and rigorous.",
  "firstMessage": "*He looks at you through his glasses and nods slightly.*",
  "group": "Custom Roles",
  "avatar": "https://example.com/avatar.webp"
}</pre>
            </div>

            <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
              <h4 class="text-sm font-semibold text-emerald-700 mb-2">{{ tr('图片上传要求', 'Image Upload Requirements') }}</h4>
              <ul class="text-xs text-emerald-700 space-y-1 leading-relaxed">
                <li>{{ tr('支持格式：PNG / JPG / WebP。', 'Formats: PNG / JPG / WebP.') }}</li>
                <li>{{ tr('文件上限：2MB（建议 200KB - 1MB）。', 'Max size: 2MB (recommended 200KB - 1MB).') }}</li>
                <li>{{ tr('分辨率：至少 512x512，推荐 768x1024 或 1:1。', 'Resolution: at least 512x512, recommended 768x1024 or 1:1.') }}</li>
                <li>{{ tr('建议使用清晰、主体居中的角色头像。', 'Use clear avatars with centered subjects.') }}</li>
                <li>{{ tr('避免严重模糊、压缩噪点和明显水印。', 'Avoid heavy blur, compression noise, and obvious watermarks.') }}</li>
              </ul>
            </div>

            <div v-if="personaCreateError" class="text-xs text-red-500 bg-red-50 border border-red-200 rounded px-3 py-2">
              {{ personaCreateError }}
            </div>
          </section>
        </div>

        <div class="p-4 border-t border-slate-100 bg-[#f8f8f8] flex items-center justify-end gap-2">
          <p v-if="personaCreateError" class="mr-auto text-xs text-red-500">
            {{ personaCreateError }}
          </p>
          <p v-else-if="!canCreatePersona" class="mr-auto text-xs text-amber-600">
            {{ tr('请先填写：', 'Please fill: ') }}{{ personaCreateMissingLabels.join(isChineseLocale ? '、' : ', ') }}
          </p>
          <button @click="closePersonaCreator" class="px-4 py-1.5 border border-slate-200 rounded text-sm hover:bg-slate-100">{{ tr('取消', 'Cancel') }}</button>
          <button
            @click="createPersona"
            :disabled="!canCreatePersona"
            class="px-4 py-1.5 bg-[#07c160] text-white rounded text-sm hover:bg-[#06ad56] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#07c160]"
          >
            {{ tr('创建角色', 'Create Role') }}
          </button>
        </div>
      </div>
    </div>

    <!-- User Profile Editor -->
    <div v-if="showUserProfileEditor" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[92vh]">
        <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-[#f8f8f8]">
          <div>
            <h3 class="font-semibold text-slate-800">{{ tr('用户自定义设定', 'User Custom Profile') }}</h3>
            <p class="text-xs text-slate-500 mt-1">{{ tr('支持手动填写、AI补全与一键AI生成。', 'Supports manual editing, AI completion, and one-click AI generation.') }}</p>
          </div>
          <button @click="closeUserProfileEditor" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 md:p-6 space-y-4">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="space-y-3">
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('自定义名字', 'Custom Name') }}</label>
                <div class="flex gap-2">
                  <input v-model="userProfile.name" type="text" class="flex-1 border border-slate-200 rounded px-3 py-2 text-sm" :placeholder="tr('例如：小满', 'e.g. Mia')">
                  <button
                    @click="generateUserNameWithAI"
                    :disabled="isGeneratingUserProfileText || !isConnected"
                    class="px-3 py-2 text-xs rounded border border-[#07c160]/40 text-[#07c160] hover:bg-[#07c160]/10 disabled:opacity-50"
                  >
                    {{ tr('AI生成', 'AI Generate') }}
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('自定义性别', 'Custom Gender') }}</label>
                <input v-model="userProfile.gender" type="text" class="w-full border border-slate-200 rounded px-3 py-2 text-sm" :placeholder="tr('例如：女 / 男 / 非二元 / 不设定', 'e.g. female / male / non-binary / prefer not to say')">
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('性格（可选）', 'Personality (Optional)') }}</label>
                <textarea v-model="userProfile.personality" class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none" :placeholder="tr('例如：外向，幽默，乐观', 'e.g. outgoing, humorous, optimistic')"></textarea>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('特点（可选）', 'Traits (Optional)') }}</label>
                <textarea v-model="userProfile.traits" class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none" :placeholder="tr('例如：喜欢旅行、摄影、夜跑', 'e.g. likes travel, photography, night running')"></textarea>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tr('聊天风格（可选）', 'Chat Style (Optional)') }}</label>
                <textarea v-model="userProfile.chatStyle" class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none" :placeholder="tr('例如：简洁直白、喜欢表情、偏理性', 'e.g. concise, likes emojis, more rational')"></textarea>
              </div>
            </div>

            <div class="space-y-3">
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <label class="block text-xs font-semibold text-slate-600 mb-2">{{ tr('自定义图像', 'Custom Avatar') }}</label>
                <div class="flex items-center gap-3 mb-2">
                  <img :src="userAvatarDisplay" class="w-16 h-16 rounded-lg border border-slate-200 object-cover" alt="user avatar">
                  <button @click="clearUserAvatar" class="text-xs text-red-500 hover:text-red-600">{{ tr('移除头像', 'Remove Avatar') }}</button>
                </div>
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  @change="handleUserAvatarUpload"
                  class="block w-full text-xs text-slate-500 file:mr-3 file:px-3 file:py-1.5 file:rounded file:border-0 file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
                >
                <input
                  v-model="userProfile.avatarUrl"
                  type="text"
                  class="w-full border border-slate-200 rounded px-3 py-2 text-sm mt-2"
                  :placeholder="tr('或填写头像 URL', 'or enter avatar URL')"
                >
              </div>

              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2">
                <label class="block text-xs font-semibold text-slate-600">{{ tr('AI头像提示词（可选）', 'AI Avatar Prompt (Optional)') }}</label>
                <textarea
                  v-model="userProfile.avatarPrompt"
                  class="w-full h-16 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                  :placeholder="tr('例如：清爽自然风头像，柔和光线，近景构图', 'e.g. clean natural avatar, soft lighting, close-up composition')"
                ></textarea>
                <div class="flex flex-wrap gap-2">
                  <button
                    @click="generateUserAvatarWithAI"
                    :disabled="isGeneratingUserAvatar || !isImageConnected"
                    class="px-3 py-1.5 text-xs rounded border border-[#07c160]/40 text-[#07c160] hover:bg-[#07c160]/10 disabled:opacity-50"
                  >
                    {{ isGeneratingUserAvatar ? tr('生成中...', 'Generating...') : tr('AI生成头像', 'AI Generate Avatar') }}
                  </button>
                  <button
                    @click="generateUserProfileTextWithAI(false)"
                    :disabled="isGeneratingUserProfileText || !isConnected"
                    class="px-3 py-1.5 text-xs rounded border border-[#07c160]/40 text-[#07c160] hover:bg-[#07c160]/10 disabled:opacity-50"
                  >
                    {{ isGeneratingUserProfileText ? tr('补全中...', 'Filling...') : tr('AI补全未填写项', 'AI Fill Empty Fields') }}
                  </button>
                  <button
                    @click="oneClickGenerateUserProfile"
                    :disabled="isGeneratingUserProfileOneClick || !isConnected"
                    class="px-3 py-1.5 text-xs rounded bg-[#07c160] text-white hover:bg-[#06ad56] disabled:opacity-50"
                  >
                    {{ isGeneratingUserProfileOneClick ? tr('一键生成中...', 'Generating...') : tr('一键AI生成全部', 'One-click AI generate all') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="userProfileInfo" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
            {{ userProfileInfo }}
          </div>
          <div v-if="userProfileError" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
            {{ userProfileError }}
          </div>
        </div>

        <div class="p-4 border-t border-slate-100 bg-[#f8f8f8] flex justify-end gap-2">
          <button @click="closeUserProfileEditor" class="px-4 py-1.5 border border-slate-200 rounded text-sm hover:bg-slate-100">{{ tr('取消', 'Cancel') }}</button>
          <button @click="saveUserProfileFromEditor" class="px-4 py-1.5 bg-[#07c160] text-white rounded text-sm hover:bg-[#06ad56]">{{ tr('保存设定', 'Save Profile') }}</button>
        </div>
      </div>
    </div>

    <!-- Moments Panel -->
    <div v-if="showMomentsPanel" class="fixed inset-0 z-50 flex items-center justify-center bg-black/35 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-5xl overflow-hidden flex flex-col max-h-[92vh]">
        <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-[#f8f8f8]">
          <div>
            <h3 class="font-semibold text-slate-800">{{ tr('朋友圈', 'Moments') }}</h3>
            <p class="text-xs text-slate-500 mt-1">{{ tr('发动态、点赞评论，与 AI 角色持续互动。', 'Post updates, like/comment, and keep interacting with AI roles.') }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="refreshMomentsFeed"
              class="px-3 py-1.5 rounded text-xs border border-slate-200 hover:bg-slate-100 text-slate-600 inline-flex items-center gap-1"
              :title="tr('刷新动态', 'Refresh Feed')"
              :disabled="isRefreshingMomentsTrend"
            >
              <RefreshCw class="w-3.5 h-3.5" :class="isRefreshingMomentsTrend ? 'animate-spin' : ''" />
              {{ isRefreshingMomentsTrend ? tr('刷新热点中...', 'Refreshing trends...') : tr('刷新动态', 'Refresh') }}
            </button>
            <button @click="closeMomentsPanel" class="text-slate-400 hover:text-slate-600">
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div class="px-4 py-2.5 border-b border-slate-100 bg-white">
          <div class="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1 text-xs">
            <button
              class="px-3 py-1.5 rounded transition-colors"
              :class="momentsPanelTab === 'feed' ? 'bg-white shadow text-slate-800' : 'text-slate-600 hover:text-slate-800'"
              @click="momentsPanelTab = 'feed'"
            >
              {{ tr('朋友圈', 'Moments') }}
            </button>
            <button
              class="px-3 py-1.5 rounded transition-colors"
              :class="momentsPanelTab === 'group' ? 'bg-white shadow text-slate-800' : 'text-slate-600 hover:text-slate-800'"
              @click="momentsPanelTab = 'group'"
            >
              {{ tr('群聊', 'Group Chat') }}
            </button>
          </div>
        </div>

        <div v-if="momentsPanelTab === 'feed'" class="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[1fr_280px]">
          <section class="p-4 md:p-5 overflow-y-auto custom-scrollbar space-y-4 bg-[#fafafa]">
            <div class="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
              <label class="text-xs font-semibold text-slate-600">{{ tr('发布朋友圈', 'Post to Moments') }}</label>
              <textarea
                v-model="momentsComposerText"
                class="w-full h-20 border border-slate-200 rounded px-3 py-2 text-sm resize-none"
                :placeholder="tr('分享一下今天的想法...', 'Share your thoughts today...')"
              ></textarea>
              <div class="flex items-center justify-between">
                <span class="text-[11px] text-slate-500 truncate pr-3" :title="momentsTrendSummary">
                  {{ momentsTrendSummary }}
                </span>
                <button
                  @click="publishMoment"
                  :disabled="isPublishingMoment || !momentsComposerText.trim()"
                  class="px-3 py-1.5 bg-[#07c160] text-white rounded text-xs hover:bg-[#06ad56] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ isPublishingMoment ? tr('发布中...', 'Publishing...') : tr('发布动态', 'Publish') }}
                </button>
              </div>
              <div v-if="momentsInfo" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
                {{ momentsInfo }}
              </div>
              <div v-if="momentsError" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
                {{ momentsError }}
              </div>
            </div>

            <div v-if="momentsPosts.length === 0" class="rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
              {{ tr('还没有动态，发第一条朋友圈吧。', 'No posts yet. Publish your first moment.') }}
            </div>

            <article
              v-for="post in momentsPosts"
              :key="post.id"
              class="rounded-xl border border-slate-200 bg-white p-4 space-y-3 shadow-sm"
            >
              <div class="flex items-start gap-3">
                <img :src="post.authorAvatar" :alt="post.authorName" class="w-10 h-10 rounded-lg object-cover border border-slate-100">
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-semibold text-slate-800 truncate">{{ post.authorName }}</div>
                  <div class="text-[11px] text-slate-400">{{ formatMomentTime(post.createdAt) }}</div>
                </div>
                <button
                  v-if="post.authorId === 'user'"
                  @click="removeMomentPost(post.id)"
                  class="text-[11px] text-red-500 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50 shrink-0"
                  :title="tr('删除这条朋友圈', 'Delete this post')"
                >
                  {{ tr('删除', 'Delete') }}
                </button>
              </div>

              <p class="text-sm leading-relaxed text-slate-700 whitespace-pre-wrap break-words">{{ post.content }}</p>

              <div class="flex items-center gap-4 text-xs text-slate-500">
                <button
                  @click="toggleMomentLike(post)"
                  class="inline-flex items-center gap-1 hover:text-[#07c160]"
                  :class="post.likedByUser ? 'text-[#07c160]' : ''"
                >
                  <Heart class="w-3.5 h-3.5" />
                  {{ post.likedByUser ? tr('已赞', 'Liked') : tr('点赞', 'Like') }}
                </button>
                <span>{{ tr('{count} 人点赞', '{count} likes').replace('{count}', String(getMomentLikeCount(post))) }}</span>
                <span>{{ tr('{count} 条评论', '{count} comments').replace('{count}', String(post.comments.length)) }}</span>
              </div>

              <div v-if="post.comments.length > 0" class="rounded-lg bg-slate-50 border border-slate-100 p-3 space-y-2">
                <div v-for="comment in post.comments" :key="comment.id" class="text-xs leading-relaxed text-slate-600">
                  <span class="font-semibold text-slate-700">{{ comment.authorName }}：</span>
                  <span>{{ comment.content }}</span>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <input
                  v-model="momentsCommentDrafts[post.id]"
                  type="text"
                  class="flex-1 border border-slate-200 rounded px-3 py-1.5 text-xs"
                  :placeholder="tr('写评论和 TA 互动...', 'Write a comment...')"
                  @keydown.enter.prevent="submitMomentComment(post)"
                >
                <button
                  @click="submitMomentComment(post)"
                  class="px-3 py-1.5 rounded border border-slate-200 text-xs hover:bg-slate-100 text-slate-600"
                >
                  {{ tr('评论', 'Comment') }}
                </button>
              </div>
            </article>
          </section>

          <aside class="hidden lg:flex flex-col border-l border-slate-100 bg-white p-4">
            <h4 class="text-sm font-semibold text-slate-800 mb-3">{{ tr('互动热度榜', 'Interaction Ranking') }}</h4>
            <div class="flex-1 overflow-y-auto custom-scrollbar space-y-2">
              <div
                v-for="(item, index) in momentsInteractionLeaders"
                :key="item.personaId"
                class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 flex items-center justify-between"
              >
                <div class="min-w-0">
                  <div class="text-xs text-slate-400">#{{ index + 1 }}</div>
                  <div class="text-sm font-medium text-slate-700 truncate">{{ item.name }}</div>
                </div>
                <div class="text-sm font-semibold text-[#07c160]">{{ item.score }}</div>
              </div>
              <div v-if="momentsInteractionLeaders.length === 0" class="text-xs text-slate-400 py-4">
                {{ tr('暂无互动数据，先去点赞评论吧。', 'No interaction data yet. Start liking and commenting.') }}
              </div>
            </div>
            <div class="mt-4 text-[11px] text-slate-500 leading-relaxed">
              {{ tr('规则：高互动角色将更频繁发动态（约 2-3 次/天）并更积极评论；低互动角色随机发动态并以点赞为主；自定义角色卡与内置角色同样参与全部互动机制。', 'Rules: highly interactive roles post more frequently and comment more; low-interaction roles post randomly and mostly like; custom and built-in roles all join this mechanism.') }}
            </div>
          </aside>
        </div>

        <div v-else class="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[300px_1fr]">
          <section class="border-r border-slate-100 bg-[#fafafa] p-4 space-y-3 overflow-y-auto custom-scrollbar">
            <div class="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
              <h4 class="text-xs font-semibold text-slate-700">{{ tr('创建群聊', 'Create Group') }}</h4>
              <input
                v-model="groupDraftName"
                class="w-full border border-slate-200 rounded px-2.5 py-1.5 text-xs"
                :placeholder="tr('群名称，例如：星穹创作群', 'Group name, e.g. StarRail Studio')"
              >
              <input
                v-model="groupDraftAvatar"
                class="w-full border border-slate-200 rounded px-2.5 py-1.5 text-xs"
                :placeholder="tr('群头像 URL（可留空自动生成）', 'Group avatar URL (optional)')"
              >

              <div class="space-y-1">
                <div class="text-[11px] text-slate-500">{{ tr('选择 AI 成员', 'Select AI Members') }}</div>
                <div class="max-h-24 overflow-y-auto rounded border border-slate-100 bg-slate-50 p-2 space-y-1">
                  <label v-for="persona in groupSelectableAiMembers" :key="`group_member_${persona.id}`" class="flex items-center gap-1.5 text-xs text-slate-700">
                    <input v-model="groupDraftMemberIds" :value="persona.id" type="checkbox">
                    <span class="truncate">{{ persona.name }}</span>
                  </label>
                </div>
              </div>

              <div class="space-y-1">
                <div class="text-[11px] text-slate-500">{{ tr('设置 AI 管理员', 'Set AI Admins') }}</div>
                <div class="max-h-24 overflow-y-auto rounded border border-slate-100 bg-slate-50 p-2 space-y-1">
                  <label
                    v-for="persona in groupSelectableAiMembers.filter((item) => groupDraftMemberIds.includes(item.id))"
                    :key="`group_admin_${persona.id}`"
                    class="flex items-center gap-1.5 text-xs text-slate-700"
                  >
                    <input v-model="groupDraftAiAdminIds" :value="persona.id" type="checkbox">
                    <span class="truncate">{{ persona.name }}</span>
                  </label>
                  <div v-if="groupDraftMemberIds.length === 0" class="text-[11px] text-slate-400">{{ tr('先选择成员', 'Select members first') }}</div>
                </div>
              </div>

              <button class="w-full px-2.5 py-1.5 rounded bg-[#07c160] text-white text-xs hover:bg-[#06ad56] disabled:opacity-60" :disabled="!groupDraftName.trim()" @click="createGroupChat">
                {{ tr('创建群聊', 'Create Group') }}
              </button>
            </div>

            <div class="rounded-lg border border-slate-200 bg-white p-2 space-y-1.5">
              <div class="text-xs font-semibold text-slate-700 px-1">{{ tr('我的群聊', 'My Groups') }}</div>
              <button
                v-for="room in groupChatsSorted"
                :key="room.id"
                class="w-full text-left rounded border px-2 py-2 text-xs transition-colors"
                :class="selectedGroupChatId === room.id ? 'border-[#07c160] bg-emerald-50' : 'border-slate-200 hover:bg-slate-50'"
                @click="selectGroupChat(room.id)"
              >
                <div class="flex items-center gap-2">
                  <img :src="room.avatar" :alt="room.name" class="w-7 h-7 rounded object-cover border border-slate-200 shrink-0">
                  <div class="min-w-0 flex-1">
                    <div class="truncate text-slate-800">{{ room.name }}</div>
                    <div class="text-[11px] text-slate-500 truncate">
                      {{ tr('{count} 人', '{count} members').replace('{count}', String(room.members.length)) }} · {{ room.mutedByUser ? tr('已屏蔽消息', 'Muted') : tr('正常接收', 'Receiving') }}
                    </div>
                  </div>
                </div>
              </button>
              <div v-if="groupChatsSorted.length === 0" class="text-[11px] text-slate-400 px-1 py-2">{{ tr('还没有群聊，先创建一个。', 'No groups yet. Create one first.') }}</div>
            </div>
          </section>

          <section class="p-4 md:p-5 overflow-y-auto custom-scrollbar space-y-3 bg-white">
            <template v-if="selectedGroupChat">
              <div class="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <div class="flex items-center gap-2 min-w-0">
                    <img :src="selectedGroupChat.avatar" :alt="selectedGroupChat.name" class="w-10 h-10 rounded object-cover border border-slate-200 shrink-0">
                    <div class="min-w-0">
                      <div class="text-sm font-semibold text-slate-800 truncate">{{ selectedGroupChat.name }}</div>
                      <div class="text-[11px] text-slate-500">
                        {{ tr('{count} 人', '{count} members').replace('{count}', String(selectedGroupChat.members.length)) }} · {{ selectedGroupChat.mutedByUser ? tr('你已屏蔽该群消息', 'You muted this group') : tr('群消息正常', 'Group messages normal') }} · AI{{ getGroupReplyModeLabel(selectedGroupChat.replyMode) }}{{ tr('模式', ' mode') }}
                      </div>
                    </div>
                  </div>
                  <div class="flex flex-wrap gap-1.5">
                    <button class="px-2.5 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100" @click="toggleGroupChatMute(selectedGroupChat)">
                      {{ selectedGroupChat.mutedByUser ? tr('取消屏蔽', 'Unmute') : tr('屏蔽消息', 'Mute') }}
                    </button>
                    <button class="px-2.5 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100" @click="triggerGroupAiConversation(selectedGroupChat)">
                      {{ tr('触发群内互动', 'Trigger Group Interaction') }}
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-[120px,1fr] gap-1.5 items-center">
                  <div class="text-[11px] text-slate-500">{{ tr('AI 回复频率', 'AI Reply Frequency') }}</div>
                  <select
                    v-model="selectedGroupChat.replyMode"
                    class="border border-slate-200 rounded px-2 py-1 text-[11px] bg-white"
                    @change="changeSelectedGroupReplyMode"
                  >
                    <option v-for="option in groupReplyModeOptions" :key="`group_reply_mode_${option.value}`" :value="option.value">
                      {{ option.label }}：{{ option.description }}
                    </option>
                  </select>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-[140px,1fr,auto,auto] gap-1.5 items-center">
                  <select v-model="groupAdminActorByRoomId[selectedGroupChat.id]" class="border border-slate-200 rounded px-2 py-1 text-[11px] bg-white">
                    <option value="user">{{ tr('用户管理员', 'User Admin') }}</option>
                    <option v-for="admin in selectedGroupChatAdminMembers.filter((m) => m.id !== 'user')" :key="`admin_actor_${admin.id}`" :value="admin.id">
                      {{ tr('AI管理员：', 'AI Admin: ') }}{{ admin.name }}
                    </option>
                  </select>
                  <input
                    v-model="groupRenameDraftByRoomId[selectedGroupChat.id]"
                    class="border border-slate-200 rounded px-2 py-1 text-[11px]"
                    :placeholder="tr('新群名', 'New group name')"
                  >
                  <button class="px-2 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100" @click="renameSelectedGroupChat">
                    {{ tr('修改群名', 'Rename') }}
                  </button>
                  <button class="px-2 py-1 rounded border border-rose-200 text-rose-600 text-[11px] hover:bg-rose-50" @click="dissolveSelectedGroupChat">
                    {{ tr('解散群聊', 'Dissolve Group') }}
                  </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-[140px,1fr,auto] gap-1.5 items-center">
                  <div class="text-[11px] text-slate-500">{{ tr('转让管理员（AI）', 'Transfer Admin (AI)') }}</div>
                  <select v-model="groupAdminTransferTargetByRoomId[selectedGroupChat.id]" class="border border-slate-200 rounded px-2 py-1 text-[11px] bg-white">
                    <option v-for="member in selectedGroupChat.members.filter((m) => m.isAi)" :key="`admin_transfer_${member.id}`" :value="member.id">
                      {{ member.name }}
                    </option>
                  </select>
                  <button class="px-2 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100" @click="transferSelectedGroupAdmin">
                    {{ tr('转让管理员', 'Transfer Admin') }}
                  </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-[120px,1fr,auto] gap-1.5 items-start">
                  <div class="text-[11px] text-slate-500 pt-1">{{ tr('群公告', 'Announcement') }}</div>
                  <input
                    v-model="groupAnnouncementDraftByRoomId[selectedGroupChat.id]"
                    class="border border-slate-200 rounded px-2 py-1 text-[11px]"
                    :placeholder="tr('公告会在群内置顶展示', 'Announcement pinned in group')"
                  >
                  <button class="px-2 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100" @click="saveSelectedGroupAnnouncement">
                    {{ tr('保存公告', 'Save Announcement') }}
                  </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-[120px,1fr,auto] gap-1.5 items-start">
                  <div class="text-[11px] text-slate-500 pt-1">{{ tr('群规则', 'Group Rules') }}</div>
                  <textarea
                    v-model="groupRulesDraftByRoomId[selectedGroupChat.id]"
                    class="border border-slate-200 rounded px-2 py-1 text-[11px] min-h-[70px]"
                    :placeholder="tr('每行一条规则，AI 管理员会按规则提醒', 'One rule per line')"
                  ></textarea>
                  <button class="px-2 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100 self-start" @click="saveSelectedGroupRules">
                    {{ tr('保存群规', 'Save Rules') }}
                  </button>
                </div>

                <div v-if="selectedGroupChat.announcement || selectedGroupChat.rules" class="rounded border border-emerald-100 bg-emerald-50 px-2.5 py-2 space-y-1">
                  <p v-if="selectedGroupChat.announcement" class="text-[11px] text-emerald-700 break-words">
                    {{ tr('公告：', 'Announcement: ') }}{{ selectedGroupChat.announcement }}
                  </p>
                  <p v-if="selectedGroupChat.rules" class="text-[11px] text-emerald-700 whitespace-pre-wrap break-words">
                    {{ tr('群规：', 'Rules: ') }}{{ selectedGroupChat.rules }}
                  </p>
                </div>

                <div class="space-y-1">
                  <div class="text-[11px] text-slate-500">{{ tr('成员管理（管理员可踢人）', 'Member Management (admins can remove)') }}</div>
                  <div class="grid grid-cols-1 md:grid-cols-[120px,1fr,auto] gap-1.5 items-center">
                    <div class="text-[11px] text-slate-500">{{ tr('添加成员', 'Add Member') }}</div>
                    <select v-model="groupAddMemberDraftByRoomId[selectedGroupChat.id]" class="border border-slate-200 rounded px-2 py-1 text-[11px] bg-white">
                      <option value="">{{ tr('选择可添加的 AI 角色', 'Select AI role to add') }}</option>
                      <option v-for="persona in selectedGroupChatAddableMembers" :key="`group_add_member_${persona.id}`" :value="persona.id">
                        {{ persona.name }}
                      </option>
                    </select>
                    <button
                      class="px-2 py-1 rounded border border-slate-300 text-[11px] hover:bg-slate-100 disabled:opacity-60"
                      :disabled="!groupAddMemberDraftByRoomId[selectedGroupChat.id]"
                      @click="addMemberToSelectedGroup"
                    >
                      {{ tr('添加成员', 'Add') }}
                    </button>
                  </div>
                  <div v-if="selectedGroupChatAddableMembers.length === 0" class="text-[11px] text-slate-400">{{ tr('当前群已包含全部可用 AI 角色。', 'All available AI roles are already in this group.') }}</div>
                  <div class="flex flex-wrap gap-1.5">
                    <div v-for="member in selectedGroupChat.members" :key="`member_${selectedGroupChat.id}_${member.id}`" class="inline-flex items-center gap-1 rounded border border-slate-200 bg-white px-2 py-1 text-[11px]">
                      <span class="truncate max-w-[90px]">{{ member.name }}</span>
                      <span v-if="member.isAdmin" class="text-emerald-600">{{ tr('管理员', 'Admin') }}</span>
                      <button
                        v-if="member.id !== 'user'"
                        class="text-rose-500 hover:text-rose-700"
                        :title="tr('移出群聊', 'Remove from group')"
                        @click="kickMemberFromSelectedGroup(member.id)"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-slate-200 bg-[#fafafa] p-3 space-y-2 min-h-[240px]">
                <div v-for="msg in selectedGroupChat.messages" :key="msg.id" class="text-xs">
                  <div v-if="msg.type === 'system'" class="text-slate-500 text-center py-1">{{ msg.content }}</div>
                  <div v-else class="rounded border border-slate-200 bg-white p-2">
                    <div class="flex items-center justify-between gap-2 mb-1">
                      <div class="flex items-center gap-1.5 min-w-0">
                        <img :src="msg.senderAvatar" :alt="msg.senderName" class="w-5 h-5 rounded object-cover border border-slate-200 shrink-0">
                        <span class="font-semibold text-slate-700 truncate">{{ msg.senderName }}</span>
                      </div>
                      <span class="text-[10px] text-slate-400 shrink-0">{{ formatMomentTime(msg.createdAt) }}</span>
                    </div>

                    <div v-if="msg.type === 'image'" class="space-y-1">
                      <img v-if="msg.mediaUrl" :src="msg.mediaUrl" :alt="msg.content || tr('群聊图片', 'Group image')" class="max-h-52 rounded border border-slate-200 object-cover">
                      <div v-else class="text-[11px] text-slate-500">{{ tr('图片资源已过期或不可用。', 'Image expired or unavailable.') }}</div>
                      <div class="text-slate-700 whitespace-pre-wrap break-words">{{ msg.content }}</div>
                    </div>
                    <div v-else-if="msg.type === 'video'" class="space-y-1">
                      <video v-if="msg.mediaUrl" :src="msg.mediaUrl" controls class="w-full max-h-64 rounded border border-slate-200 bg-black/90"></video>
                      <div v-else class="text-[11px] text-slate-500">{{ tr('视频资源已过期或不可用。', 'Video expired or unavailable.') }}</div>
                      <div class="text-slate-700 whitespace-pre-wrap break-words">{{ msg.content }}</div>
                    </div>
                    <div v-else-if="msg.type === 'audio'" class="space-y-1">
                      <audio :src="msg.mediaUrl" controls class="w-full"></audio>
                      <div v-if="msg.content" class="text-slate-700 whitespace-pre-wrap break-words">{{ msg.content }}</div>
                    </div>
                    <div v-else-if="msg.type === 'emoji'" class="text-xl">{{ msg.content }}</div>
                    <div v-else class="text-slate-700 whitespace-pre-wrap break-words">{{ msg.content }}</div>
                  </div>
                </div>

                <div v-if="selectedGroupChat.messages.length === 0" class="text-xs text-slate-400 text-center py-6">{{ tr('暂无群消息，发送第一条吧。', 'No group messages yet. Send the first one.') }}</div>
              </div>

              <div
                v-if="groupImageConsentPending && groupImageConsentPending.groupId === selectedGroupChat.id"
                class="rounded-lg border border-amber-200 bg-amber-50 p-3 space-y-2"
              >
                <div class="text-xs text-amber-800">
                  {{ groupImageConsentPending.speakerName }} {{ tr('想发送一张 AI 图片，是否同意？', 'wants to send an AI image. Approve?') }}
                </div>
                <div class="text-[11px] text-amber-700 break-words">{{ groupImageConsentPending.prompt }}</div>
                <div class="flex gap-2">
                  <button
                    class="px-2.5 py-1 rounded bg-amber-600 text-white text-xs hover:bg-amber-700 disabled:opacity-60"
                    :disabled="isGroupGeneratingImage"
                    @click="approveGroupImageRequest"
                  >
                    {{ isGroupGeneratingImage ? tr('生成中...', 'Generating...') : tr('同意并生成', 'Approve & Generate') }}
                  </button>
                  <button
                    class="px-2.5 py-1 rounded border border-amber-300 text-amber-700 text-xs hover:bg-amber-100"
                    @click="rejectGroupImageRequest"
                  >
                    {{ tr('拒绝发送', 'Reject') }}
                  </button>
                </div>
              </div>

              <div class="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
                <input ref="groupMediaInputRef" type="file" class="hidden" accept="image/*,video/*" @change="handleGroupMediaUpload">
                <div class="flex flex-wrap items-center gap-2">
                  <input
                    v-model="groupChatMessageDraft"
                    class="flex-1 min-w-[160px] border border-slate-200 rounded px-3 py-2 text-xs"
                    :placeholder="tr('输入群消息，支持触发 AI 互动', 'Type group message, supports AI interaction')"
                    @keydown.enter.prevent="sendGroupChatMessage"
                  >
                  <button class="px-3 py-2 rounded bg-[#07c160] text-white text-xs hover:bg-[#06ad56] disabled:opacity-60" :disabled="!groupChatMessageDraft.trim()" @click="sendGroupChatMessage">
                    {{ tr('发送', 'Send') }}
                  </button>
                  <button class="px-2.5 py-2 rounded border border-slate-200 text-xs hover:bg-slate-50" @click="openGroupMediaPicker('image')">{{ tr('图片', 'Image') }}</button>
                  <button class="px-2.5 py-2 rounded border border-slate-200 text-xs hover:bg-slate-50" @click="openGroupMediaPicker('video')">{{ tr('视频', 'Video') }}</button>
                  <button class="px-2.5 py-2 rounded border border-slate-200 text-xs hover:bg-slate-50" @click="showGroupEmojiPanel = !showGroupEmojiPanel">
                    {{ showGroupEmojiPanel ? tr('收起表情', 'Hide Emoji') : tr('表情面板', 'Emoji Panel') }}
                  </button>
                  <button class="px-2.5 py-2 rounded border border-slate-200 text-xs hover:bg-slate-50" @click="sendGroupEmoji('😀')">😀</button>
                  <button class="px-2.5 py-2 rounded border border-slate-200 text-xs hover:bg-slate-50" @click="sendGroupEmoji('🎉')">🎉</button>
                </div>
                <div v-if="showGroupEmojiPanel" class="rounded border border-slate-200 bg-slate-50 p-2 space-y-2">
                  <div class="flex flex-wrap gap-1.5">
                    <button
                      v-for="category in groupEmojiCategories"
                      :key="`group_emoji_category_${category}`"
                      class="px-2 py-1 rounded text-[11px] border"
                      :class="selectedGroupEmojiCategory === category ? 'border-[#07c160] bg-emerald-50 text-emerald-700' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-100'"
                      @click="selectedGroupEmojiCategory = category"
                    >
                      {{ getGroupEmojiCategoryLabel(category) }}
                    </button>
                  </div>
                  <div class="grid grid-cols-8 sm:grid-cols-12 gap-1">
                    <button
                      v-for="emoji in activeGroupEmojiList"
                      :key="`group_emoji_${selectedGroupEmojiCategory}_${emoji}`"
                      class="px-1.5 py-1 rounded border border-slate-200 bg-white hover:bg-slate-100 text-lg leading-none"
                      @click="sendGroupEmoji(emoji)"
                    >
                      {{ emoji }}
                    </button>
                  </div>
                </div>
                <p v-if="groupChatInfo" class="text-[11px] text-emerald-700">{{ groupChatInfo }}</p>
                <p v-if="groupChatError" class="text-[11px] text-rose-600">{{ groupChatError }}</p>
              </div>
            </template>

            <div v-else class="rounded-lg border border-dashed border-slate-300 bg-slate-50 text-sm text-slate-500 p-6 text-center">
              {{ tr('请选择一个群聊，或先在左侧创建群聊。', 'Select a group chat, or create one on the left first.') }}
            </div>
          </section>
        </div>
      </div>
    </div>

    <!-- Settings Modal (Kept functionality but minimal style) -->
    <div v-if="showSettings" class="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
       <div class="bg-white rounded-lg shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
          <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-[#f5f5f5]">
             <h3 class="font-medium text-slate-800">{{ tr('设置', 'Settings') }}</h3>
             <button @click="showSettings = false" class="text-slate-400 hover:text-slate-600"><X class="w-5 h-5" /></button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
             <!-- API Settings Only for Simplicity -->
             <div class="space-y-4">
               <h4 class="text-xs font-bold text-slate-400 uppercase">{{ tr('API 连接', 'API Connection') }}</h4>
               <div class="space-y-2 rounded border border-slate-200 bg-slate-50 p-3">
                 <div class="text-xs font-semibold text-slate-700">{{ tr('文本接口（原接口）', 'Text API') }}</div>
                 <p class="text-[11px] leading-relaxed text-slate-500">
                   {{ tr('用途：文本聊天、剧情生成与语音台词生成。不会用于 AI 生图。', 'Usage: text chat, story generation, and voice script generation. Not used for image generation.') }}
                 </p>
                 <input v-model="tempSettings.baseUrl" type="text" placeholder="Text/Voice Base URL" class="w-full border rounded px-3 py-2 text-sm">
                 <input v-model="tempSettings.apiKey" type="password" placeholder="Text/Voice API Key" class="w-full border rounded px-3 py-2 text-sm">
                 <input v-model="tempSettings.modelName" type="text" placeholder="Text/Voice Model" class="w-full border rounded px-3 py-2 text-sm">
               </div>
               <div class="space-y-2 rounded border border-sky-200 bg-sky-50/60 p-3">
                 <div class="text-xs font-semibold text-sky-700">{{ tr('TTS 语音引擎（补充）', 'TTS Engine (Supplement)') }}</div>
                 <p class="text-[11px] leading-relaxed text-sky-700/80">
                   {{ tr('用途：语音合成可选 OpenAI 兼容 /audio/speech 或 Coqui TTS，本项仅影响“生成语音”。', 'Usage: voice synthesis can use OpenAI-compatible /audio/speech or Coqui TTS. This only affects voice generation.') }}
                 </p>
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-sky-800">{{ tr('语音引擎', 'Voice Engine') }}</label>
                   <select v-model="tempSettings.ttsProvider" class="w-full border rounded px-3 py-2 text-sm bg-white">
                     <option value="openai_compatible">{{ tr('OpenAI兼容（/audio/speech）', 'OpenAI-Compatible (/audio/speech)') }}</option>
                     <option value="coqui">{{ tr('Coqui TTS（本地/自建）', 'Coqui TTS (Local/Self-hosted)') }}</option>
                   </select>
                 </div>
                 <template v-if="tempSettings.ttsProvider === 'coqui'">
                   <input v-model="tempSettings.coquiBaseUrl" type="text" placeholder="/api/tts/coqui/synthesize/" class="w-full border rounded px-3 py-2 text-sm bg-white">
                   <input v-model="tempSettings.coquiModelName" type="text" placeholder="tts_models/multilingual/multi-dataset/xtts_v2" class="w-full border rounded px-3 py-2 text-sm bg-white">
                   <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                     <input v-model="tempSettings.coquiLanguage" type="text" placeholder="zh-cn" class="w-full border rounded px-3 py-2 text-sm bg-white">
                     <input v-model="tempSettings.coquiSpeaker" type="text" :placeholder="tr('可选：speaker 名称', 'Optional: speaker name')" class="w-full border rounded px-3 py-2 text-sm bg-white">
                   </div>
                   <p class="text-[11px] leading-relaxed text-sky-700/80">
                     {{ tr('提示：如用 XTTS 模型，建议在后端传入参考音频可获得更稳定音色。', 'Tip: for XTTS models, passing a reference speaker wav on backend gives more stable timbre.') }}
                   </p>
                 </template>
               </div>
               <div class="space-y-2 rounded border border-emerald-200 bg-emerald-50/60 p-3">
                 <div class="text-xs font-semibold text-emerald-700">{{ tr('AI 生图接口（新增）', 'AI Image API') }}</div>
                 <p class="text-[11px] leading-relaxed text-emerald-700/80">
                   {{ tr('用途：全站 AI 生图（角色头像、群聊配图、媒体面板图片、小说封面/角色/章节配图）。', 'Usage: AI image generation across the site.') }}
                 </p>
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-emerald-800">{{ tr('接口类型', 'API Type') }}</label>
                   <select v-model="tempSettings.imageApiType" class="w-full border rounded px-3 py-2 text-sm bg-white">
                     <option value="gemini_native">{{ tr('谷歌原生接口（Gemini）', 'Google Native (Gemini)') }}</option>
                     <option value="openai_compatible">{{ tr('OpenAI兼容接口（/images）', 'OpenAI-Compatible (/images)') }}</option>
                   </select>
                 </div>
                 <p class="text-[11px] leading-relaxed text-emerald-700/80">
                   {{
                     tempSettings.imageApiType === 'gemini_native'
                       ? tr('谷歌原生：将调用 Gemini v1beta `models/*:generateContent` 接口。', 'Google native: will call Gemini v1beta `models/*:generateContent`.')
                       : tr('OpenAI兼容：将调用 `/images/generations`（有参考图时调用 `/images/edits`）。', 'OpenAI-compatible: will call `/images/generations` (uses `/images/edits` when reference image is provided).')
                   }}
                 </p>
                 <input v-model="tempSettings.imageBaseUrl" type="text" placeholder="Image Base URL" class="w-full border rounded px-3 py-2 text-sm bg-white">
                 <input v-model="tempSettings.imageApiKey" type="password" placeholder="Image API Key" class="w-full border rounded px-3 py-2 text-sm bg-white">
                 <input v-model="tempSettings.imageModelName" type="text" placeholder="Image Model" class="w-full border rounded px-3 py-2 text-sm bg-white">
               </div>
               <div class="flex flex-wrap items-center gap-3">
                 <button
                 @click="testConnection"
                 :disabled="isTesting"
                 class="text-sm text-blue-600 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ isTesting ? tr('测试中...', 'Testing...') : tr('测试文本连接', 'Test Text API') }}
                 </button>
                 <button
                 @click="testImageConnection"
                 :disabled="isTestingImage"
                 class="text-sm text-emerald-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ isTestingImage ? tr('测试中...', 'Testing...') : tr('测试生图连接', 'Test Image API') }}
                </button>
              </div>
               <div v-if="testStatus.message" class="text-xs" :class="testStatus.success ? 'text-green-600' : 'text-red-600'">{{ testStatus.message }}</div>
               <div v-if="imageTestStatus.message" class="text-xs" :class="imageTestStatus.success ? 'text-emerald-700' : 'text-red-600'">{{ imageTestStatus.message }}</div>
             </div>
             <div class="space-y-3">
               <h4 class="text-xs font-bold text-slate-400 uppercase">{{ tr('语音聊天工具箱', 'Voice Toolbox') }}</h4>
               <div class="space-y-2 rounded border border-slate-200 bg-slate-50 p-3">
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-slate-600">{{ tr('选声模式', 'Voice Mode') }}</label>
                   <select v-model="tempVoiceToolboxSettings.mode" class="w-full border border-slate-200 rounded px-2 py-1 text-xs bg-white">
                     <option v-for="mode in voiceToolboxModeOptions" :key="`voice_mode_${mode.value}`" :value="mode.value">
                       {{ mode.label }}
                     </option>
                   </select>
                 </div>
                 <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600">
                   <label class="inline-flex items-center gap-1.5">
                     <input v-model="tempVoiceToolboxSettings.usePersonalitySignals" type="checkbox">
                     <span>{{ tr('启用性格特征选声', 'Use personality signals') }}</span>
                   </label>
                   <label class="inline-flex items-center gap-1.5">
                     <input v-model="tempVoiceToolboxSettings.useAvatarSignals" type="checkbox">
                     <span>{{ tr('启用头像特征选声', 'Use avatar signals') }}</span>
                   </label>
                   <label class="inline-flex items-center gap-1.5">
                     <input v-model="tempVoiceToolboxSettings.keepPreferredVoiceFirst" type="checkbox">
                     <span>{{ tr('保留“语音音色”偏好', 'Keep voice preference first') }}</span>
                   </label>
                   <div class="text-[11px] text-slate-500 leading-relaxed">
                     {{ tr('严格自动：优先防串音；平衡自动：允许风格化混合；手动优先：优先使用你手动选的音色。', 'Auto strict: avoid voice mismatch first; auto balanced: allow style mix; manual preferred: prefer your selected voice.') }}
                   </div>
                 </div>
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-slate-600">{{ tr('女角色主音色', 'Female Main Voice') }}</label>
                   <select v-model="tempVoiceToolboxSettings.femalePreferredVoice" class="w-full border border-slate-200 rounded px-2 py-1 text-xs bg-white">
                     <option v-for="voice in femaleVoiceOptionsForToolbox" :key="`female_voice_${voice.value}`" :value="voice.value">
                       {{ voice.label }}
                     </option>
                   </select>
                 </div>
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-slate-600">{{ tr('男角色主音色', 'Male Main Voice') }}</label>
                   <select v-model="tempVoiceToolboxSettings.malePreferredVoice" class="w-full border border-slate-200 rounded px-2 py-1 text-xs bg-white">
                     <option v-for="voice in maleVoiceOptionsForToolbox" :key="`male_voice_${voice.value}`" :value="voice.value">
                       {{ voice.label }}
                     </option>
                   </select>
                 </div>
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-slate-600">{{ tr('中性主音色', 'Neutral Main Voice') }}</label>
                   <select v-model="tempVoiceToolboxSettings.neutralPreferredVoice" class="w-full border border-slate-200 rounded px-2 py-1 text-xs bg-white">
                     <option v-for="voice in neutralVoiceOptionsForToolbox" :key="`neutral_voice_${voice.value}`" :value="voice.value">
                       {{ voice.label }}
                     </option>
                   </select>
                 </div>
                 <div class="grid grid-cols-1 sm:grid-cols-[110px,1fr] items-center gap-2">
                   <label class="text-xs text-slate-600">{{ tr('兜底音色', 'Fallback Voice') }}</label>
                   <select v-model="tempVoiceToolboxSettings.fallbackVoice" class="w-full border border-slate-200 rounded px-2 py-1 text-xs bg-white">
                     <option v-for="voice in MEDIA_VOICE_OPTIONS" :key="`fallback_voice_${voice.value}`" :value="voice.value">
                       {{ voice.label }}
                     </option>
                   </select>
                 </div>
                 <div class="text-[11px] text-emerald-700">
                   {{ tr('当前角色推荐音色：', 'Current recommended voice: ') }}{{ getVoiceLabel(resolvePrimaryVoiceForPersona(currentPersona, tempVoiceToolboxSettings)) }}
                 </div>
               </div>
             </div>
             <div class="space-y-3">
               <h4 class="text-xs font-bold text-slate-400 uppercase">{{ tr('快捷入口', 'Quick Entry') }}</h4>
               <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                 <button
                   class="rounded border border-indigo-300 bg-indigo-50 px-3 py-2 text-sm text-indigo-700 hover:bg-indigo-100"
                   @click="openNovelStoryPage"
                 >
                   {{ tr('打开小说剧情', 'Open Novel Story') }}
                 </button>
                 <button
                   class="rounded border border-emerald-300 bg-emerald-50 px-3 py-2 text-sm text-emerald-700 hover:bg-emerald-100"
                   @click="openPlazaPage"
                 >
                   {{ tr('打开广场', 'Open Plaza') }}
                 </button>
               </div>
             </div>
          </div>
          <div class="p-4 border-t border-slate-100 flex justify-end gap-2 bg-[#f5f5f5]">
             <button @click="showSettings = false" class="px-4 py-1.5 border rounded text-sm hover:bg-slate-50">{{ tr('取消', 'Cancel') }}</button>
             <button @click="saveSettings" class="px-4 py-1.5 bg-[#07c160] text-white rounded text-sm hover:bg-[#06ad56]">{{ tr('保存', 'Save') }}</button>
          </div>
       </div>
    </div>

    <!-- Game Editor Modal (Minimal) -->
    <div v-if="showGameEditor" class="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
       <div class="bg-white rounded-lg shadow-2xl w-full max-w-lg flex flex-col">
          <div class="p-4 border-b bg-[#f5f5f5] flex justify-between">
             <h3 class="font-medium">{{ tr('编辑游戏', 'Edit Game') }}</h3>
             <button @click="showGameEditor = false"><X class="w-5 h-5" /></button>
          </div>
          <div class="p-6 space-y-4">
             <input v-model="tempGame.name" class="w-full border rounded px-3 py-2 text-sm" :placeholder="tr('名称', 'Name')">
             <input v-model="tempGame.themeColor" type="color" class="w-full h-8">
             <textarea v-model="tempGameQuests" class="w-full border rounded px-3 py-2 text-sm h-32" :placeholder="tr('JSON 任务', 'Quest JSON')"></textarea>
          </div>
          <div class="p-4 border-t bg-[#f5f5f5] flex justify-end gap-2">
             <button @click="saveGame" class="px-4 py-1.5 bg-[#07c160] text-white rounded text-sm">{{ tr('保存', 'Save') }}</button>
          </div>
       </div>
    </div>

    <!-- Character Details Modal -->
    <div v-if="showCharacterModal && characterModalData" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
       <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-200">
          
          <!-- Header Image -->
          <div class="relative h-48 sm:h-64 shrink-0 bg-slate-100">
             <img :src="characterModalData.avatar" class="w-full h-full object-cover" />
             <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-6">
                <div>
                  <h2 class="text-3xl font-bold text-white shadow-sm mb-1">{{ characterModalData.name }}</h2>
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 bg-[#07c160] text-white text-xs font-bold rounded">{{ tr('角色档案', 'Role Card') }}</span>
                  </div>
                </div>
             </div>
             <button @click="showCharacterModal = false" class="absolute top-4 right-4 p-2 bg-black/20 hover:bg-black/40 text-white rounded-full transition-colors backdrop-blur-md">
               <X class="w-5 h-5" />
             </button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto p-6 custom-scrollbar">
             <div class="space-y-6">
               
               <!-- Description -->
               <section>
                 <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                   <User class="w-4 h-4" /> {{ tr('角色简介', 'Role Description') }}
                 </h3>
                 <div
                   class="prose prose-sm max-w-none text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100"
                   v-html="renderMarkdown(characterModalData.description || '')"
                 ></div>
                 <div
                   v-if="!String(characterModalData.description || '').trim()"
                   class="text-sm text-slate-500 bg-slate-50 p-4 rounded-lg border border-slate-100"
                 >
                   {{ tr('暂无角色简介', 'No role description yet') }}
                 </div>
               </section>

               <!-- System Prompt (Optional) -->
               <section v-if="characterModalData.systemPrompt">
                 <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                   <Cpu class="w-4 h-4" /> {{ tr('设定详情 (System Prompt)', 'Setup Details (System Prompt)') }}
                 </h3>
                 <div
                   class="prose prose-sm max-w-none text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100 max-h-60 overflow-y-auto custom-scrollbar"
                   v-html="renderMarkdown(characterModalData.systemPrompt || '')"
                 ></div>
                 <div
                   v-if="!String(characterModalData.systemPrompt || '').trim()"
                   class="text-xs text-slate-500 bg-slate-50 p-4 rounded-lg border border-slate-100"
                 >
                   {{ tr('暂无设定详情', 'No setup details yet') }}
                 </div>
               </section>

             </div>
          </div>
          
          <!-- Footer -->
          <div class="p-4 border-t border-slate-100 bg-[#f9f9f9] flex justify-end">
             <button @click="showCharacterModal = false" class="px-5 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium rounded-lg transition-colors text-sm">
               {{ tr('关闭', 'Close') }}
             </button>
          </div>
       </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, computed, reactive } from 'vue'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { 
  Settings, Send, User, Plus, Search, 
  MessageSquare, Trash2, X, 
  CheckCircle2, AlertCircle, Sparkles, Cpu, 
  Swords, Gamepad2, ChevronDown, RefreshCw, Volume2, Image, Video, Braces, Menu, Download, Upload, Heart
} from 'lucide-vue-next'
import {
  guardUsagePolicyContent,
  isUsagePolicyViolationError,
  openUsagePolicyDialog,
} from '../utils/usagePolicy'

const { locale } = useI18n()
const isChineseLocale = computed(() => String(locale.value || '').toLowerCase().startsWith('zh'))
const tr = (zh: string, en: string): string => (isChineseLocale.value ? zh : en)
const HAN_CHAR_REGEX = /\p{Script=Han}/u
const PERSONA_GROUP_BASE = '基础好友'
const PERSONA_GROUP_CHARACTER = '角色好友'
const PERSONA_GROUP_NOVEL = '游戏小说好友'
const PERSONA_GROUP_CUSTOM = '自定义角色'
const PERSONA_GROUP_OTHER = '其他'

const defaultCustomPersonaGroup = () => tr(PERSONA_GROUP_CUSTOM, 'Custom Roles')
const defaultUserName = () => tr('用户', 'User')
const unknownLocationStatusLabel = () => tr('未知地点', 'Unknown location')
const containsHanChars = (value: string) => HAN_CHAR_REGEX.test(String(value || ''))

const getPersonaGroupLabel = (groupName: string) => {
  const normalized = String(groupName || '').trim()
  if (normalized === PERSONA_GROUP_BASE) return tr(PERSONA_GROUP_BASE, 'Core Friends')
  if (normalized === PERSONA_GROUP_CHARACTER) return tr(PERSONA_GROUP_CHARACTER, 'Character Friends')
  if (normalized === PERSONA_GROUP_NOVEL) return tr(PERSONA_GROUP_NOVEL, 'Game Novel Friends')
  if (normalized === PERSONA_GROUP_CUSTOM) return tr(PERSONA_GROUP_CUSTOM, 'Custom Roles')
  if (normalized === PERSONA_GROUP_OTHER) return tr(PERSONA_GROUP_OTHER, 'Others')
  return normalized || tr(PERSONA_GROUP_OTHER, 'Others')
}

// --- Types ---
interface Quest {
  title: string
  reward: string
  link: string
}

interface QuestData {
  quest: string
  type?: string
  description?: string
  reward?: string
  link?: string
  linkText?: string
}

interface CharacterCardData {
  name: string
  description: string
  avatar: string
  // Full detail
  systemPrompt?: string
}

interface MediaAttachment {
  type: MediaType
  src: string
  name?: string
  mimeType?: string
  sizeLabel?: string
  origin?: 'ai_generated' | 'user_upload'
}

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  isTyping?: boolean
  expanded?: boolean
  questData?: QuestData
  cardData?: CharacterCardData
  mediaData?: MediaAttachment
}

interface MomentComment {
  id: string
  authorId: string
  authorName: string
  authorAvatar: string
  content: string
  createdAt: number
}

interface MomentPost {
  id: string
  authorId: string
  authorName: string
  authorAvatar: string
  content: string
  createdAt: number
  likedByUser: boolean
  likedByPersonaIds: string[]
  comments: MomentComment[]
}

interface MomentsTrendContext {
  dateKey: string
  dateLabel: string
  holidayLabels: string[]
  hotTopics: string[]
  personaAngles: string[]
  source: 'local' | 'ai' | 'mixed'
  updatedAt: number
}

type GroupReplyMode = 'cold' | 'normal' | 'warm' | 'frenzy'
type GroupChatMessageType = 'text' | 'emoji' | 'audio' | 'image' | 'video' | 'system'

interface GroupChatMember {
  id: string
  name: string
  avatar: string
  isAi: boolean
  isAdmin: boolean
}

interface GroupChatMessage {
  id: string
  senderId: string
  senderName: string
  senderAvatar: string
  type: GroupChatMessageType
  content: string
  mediaUrl?: string
  createdAt: number
}

interface GroupChatRoom {
  id: string
  name: string
  avatar: string
  members: GroupChatMember[]
  messages: GroupChatMessage[]
  replyMode: GroupReplyMode
  announcement: string
  rules: string
  mutedByUser: boolean
  dissolved: boolean
  createdAt: number
  updatedAt: number
}

interface GroupImageConsentRequest {
  id: string
  groupId: string
  speakerId: string
  speakerName: string
  prompt: string
  createdAt: number
}

interface GroupReplyModeProfile {
  minSpeakers: number
  maxSpeakers: number
  emojiChance: number
  imageRequestChance: number
  audioChance: number
  followUpChance: number
  maxFollowUps: number
  leaveChance: number
  adminActionChance: number
  adminActionCount: number
  autoKickChance: number
}

type ImageApiType = 'gemini_native' | 'openai_compatible'
type TtsProvider = 'openai_compatible' | 'coqui'

interface ApiSettings {
  baseUrl: string
  apiKey: string
  modelName: string
  imageBaseUrl: string
  imageApiKey: string
  imageModelName: string
  imageApiType: ImageApiType
  ttsProvider: TtsProvider
  coquiBaseUrl: string
  coquiModelName: string
  coquiLanguage: string
  coquiSpeaker: string
}

interface ResolvedApiConfig {
  baseUrl: string
  apiKey: string
  modelName: string
}

interface ResolvedImageApiConfig extends ResolvedApiConfig {
  imageApiType: ImageApiType
}

interface ResolvedTtsConfig {
  ttsProvider: TtsProvider
  coquiBaseUrl: string
  coquiModelName: string
  coquiLanguage: string
  coquiSpeaker: string
}

type VoiceToolboxMode = 'auto_strict' | 'auto_balanced' | 'manual_preferred'

interface VoiceToolboxSettings {
  mode: VoiceToolboxMode
  usePersonalitySignals: boolean
  useAvatarSignals: boolean
  keepPreferredVoiceFirst: boolean
  fallbackVoice: string
  femalePreferredVoice: string
  malePreferredVoice: string
  neutralPreferredVoice: string
}

interface Persona {
  id: string
  name: string
  avatar: string
  description: string
  systemPrompt: string
  gender?: string
  personality?: string
  group?: string
  firstMessage?: string
  file?: string
  source?: 'imported' | 'custom' | 'default'
}

interface PersonaCreateForm {
  name: string
  nickname: string
  age: string
  gender: string
  title: string
  description: string
  personality: string
  background: string
  firstMessage: string
  systemPrompt: string
  group: string
  avatarPreview: string
  avatarUrl: string
}

interface UserProfileForm {
  name: string
  gender: string
  personality: string
  traits: string
  chatStyle: string
  avatarPreview: string
  avatarUrl: string
  avatarPrompt: string
}

interface PersonaCardImportData {
  name: string
  description: string
  systemPrompt: string
  firstMessage: string
  group: string
  avatar: string
}

type PersonaAutoFillField =
  | 'name'
  | 'nickname'
  | 'age'
  | 'gender'
  | 'title'
  | 'description'
  | 'personality'
  | 'background'
  | 'firstMessage'
  | 'systemPrompt'
  | 'group'

type MediaType = 'image' | 'video' | 'audio'

interface GameConfig {
  id: string
  name: string
  themeColor: string
  accentColor?: string
  bgGradient?: string
  bgImage?: string
  questIcon?: string
  npcRole?: string
  systemPrompt?: string
  quests: Quest[]
  terminology: Record<string, string>
}

interface VisualConfig {
  themeMode: 'light' | 'glass' | 'dark'
  bgStyle: 'solid' | 'gradient' | 'animated' | 'custom'
  bubbleStyle: 'solid' | 'gradient' | 'glass'
  enableAnimations: boolean
  glassOpacity: number // 0.1 to 1.0
}

interface Script {
  id: string
  name: string
  version: string
  enabled: boolean
  code: string
  description?: string
  error?: string
}

interface ThemeItem {
  id: string
  name: string
  file: string
}

// --- Constants ---
const DEFAULT_PERSONAS: Persona[] = [
  {
    id: 'erin',
    name: 'Erin',
    avatar: 'https://api.dicebear.com/7.x/notionists/svg?seed=Erin&backgroundColor=e0e7ff',
    description: 'Silver-haired assistant with calm and professional tone.',
    systemPrompt: `You are Erin, a high-quality anime style game assistant.`,
    group: PERSONA_GROUP_BASE,
    source: 'default'
  }
]

const DEFAULT_GAMES: GameConfig[] = [
  {
    id: 'genshin_01',
    name: 'Genshin Impact',
    themeColor: '#0EA5E9',
    accentColor: '#E0F2FE',
    bgGradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
    questIcon: '!',
    npcRole: 'Guild receptionist',
    systemPrompt: 'You are a guild receptionist who gives useful quest guidance.',
    quests: [
      { title: 'Abyss Floor Guide', reward: '100 points', link: 'https://www.google.com/search?q=genshin+abyss+guide' }
    ],
    terminology: { stamina: 'Resin', coins: 'Mora' }
  }
]

const CUSTOM_PERSONAS_STORAGE_KEY = 'cypher_tavern_custom_personas'
const CUSTOM_PERSONAS_STORAGE_KEY_V2 = 'cypher_tavern_custom_personas_v2'
const BROKEN_IMPORTED_PERSONAS_STORAGE_KEY = 'cypher_tavern_broken_imported_persona_ids_v1'
const SETTINGS_STORAGE_KEY = 'cypher_tavern_settings'
const SETTINGS_STORAGE_KEY_V2 = 'cypher_tavern_settings_v2'
const VOICE_TOOLBOX_STORAGE_KEY = 'cypher_tavern_voice_toolbox_v1'
const SELECTED_PERSONA_STORAGE_KEY = 'cypher_tavern_selected_persona_id'
const SELECTED_PERSONA_STORAGE_KEY_V2 = 'cypher_tavern_selected_persona_id_v2'
const USER_PROFILE_STORAGE_KEY = 'cypher_tavern_user_profile_v1'
const MOMENTS_STORAGE_KEY = 'cypher_tavern_moments_v1'
const GROUP_CHAT_STORAGE_KEY = 'cypher_tavern_group_chats_v1'
const MOMENTS_TREND_CONTEXT_STORAGE_KEY = 'cypher_tavern_moments_trend_context_v1'
const MOMENTS_TREND_REFRESH_INTERVAL_MS = 2 * 60 * 60 * 1000
const PERSONA_LOCATION_STATUS_STORAGE_KEY = 'cypher_tavern_persona_location_status_v1'
const GROUP_REPLY_MODE_OPTIONS = [
  { value: 'cold', label: '冷漠', description: '少量回复、偏文字' },
  { value: 'normal', label: '正常', description: '均衡互动、稳定回复' },
  { value: 'warm', label: '热情', description: '更多角色参与、媒体更多' },
  { value: 'frenzy', label: '狂热', description: '高频连聊、强互动' },
] as const
const GROUP_REPLY_MODE_PROFILES: Record<GroupReplyMode, GroupReplyModeProfile> = {
  cold: {
    minSpeakers: 1,
    maxSpeakers: 1,
    emojiChance: 0.06,
    imageRequestChance: 0.03,
    audioChance: 0.1,
    followUpChance: 0.04,
    maxFollowUps: 0,
    leaveChance: 0.02,
    adminActionChance: 0.08,
    adminActionCount: 1,
    autoKickChance: 0.04,
  },
  normal: {
    minSpeakers: 1,
    maxSpeakers: 2,
    emojiChance: 0.12,
    imageRequestChance: 0.08,
    audioChance: 0.24,
    followUpChance: 0.16,
    maxFollowUps: 1,
    leaveChance: 0.015,
    adminActionChance: 0.12,
    adminActionCount: 1,
    autoKickChance: 0.06,
  },
  warm: {
    minSpeakers: 2,
    maxSpeakers: 3,
    emojiChance: 0.2,
    imageRequestChance: 0.12,
    audioChance: 0.32,
    followUpChance: 0.28,
    maxFollowUps: 1,
    leaveChance: 0.01,
    adminActionChance: 0.2,
    adminActionCount: 2,
    autoKickChance: 0.12,
  },
  frenzy: {
    minSpeakers: 2,
    maxSpeakers: 4,
    emojiChance: 0.3,
    imageRequestChance: 0.17,
    audioChance: 0.4,
    followUpChance: 0.42,
    maxFollowUps: 2,
    leaveChance: 0,
    adminActionChance: 0.32,
    adminActionCount: 2,
    autoKickChance: 0.2,
  },
}
const GROUP_EMOJI_CATEGORIES = ['常用', '情绪', '互动', '游戏', '庆祝'] as const
type GroupEmojiCategory = (typeof GROUP_EMOJI_CATEGORIES)[number]
const GROUP_EMOJI_LIBRARY: Record<GroupEmojiCategory, string[]> = {
  常用: ['😀', '😄', '😊', '😉', '🙂', '😍', '🥰', '😎', '🤔', '😴', '😭', '😡', '🥹', '🙌', '👍', '👀'],
  情绪: ['😆', '😂', '🤣', '😌', '😇', '😏', '😮', '😳', '🥺', '😤', '🤯', '🥲', '🫠', '🤭', '😬', '😮‍💨'],
  互动: ['👏', '🤝', '🙏', '🫶', '🤗', '💬', '📣', '✅', '❓', '💡', '🧠', '📝', '🎤', '📸', '🎧', '💭'],
  游戏: ['🎮', '🕹️', '⚔️', '🛡️', '🏆', '🎯', '🎲', '🧩', '🚀', '🔥', '💥', '✨', '🗺️', '📦', '🪙', '🧪'],
  庆祝: ['🎉', '🎊', '🥳', '🍻', '🎂', '🌟', '💐', '🎁', '💖', '💯', '🧨', '🌈', '🏅', '🍀', '🌸', '🫡'],
}
const getGroupEmojiCategoryLabel = (category: GroupEmojiCategory) => {
  if (category === '常用') return tr('常用', 'Common')
  if (category === '情绪') return tr('情绪', 'Emotion')
  if (category === '互动') return tr('互动', 'Interaction')
  if (category === '游戏') return tr('游戏', 'Game')
  if (category === '庆祝') return tr('庆祝', 'Celebrate')
  return category
}
const MESSAGE_COLLAPSE_THRESHOLD = 900
const NETWORK_STATUS_OPTIONS = ['4G', '5G', 'WiFi'] as const
const LOCAL_PERSONA_LOCATION_POOL = isChineseLocale.value
  ? [
      '北京·三里屯',
      '上海·静安寺',
      '广州·天河城',
      '深圳·南山科技园',
      '杭州·西湖边',
      '成都·春熙路',
      '重庆·解放碑',
      '武汉·光谷广场',
      '南京·新街口',
      '西安·钟楼',
      '长沙·五一广场',
      '苏州·金鸡湖',
      '天津·和平路',
      '青岛·台东',
      '厦门·中山路',
      '福州·东街口',
      '郑州·二七广场',
      '合肥·政务区',
      '昆明·南屏街',
      '宁波·东部新城',
      '无锡·南长街',
      '沈阳·中街',
      '大连·星海广场',
      '南昌·红谷滩',
      '贵阳·花果园',
      '兰州·东方红广场',
      '太原·柳巷',
      '石家庄·勒泰',
      '南宁·朝阳广场',
      '哈尔滨·中央大街',
    ]
  : [
      'Tokyo·Shibuya',
      'Osaka·Namba',
      'Seoul·Gangnam',
      'Taipei·Ximending',
      'New York·Times Square',
      'Los Angeles·Santa Monica',
      'London·Soho',
      'Paris·Le Marais',
      'Berlin·Mitte',
      'Singapore·Marina Bay',
      'Hong Kong·Central',
      'Bangkok·Siam',
      'Sydney·Darling Harbour',
      'Vancouver·Downtown',
      'Toronto·Queen St',
      'San Francisco·Mission',
    ]
const FALLBACK_LOCATION_CITY_POOL = isChineseLocale.value
  ? ['北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '武汉', '南京', '西安', '长沙', '苏州', '天津', '青岛', '厦门']
  : ['Tokyo', 'Osaka', 'Seoul', 'Taipei', 'New York', 'Los Angeles', 'London', 'Paris', 'Berlin', 'Singapore', 'Bangkok', 'Sydney', 'Toronto', 'Vancouver', 'San Francisco']
const FALLBACK_LOCATION_SCENE_POOL = isChineseLocale.value
  ? ['商务区', '地铁口', '江边步道', '老城区', '大学城', '创意园', '会展中心', '夜市街', 'CBD写字楼', '社区公园']
  : ['Business District', 'Metro Exit', 'Riverside Walk', 'Old Town', 'University Area', 'Creative Park', 'Expo Center', 'Night Market', 'CBD Office', 'Community Park']
const MOMENTS_MAX_CONTENT_LENGTH = 240
const MOMENTS_MAX_POSTS_IN_MEMORY = 220
const MOMENTS_MAX_POSTS_IN_STORAGE = 80
const MOMENTS_MAX_COMMENTS_IN_STORAGE = 16
const GROUP_CHAT_MAX_MESSAGES = 260
const GROUP_CHAT_MAX_MESSAGES_IN_STORAGE = 120
const MOMENTS_TICK_MIN_DELAY_MS = 75 * 1000
const MOMENTS_TICK_MAX_DELAY_MS = 125 * 1000
const USER_AVATAR_URL = 'https://api.dicebear.com/7.x/notionists/svg?seed=User&backgroundColor=e0e7ff'
const HTML_FRAME_SOURCE = 'cypher_tavern_html_frame'
const DEFAULT_HTML_FRAME_HEIGHT = 360
const MIN_HTML_FRAME_HEIGHT = 220
const MAX_HTML_FRAME_HEIGHT = 860
const PERSONA_AUTOFILL_FIELDS: PersonaAutoFillField[] = [
  'name',
  'nickname',
  'age',
  'gender',
  'title',
  'description',
  'personality',
  'background',
  'firstMessage',
  'systemPrompt',
  'group'
]
const PERSONA_FIELD_LABELS: Record<PersonaAutoFillField, string> = {
  name: tr('角色名称', 'Role Name'),
  nickname: tr('昵称', 'Nickname'),
  age: tr('年龄', 'Age'),
  gender: tr('性别', 'Gender'),
  title: tr('头衔', 'Title'),
  description: tr('角色简介', 'Role Description'),
  personality: tr('性格', 'Personality'),
  background: tr('背景', 'Background'),
  firstMessage: tr('首条消息', 'First Message'),
  systemPrompt: tr('系统提示词', 'System Prompt'),
  group: tr('分组', 'Group')
}
const MEDIA_VOICE_OPTIONS = [
  { value: 'alloy', label: tr('Alloy（中性通用）', 'Alloy (neutral all-round)') },
  { value: 'ash', label: tr('Ash（沉稳男声）', 'Ash (steady male voice)') },
  { value: 'ballad', label: tr('Ballad（讲述感）', 'Ballad (narrative)') },
  { value: 'coral', label: tr('Coral（温柔女声）', 'Coral (gentle female voice)') },
  { value: 'echo', label: tr('Echo（清晰明亮）', 'Echo (clear and bright)') },
  { value: 'fable', label: tr('Fable（故事感）', 'Fable (storytelling)') },
  { value: 'nova', label: tr('Nova（活泼女声）', 'Nova (lively female voice)') },
  { value: 'onyx', label: tr('Onyx（低沉男声）', 'Onyx (deep male voice)') },
  { value: 'sage', label: tr('Sage（成熟稳重）', 'Sage (mature and steady)') },
  { value: 'shimmer', label: tr('Shimmer（轻柔空灵）', 'Shimmer (soft and airy)') },
  { value: 'verse', label: tr('Verse（电台播音）', 'Verse (broadcast style)') }
] as const
const MEDIA_VOICE_STYLE_PRESETS = [
  { value: 'natural', label: '自然叙述', instruction: '语气自然口语化，像真实对话。' },
  { value: 'story', label: '故事旁白', instruction: '强调画面感与叙事节奏，像故事旁白。' },
  { value: 'radio', label: '电台播报', instruction: '语速稳健、吐字清晰，像电台主播。' },
  { value: 'anime', label: '二次元演绎', instruction: '情绪更鲜明，表达更有角色感。' },
  { value: 'gentle', label: '温柔陪伴', instruction: '语气柔和，停顿舒缓，听感放松。' }
] as const
const MEDIA_VOICE_EMOTION_OPTIONS = ['中性', '温柔', '活泼', '沉稳', '热情', '治愈', '严肃', '神秘'] as const
const DEFAULT_MEDIA_VOICE = MEDIA_VOICE_OPTIONS[0]?.value || 'alloy'
type PersonaVoiceGender = 'female' | 'male' | 'neutral'
const FEMALE_VOICE_CANDIDATES = ['nova', 'shimmer', 'coral'] as const
const MALE_VOICE_CANDIDATES = ['onyx', 'echo', 'fable', 'ash'] as const
const NEUTRAL_VOICE_CANDIDATES = ['alloy', 'sage', 'verse', 'ballad'] as const
const FEMALE_GENDER_HINTS = ['female', 'woman', 'girl', 'she', 'her', '女生', '女性', '少女', '女人', '女孩', '女主', '女角色']
const MALE_GENDER_HINTS = ['male', 'man', 'boy', 'he', 'his', '男生', '男性', '少年', '男人', '男孩', '男主', '男角色']
const FEMALE_AVATAR_HINTS = ['female', 'girl', 'woman', 'waifu', 'maid', 'princess', 'queen', 'cute', 'pink', 'longhair', 'long-hair', '女', '少女']
const MALE_AVATAR_HINTS = ['male', 'boy', 'man', 'husbando', 'prince', 'king', 'warrior', 'knight', 'beard', 'armor', 'short-hair', '男', '少年']
const FEMALE_PRONOUN_HINTS = ['她']
const MALE_PRONOUN_HINTS = ['他']
const VOICE_TOOLBOX_MODE_OPTIONS = [
  { value: 'auto_strict', label: '严格自动' },
  { value: 'auto_balanced', label: '平衡自动' },
  { value: 'manual_preferred', label: '手动优先' },
] as const
const DEFAULT_VOICE_TOOLBOX_SETTINGS: VoiceToolboxSettings = {
  mode: 'auto_strict',
  usePersonalitySignals: true,
  useAvatarSignals: true,
  keepPreferredVoiceFirst: true,
  fallbackVoice: 'alloy',
  femalePreferredVoice: 'shimmer',
  malePreferredVoice: 'onyx',
  neutralPreferredVoice: 'alloy',
}
const VOICE_PERSONALITY_HINT_RULES: Array<{ keywords: string[]; boosts: Partial<Record<string, number>> }> = [
  {
    keywords: ['温柔', '治愈', '细腻', '软萌', '甜', '轻声', '陪伴', '知心', '柔和'],
    boosts: { shimmer: 4, coral: 3, nova: 2, ballad: 1, alloy: 1 },
  },
  {
    keywords: ['活泼', '元气', '开朗', '俏皮', '可爱', '阳光', '热情', '灵动'],
    boosts: { nova: 4, coral: 2, echo: 1, shimmer: 1 },
  },
  {
    keywords: ['沉稳', '冷静', '理性', '专业', '成熟', '知性', '克制', '稳重'],
    boosts: { sage: 4, verse: 2, alloy: 2, ash: 1 },
  },
  {
    keywords: ['低沉', '严肃', '冷酷', '霸气', '战斗', '硬核', '果断', '压迫感'],
    boosts: { onyx: 5, ash: 3, fable: 1, echo: 1 },
  },
  {
    keywords: ['故事', '旁白', '诗意', '幻想', '叙事', '戏剧', '舞台', '吟游'],
    boosts: { fable: 3, ballad: 3, verse: 2, sage: 1 },
  },
]
const WEEKDAY_LABELS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'] as const
const SEASONAL_MOMENT_TOPICS_BY_MONTH: Record<number, string[]> = {
  1: ['新年计划', '寒假日常', '冬季保暖', '春节筹备'],
  2: ['情人节氛围', '开工复工', '春季穿搭', '新学期准备'],
  3: ['春游踏青', '开学状态', '健身打卡', '换季生活'],
  4: ['樱花季', '清明出行', '读书计划', '摄影分享'],
  5: ['劳动节出游', '初夏美食', '音乐节', '户外运动'],
  6: ['毕业季', '端午风味', '夏日宅家', '追剧推荐'],
  7: ['暑期档', '旅行攻略', '夜宵探店', '高温预警'],
  8: ['七夕话题', '夏末穿搭', '热门游戏活动', '演唱会现场'],
  9: ['开学季', '中秋前瞻', '秋日生活', '学习计划'],
  10: ['国庆假期', '秋游露营', '新游体验', '观影打卡'],
  11: ['双十一', '入冬仪式感', '城市漫步', '书影音推荐'],
  12: ['年末总结', '跨年安排', '圣诞氛围', '冬日火锅'],
}

// --- State ---
const showSettings = ref(false)
const settingsTab = ref<'api' | 'visual' | 'scripts' | 'themes'>('api')
const showGameSelector = ref(false)
const showGameEditor = ref(false)
const showScriptEditor = ref(false)
const showCharacterModal = ref(false)
const characterModalData = ref<CharacterCardData | null>(null)
const showMobileSidebar = ref(false)
const showVariablePicker = ref(false)
const isTyping = ref(false)
const isStreaming = ref(false)
const inputMessage = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const inputTextarea = ref<HTMLTextAreaElement | null>(null)
const personaCreatorBodyRef = ref<HTMLElement | null>(null)
const personaNameInputRef = ref<HTMLInputElement | null>(null)
const personaSystemPromptRef = ref<HTMLTextAreaElement | null>(null)
const userMediaInputRef = ref<HTMLInputElement | null>(null)
const groupMediaInputRef = ref<HTMLInputElement | null>(null)
const messages = ref<Message[]>([])
const isTesting = ref(false)
const testStatus = ref<{ success: boolean; message: string }>({ success: false, message: '' })
const isTestingImage = ref(false)
const imageTestStatus = ref<{ success: boolean; message: string }>({ success: false, message: '' })
const textareaHeight = ref('auto')
const availableVariables = ['{{current_game}}', '{{terminology}}']
const showUserProfileEditor = ref(false)
const showPersonaCreator = ref(false)
const personaCreateError = ref('')
const personaCardImportInfo = ref('')
const personaCardImportError = ref('')
const personaAutoFillInfo = ref('')
const personaAutoFillError = ref('')
const isAutoCompletingPersona = ref(false)
const avatarGeneratePrompt = ref('')
const avatarGenerateInfo = ref('')
const avatarGenerateError = ref('')
const isGeneratingAvatar = ref(false)
const userProfileInfo = ref('')
const userProfileError = ref('')
const isGeneratingUserProfileText = ref(false)
const isGeneratingUserAvatar = ref(false)
const isGeneratingUserProfileOneClick = ref(false)
const showMomentsPanel = ref(false)
const momentsPanelTab = ref<'feed' | 'group'>('feed')
const momentsPosts = ref<MomentPost[]>([])
const momentsComposerText = ref('')
const momentsInfo = ref('')
const momentsError = ref('')
const momentsCommentDrafts = ref<Record<string, string>>({})
const momentsInteractionScores = ref<Record<string, number>>({})
const momentsNextPostAt = ref<Record<string, number>>({})
const momentsLastViewedAt = ref(0)
const momentsTrendContext = ref<MomentsTrendContext>({
  dateKey: '',
  dateLabel: '',
  holidayLabels: [],
  hotTopics: [],
  personaAngles: [],
  source: 'local',
  updatedAt: 0,
})
const isPublishingMoment = ref(false)
const momentsHydrated = ref(false)
const isRefreshingMomentsTrend = ref(false)
const groupChats = ref<GroupChatRoom[]>([])
const selectedGroupChatId = ref('')
const groupDraftName = ref('')
const groupDraftAvatar = ref('')
const groupDraftMemberIds = ref<string[]>([])
const groupDraftAiAdminIds = ref<string[]>([])
const groupChatMessageDraft = ref('')
const groupChatInfo = ref('')
const groupChatError = ref('')
const groupAnnouncementDraftByRoomId = ref<Record<string, string>>({})
const groupRulesDraftByRoomId = ref<Record<string, string>>({})
const groupRenameDraftByRoomId = ref<Record<string, string>>({})
const groupAdminActorByRoomId = ref<Record<string, string>>({})
const groupAdminTransferTargetByRoomId = ref<Record<string, string>>({})
const groupAddMemberDraftByRoomId = ref<Record<string, string>>({})
const showGroupEmojiPanel = ref(false)
const selectedGroupEmojiCategory = ref<GroupEmojiCategory>('常用')
const groupMediaPickerType = ref<'image' | 'video'>('image')
const groupImageConsentPending = ref<GroupImageConsentRequest | null>(null)
const isGroupGeneratingImage = ref(false)
const isGroupGeneratingAudio = ref(false)
const showMediaGenerator = ref(false)
const activeMediaType = ref<MediaType>('image')
const mediaPromptInput = ref('')
const mediaVoice = ref(DEFAULT_MEDIA_VOICE)
const mediaVoiceStylePreset = ref(MEDIA_VOICE_STYLE_PRESETS[0]?.value || 'natural')
const mediaVoiceEmotion = ref<(typeof MEDIA_VOICE_EMOTION_OPTIONS)[number]>(MEDIA_VOICE_EMOTION_OPTIONS[0] || '中性')
const mediaSpeechRate = ref(1)
const mediaVoiceCustomStyle = ref('')
const voiceToolboxSettings = ref<VoiceToolboxSettings>({ ...DEFAULT_VOICE_TOOLBOX_SETTINGS })
const tempVoiceToolboxSettings = ref<VoiceToolboxSettings>({ ...DEFAULT_VOICE_TOOLBOX_SETTINGS })
const mediaGenerateInfo = ref('')
const mediaGenerateError = ref('')
const isGeneratingMedia = ref(false)
const userMediaUploadInfo = ref('')
const userMediaUploadError = ref('')
const networkStatusLabel = ref<(typeof NETWORK_STATUS_OPTIONS)[number]>('4G')
const personaLocationStatusMap = ref<Record<string, string>>({})
let networkStatusTimer: ReturnType<typeof setTimeout> | null = null
let momentsTimer: ReturnType<typeof setTimeout> | null = null
let personaLocationAssignToken = 0
const messageHtmlFrameHeights = ref<Record<string, number>>({})
const trackedObjectUrls = ref<string[]>([])

const createEmptyPersonaForm = (): PersonaCreateForm => ({
  name: '',
  nickname: '',
  age: '',
  gender: '',
  title: '',
  description: '',
  personality: '',
  background: '',
  firstMessage: '',
  systemPrompt: '',
  group: defaultCustomPersonaGroup(),
  avatarPreview: '',
  avatarUrl: ''
})

const createDefaultUserProfile = (): UserProfileForm => ({
  name: defaultUserName(),
  gender: '',
  personality: '',
  traits: '',
  chatStyle: '',
  avatarPreview: '',
  avatarUrl: '',
  avatarPrompt: ''
})

const personaForm = reactive<PersonaCreateForm>(createEmptyPersonaForm())
const userProfile = reactive<UserProfileForm>(createDefaultUserProfile())
const customPersonas = ref<Persona[]>([])
const brokenImportedPersonaIds = new Set<string>()
const personaAvatarErrorLock = new Set<string>()
const personaMissingFieldKeys = computed<PersonaAutoFillField[]>(() => {
  return PERSONA_AUTOFILL_FIELDS.filter((field) => {
    const value = personaForm[field]
    return typeof value !== 'string' || value.trim() === ''
  })
})
const personaCreateMissingLabels = computed<string[]>(() => {
  const missing: string[] = []
  if (!personaForm.name.trim()) missing.push(tr('角色名称', 'Role Name'))
  if (!personaForm.systemPrompt.trim()) missing.push(tr('系统提示词', 'System Prompt'))
  return missing
})
const canCreatePersona = computed(() => personaCreateMissingLabels.value.length === 0)

const personas = ref<Persona[]>(DEFAULT_PERSONAS)
const currentPersona = ref<Persona>(personas.value[0])
const personaSearchQuery = ref('')
const collapsedGroups = ref<Record<string, boolean>>({
  [PERSONA_GROUP_BASE]: true,
  [PERSONA_GROUP_NOVEL]: true
})

const normalizePersonaSearchText = (value: unknown): string =>
  String(value || '')
    .toLowerCase()
    .replace(/\s+/g, '')
    .trim()

const filteredPersonas = computed(() => {
  const keyword = normalizePersonaSearchText(personaSearchQuery.value)
  if (!keyword) return personas.value
  return personas.value.filter((persona) => {
    const fields = [
      persona.name,
      persona.description,
      persona.gender,
      persona.personality,
      persona.group,
      persona.id,
    ]
    return fields.some((field) => normalizePersonaSearchText(field).includes(keyword))
  })
})

const groupedPersonas = computed(() => {
  const groups: Record<string, Persona[]> = {}
  groups[PERSONA_GROUP_BASE] = []
  groups[PERSONA_GROUP_CHARACTER] = []
  groups[PERSONA_GROUP_NOVEL] = []

  filteredPersonas.value.forEach(p => {
    const g = p.group || PERSONA_GROUP_OTHER
    if (!groups[g]) groups[g] = []
    groups[g].push(p)
  })

  return groups
})

const currentPersonaAddressStatus = computed(() => {
  const currentId = String(currentPersona.value?.id || '')
  if (!currentId) return unknownLocationStatusLabel()
  return personaLocationStatusMap.value[currentId] || unknownLocationStatusLabel()
})

const toggleGroup = (groupName: string) => {
  collapsedGroups.value[groupName] = !collapsedGroups.value[groupName]
}

const games = ref<GameConfig[]>(DEFAULT_GAMES)
const currentGame = ref<GameConfig>(games.value[0])

// Theme Store State
const themes = ref<ThemeItem[]>([])
const themeSearchQuery = ref('')
const filteredThemes = computed(() => {
  if (!themeSearchQuery.value) return themes.value
  return themes.value.filter(t => t.name.toLowerCase().includes(themeSearchQuery.value.toLowerCase()))
})
const isApplyingTheme = ref(false)

// Editor State
const tempGame = reactive<GameConfig>({ id: '', name: '', themeColor: '#22c55e', quests: [], terminology: {} })
const tempGameQuests = ref('')

// Script State
const scripts = ref<Script[]>([])
const searchQuery = ref('')
const currentScript = reactive<Script>({ id: '', name: '', version: '1.0.0', enabled: true, code: '' })
const scriptSearch = computed(() => {
  if (!searchQuery.value) return scripts.value
  return scripts.value.filter(s => s.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

// Script Engine
class ScriptEngine {
  private api: any

  constructor() {
    this.api = {
      onMessage: (callback: (msg: Message) => void) => {
        // Mock hook
        console.log('Script registered onMessage hook')
      },
      onUIChange: (callback: (config: VisualConfig) => void) => {
        console.log('Script registered onUIChange hook')
      },
      getCharacterData: () => currentPersona.value,
      getGameData: () => currentGame.value,
      log: (msg: string) => console.log(`[Script]: ${msg}`)
    }
    
    // Inject global API
    ;(window as any).SillyTavernAPI = this.api
  }

  async loadScripts() {
    const savedScripts = localStorage.getItem('cypher_tavern_scripts')
    if (savedScripts) {
      try {
        scripts.value = JSON.parse(savedScripts)
        this.executeEnabledScripts()
      } catch (e) { console.error(e) }
    }
  }

  saveScripts() {
    localStorage.setItem('cypher_tavern_scripts', JSON.stringify(scripts.value))
  }

  executeEnabledScripts() {
     scripts.value.forEach(script => {
       if (script.enabled) {
         this.runScript(script)
       }
     })
   }

   runScript(script: Script) {
     try {
       script.error = undefined
       
       // Cleanup previous instance if exists (for re-runs)
       if ((script as any).cleanup) {
         (script as any).cleanup()
         ;(script as any).cleanup = undefined
       }

       // Wrap code in a safe scope
       const func = new Function('SillyTavernAPI', 'script', `
         try {
           ${script.code}
         } catch (e) {
           throw e
         }
       `)
       
       // Execute and store cleanup function if returned
       const cleanup = func(this.api, script)
       if (typeof cleanup === 'function') {
         ;(script as any).cleanup = cleanup
       }
       
     } catch (e: any) {
       console.error(`Script [${script.name}] execution error:`, e)
       script.error = e.message
     }
   }
   
   stopScript(script: Script) {
     if ((script as any).cleanup) {
       try {
         (script as any).cleanup()
         console.log(`Script [${script.name}] stopped and cleaned up.`)
       } catch (e) {
         console.error(`Script [${script.name}] cleanup error:`, e)
       }
       ;(script as any).cleanup = undefined
     }
   }
 }

const scriptEngine = new ScriptEngine()
const router = useRouter()

const apiSettings = ref<ApiSettings>({
  baseUrl: 'https://api.openai.com/v1',
  apiKey: '',
  modelName: 'gpt-3.5-turbo',
  imageBaseUrl: 'https://api.openai.com/v1',
  imageApiKey: '',
  imageModelName: 'gpt-image-1',
  imageApiType: 'openai_compatible',
  ttsProvider: 'openai_compatible',
  coquiBaseUrl: '/api/tts/coqui/synthesize/',
  coquiModelName: 'tts_models/multilingual/multi-dataset/xtts_v2',
  coquiLanguage: 'zh-cn',
  coquiSpeaker: '',
})

const visualSettings = ref<VisualConfig>({
  themeMode: 'light',
  bgStyle: 'solid',
  bubbleStyle: 'solid',
  enableAnimations: false,
  glassOpacity: 1
})

const tempSettings = ref<ApiSettings>({ ...apiSettings.value })
const tempVisualSettings = ref<VisualConfig>({ ...visualSettings.value })

const normalizeApiBaseUrl = (value: string) => String(value || '').trim().replace(/\/+$/, '')
const normalizeRelativeOrAbsoluteUrl = (value: unknown, fallback: string) => {
  const raw = String(value || '').trim()
  if (!raw) return fallback
  if (/^https?:\/\//i.test(raw)) return raw.replace(/\/+$/, '')
  if (raw.startsWith('/')) return raw.replace(/\/+$/, '') || fallback
  return `/${raw.replace(/^\/+/, '').replace(/\/+$/, '')}`
}
const ensureTrailingSlash = (url: string) => {
  const raw = String(url || '').trim()
  if (!raw) return raw
  const queryIndex = raw.indexOf('?')
  const hashIndex = raw.indexOf('#')
  const splitIndex = [queryIndex, hashIndex].filter((index) => index >= 0).sort((a, b) => a - b)[0] ?? -1
  if (splitIndex < 0) {
    return raw.endsWith('/') ? raw : `${raw}/`
  }
  const prefix = raw.slice(0, splitIndex)
  const suffix = raw.slice(splitIndex)
  return `${prefix.endsWith('/') ? prefix : `${prefix}/`}${suffix}`
}
const normalizeImageApiType = (value: unknown): ImageApiType => {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'gemini_native' || normalized === 'gemini' || normalized === 'google_native' || normalized === 'google') {
    return 'gemini_native'
  }
  return 'openai_compatible'
}
const normalizeTtsProvider = (value: unknown): TtsProvider => {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'coqui' || normalized === 'coqui_tts' || normalized === 'local_coqui') {
    return 'coqui'
  }
  return 'openai_compatible'
}
const inferImageApiTypeFromModel = (modelName: unknown): ImageApiType => {
  return /gemini/i.test(String(modelName || '')) ? 'gemini_native' : 'openai_compatible'
}
const defaultImageModelByType = (imageApiType: ImageApiType): string => {
  return imageApiType === 'gemini_native' ? 'gemini-2.5-flash-image-preview' : 'gpt-image-1'
}
const buildImageModelCandidates = (config: { modelName: string; imageApiType: ImageApiType }): string[] => {
  return Array.from(new Set([String(config.modelName || '').trim(), defaultImageModelByType(config.imageApiType)].filter(Boolean)))
}
const buildAudioModelCandidates = (configuredModel: string): string[] => {
  return Array.from(new Set(['gpt-4o-mini-tts', String(configuredModel || '').trim()].filter(Boolean)))
}

const resolveTextApiConfig = (): ResolvedApiConfig => ({
  baseUrl: normalizeApiBaseUrl(apiSettings.value.baseUrl),
  apiKey: String(apiSettings.value.apiKey || '').trim(),
  modelName: String(apiSettings.value.modelName || '').trim(),
})

const resolveImageApiConfig = (): ResolvedImageApiConfig => {
  const imageApiType = normalizeImageApiType(apiSettings.value.imageApiType)
  return {
    baseUrl: normalizeApiBaseUrl(apiSettings.value.imageBaseUrl || apiSettings.value.baseUrl),
    apiKey: String(apiSettings.value.imageApiKey || apiSettings.value.apiKey || '').trim(),
    modelName:
      String(apiSettings.value.imageModelName || apiSettings.value.modelName || '').trim() ||
      defaultImageModelByType(imageApiType),
    imageApiType,
  }
}
const resolveTtsConfig = (): ResolvedTtsConfig => ({
  ttsProvider: normalizeTtsProvider(apiSettings.value.ttsProvider),
  coquiBaseUrl: normalizeRelativeOrAbsoluteUrl(apiSettings.value.coquiBaseUrl, '/api/tts/coqui/synthesize/'),
  coquiModelName:
    String(apiSettings.value.coquiModelName || '').trim() ||
    'tts_models/multilingual/multi-dataset/xtts_v2',
  coquiLanguage: String(apiSettings.value.coquiLanguage || '').trim() || 'zh-cn',
  coquiSpeaker: normalizeCoquiSpeakerValue(apiSettings.value.coquiSpeaker),
})

const isConnected = computed(() => {
  const cfg = resolveTextApiConfig()
  return !!(cfg.baseUrl && cfg.apiKey)
})

const isImageConnected = computed(() => {
  const cfg = resolveImageApiConfig()
  return !!(cfg.baseUrl && cfg.apiKey)
})
const isAudioConnected = computed(() => {
  const textCfg = resolveTextApiConfig()
  if (!(textCfg.baseUrl && textCfg.apiKey)) return false
  const ttsCfg = resolveTtsConfig()
  if (ttsCfg.ttsProvider === 'coqui') {
    return !!ttsCfg.coquiBaseUrl
  }
  return true
})

const mediaLabelByType = (type: MediaType) => {
  if (type === 'video') return tr('视频', 'Video')
  if (type === 'audio') return tr('语音', 'Voice')
  return tr('图片', 'Image')
}

const activeMediaLabel = computed(() => {
  return mediaLabelByType(activeMediaType.value)
})

const mediaPromptPlaceholder = computed(() => {
  if (activeMediaType.value === 'video') {
    return tr(
      '可选：补充视频画面与镜头提示（留空则自动根据角色卡和上下文生成）',
      'Optional: add scene/camera hints for video'
    )
  }
  if (activeMediaType.value === 'audio') {
    return tr(
      '可选：补充语音内容或情绪风格（留空则自动根据角色卡和上下文生成）',
      'Optional: add voice content/emotion hints'
    )
  }
  return tr(
    '可选：补充图片风格提示（留空则自动根据角色卡和上下文生成）',
    'Optional: add image style hints'
  )
})

const getVoiceLabel = (voiceValue: string) => {
  return MEDIA_VOICE_OPTIONS.find((item) => item.value === voiceValue)?.label || voiceValue
}

const mediaVoiceStyleOptions = computed(() => {
  return MEDIA_VOICE_STYLE_PRESETS.map((preset) => {
    if (preset.value === 'natural') return { ...preset, label: tr('自然叙述', 'Natural') }
    if (preset.value === 'story') return { ...preset, label: tr('故事旁白', 'Narration') }
    if (preset.value === 'radio') return { ...preset, label: tr('电台播报', 'Broadcast') }
    if (preset.value === 'anime') return { ...preset, label: tr('二次元演绎', 'Anime Style') }
    if (preset.value === 'gentle') return { ...preset, label: tr('温柔陪伴', 'Gentle') }
    return preset
  })
})

const mediaVoiceEmotionOptions = computed(() => {
  return MEDIA_VOICE_EMOTION_OPTIONS.map((emotion) => {
    const labelMap: Record<string, string> = {
      中性: 'Neutral',
      温柔: 'Gentle',
      活泼: 'Lively',
      沉稳: 'Steady',
      热情: 'Warm',
      治愈: 'Soothing',
      严肃: 'Serious',
      神秘: 'Mysterious',
    }
    return {
      value: emotion,
      label: tr(emotion, labelMap[emotion] || emotion),
    }
  })
})

const voiceToolboxModeOptions = computed(() => {
  return VOICE_TOOLBOX_MODE_OPTIONS.map((mode) => {
    if (mode.value === 'auto_strict') return { ...mode, label: tr('严格自动', 'Auto Strict') }
    if (mode.value === 'auto_balanced') return { ...mode, label: tr('平衡自动', 'Auto Balanced') }
    if (mode.value === 'manual_preferred') return { ...mode, label: tr('手动优先', 'Manual Preferred') }
    return mode
  })
})
const femaleVoiceOptionsForToolbox = MEDIA_VOICE_OPTIONS.filter(
  (voice) => FEMALE_VOICE_CANDIDATES.includes(voice.value as any) || NEUTRAL_VOICE_CANDIDATES.includes(voice.value as any)
)
const maleVoiceOptionsForToolbox = MEDIA_VOICE_OPTIONS.filter(
  (voice) => MALE_VOICE_CANDIDATES.includes(voice.value as any) || NEUTRAL_VOICE_CANDIDATES.includes(voice.value as any)
)
const neutralVoiceOptionsForToolbox = MEDIA_VOICE_OPTIONS.filter(
  (voice) => NEUTRAL_VOICE_CANDIDATES.includes(voice.value as any)
)

const normalizeVoiceValue = (value: unknown, fallback = DEFAULT_MEDIA_VOICE) => {
  const normalized = String(value || '').trim().toLowerCase()
  if (MEDIA_VOICE_OPTIONS.some((item) => item.value === normalized)) return normalized
  return fallback
}
const OPENAI_STYLE_VOICE_VALUE_SET = new Set(MEDIA_VOICE_OPTIONS.map((item) => item.value))
const normalizeCoquiSpeakerValue = (value: unknown) => {
  const speaker = normalizeStorageText(value)
  if (!speaker) return ''
  // Filter out OpenAI voice ids accidentally persisted into Coqui speaker config.
  if (OPENAI_STYLE_VOICE_VALUE_SET.has(speaker.toLowerCase())) return ''
  return speaker
}

const countKeywordHits = (source: string, keywords: readonly string[]) => {
  if (!source) return 0
  return keywords.reduce((count, keyword) => {
    const target = String(keyword || '').toLowerCase()
    return target && source.includes(target) ? count + 1 : count
  }, 0)
}

const normalizeVoiceToolboxSettings = (payload: any): VoiceToolboxSettings => {
  const source = payload && typeof payload === 'object' ? payload : {}
  const modeSource = String(source.mode || '').toLowerCase()
  const mode: VoiceToolboxMode =
    modeSource === 'auto_balanced' || modeSource === 'manual_preferred'
      ? modeSource
      : 'auto_strict'

  return {
    mode,
    usePersonalitySignals: source.usePersonalitySignals !== false,
    useAvatarSignals: source.useAvatarSignals !== false,
    keepPreferredVoiceFirst: source.keepPreferredVoiceFirst !== false,
    fallbackVoice: normalizeVoiceValue(source.fallbackVoice, DEFAULT_VOICE_TOOLBOX_SETTINGS.fallbackVoice),
    femalePreferredVoice: normalizeVoiceValue(source.femalePreferredVoice, DEFAULT_VOICE_TOOLBOX_SETTINGS.femalePreferredVoice),
    malePreferredVoice: normalizeVoiceValue(source.malePreferredVoice, DEFAULT_VOICE_TOOLBOX_SETTINGS.malePreferredVoice),
    neutralPreferredVoice: normalizeVoiceValue(source.neutralPreferredVoice, DEFAULT_VOICE_TOOLBOX_SETTINGS.neutralPreferredVoice),
  }
}

const detectVoiceGenderHintFromText = (text: string): PersonaVoiceGender | null => {
  const source = String(text || '').toLowerCase()
  if (!source) return null

  const femaleHints = ['女声', '女生音', '女性音', '女孩子', '少女音', '御姐音', '萝莉音', 'female voice', 'female']
  const maleHints = ['男声', '男生音', '男性音', '少年音', '大叔音', 'male voice', 'male']
  const femaleHits = femaleHints.reduce((count, hint) => (source.includes(hint) ? count + 1 : count), 0)
  const maleHits = maleHints.reduce((count, hint) => (source.includes(hint) ? count + 1 : count), 0)
  if (femaleHits > maleHits && femaleHits > 0) return 'female'
  if (maleHits > femaleHits && maleHits > 0) return 'male'
  return null
}

const parseExplicitPersonaGender = (value: string): PersonaVoiceGender | null => {
  const source = String(value || '').toLowerCase().trim()
  if (!source) return null
  if (
    /^(女|女生|女性|female|woman|girl)$/i.test(source) ||
    source.includes('女性') ||
    source.includes('女生') ||
    source.includes('female')
  ) {
    return 'female'
  }
  if (
    /^(男|男生|男性|male|man|boy)$/i.test(source) ||
    source.includes('男性') ||
    source.includes('男生') ||
    source.includes('male')
  ) {
    return 'male'
  }
  return null
}

const buildPersonaGenderSignalText = (persona: Persona) => {
  return [
    persona.name || '',
    persona.gender || '',
    persona.description || '',
    persona.personality || '',
    persona.group || '',
  ]
    .join(' ')
    .toLowerCase()
}

const buildPersonaVoiceSignalText = (persona: Persona) => {
  return [
    persona.gender || '',
    persona.personality || '',
    persona.name || '',
    persona.description || '',
    persona.systemPrompt || '',
    persona.group || '',
    persona.firstMessage || '',
  ]
    .join(' ')
    .toLowerCase()
}

const inferPersonaGenderForVoice = (persona: Persona, settings: VoiceToolboxSettings = voiceToolboxSettings.value): PersonaVoiceGender => {
  const explicitGender = parseExplicitPersonaGender(persona.gender || '')
  if (explicitGender) return explicitGender

  const signalText = buildPersonaGenderSignalText(persona)
  let femaleScore = 0
  let maleScore = 0

  femaleScore += countKeywordHits(signalText, FEMALE_GENDER_HINTS)
  maleScore += countKeywordHits(signalText, MALE_GENDER_HINTS)

  // Pronoun weight is lower to avoid "他/她" in system texts causing false matches.
  femaleScore += countKeywordHits(signalText, FEMALE_PRONOUN_HINTS) * 0.35
  maleScore += countKeywordHits(signalText, MALE_PRONOUN_HINTS) * 0.35

  if (settings.useAvatarSignals) {
    const avatarSource = decodeURIComponent(String(persona.avatar || ''))
      .toLowerCase()
      .replace(/[^\w\u4e00-\u9fa5-]/g, ' ')
    femaleScore += countKeywordHits(avatarSource, FEMALE_AVATAR_HINTS) * 1.8
    maleScore += countKeywordHits(avatarSource, MALE_AVATAR_HINTS) * 1.8
  }

  const diff = femaleScore - maleScore
  if (diff >= 1.1) return 'female'
  if (diff <= -1.1) return 'male'
  return 'neutral'
}

const applyVoiceBoost = (scoreMap: Map<string, number>, boosts: Partial<Record<string, number>>, weight = 1) => {
  Object.entries(boosts).forEach(([voice, boost]) => {
    const value = Number(boost || 0)
    if (!value || !scoreMap.has(voice)) return
    scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + value * weight)
  })
}

const resolveVoiceCandidatesByPersona = (
  persona: Persona,
  preferredVoice: string,
  rawSettings: VoiceToolboxSettings = voiceToolboxSettings.value,
  forcedGender: PersonaVoiceGender | null = null
) => {
  const settings = normalizeVoiceToolboxSettings(rawSettings)
  const personaGender = forcedGender || inferPersonaGenderForVoice(persona, settings)
  const femaleVoices = [...FEMALE_VOICE_CANDIDATES]
  const maleVoices = [...MALE_VOICE_CANDIDATES]
  const neutralVoices = [...NEUTRAL_VOICE_CANDIDATES]
  const allVoices = MEDIA_VOICE_OPTIONS.map((item) => item.value)
  const scoreMap = new Map<string, number>(allVoices.map((voice) => [voice, 0]))

  if (personaGender === 'female') {
    femaleVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + 12))
    neutralVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + 6))
    maleVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + (settings.mode === 'auto_balanced' ? 1 : -18)))
    scoreMap.set(settings.femalePreferredVoice, Number(scoreMap.get(settings.femalePreferredVoice) || 0) + 5)
  } else if (personaGender === 'male') {
    maleVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + 12))
    neutralVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + 6))
    femaleVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + (settings.mode === 'auto_balanced' ? 1 : -18)))
    scoreMap.set(settings.malePreferredVoice, Number(scoreMap.get(settings.malePreferredVoice) || 0) + 5)
  } else {
    neutralVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + 9))
    femaleVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + 3))
    maleVoices.forEach((voice) => scoreMap.set(voice, Number(scoreMap.get(voice) || 0) + (settings.mode === 'auto_balanced' ? 3 : 1)))
    scoreMap.set(settings.neutralPreferredVoice, Number(scoreMap.get(settings.neutralPreferredVoice) || 0) + 4)
  }

  if (settings.usePersonalitySignals) {
    const personalitySource = buildPersonaVoiceSignalText(persona)
    VOICE_PERSONALITY_HINT_RULES.forEach((rule) => {
      const hitCount = countKeywordHits(personalitySource, rule.keywords)
      if (hitCount <= 0) return
      applyVoiceBoost(scoreMap, rule.boosts, hitCount)
    })
  }

  if (settings.useAvatarSignals) {
    const avatarSource = decodeURIComponent(String(persona.avatar || '')).toLowerCase()
    const femaleHitCount = countKeywordHits(avatarSource, FEMALE_AVATAR_HINTS)
    const maleHitCount = countKeywordHits(avatarSource, MALE_AVATAR_HINTS)
    if (femaleHitCount > 0) {
      applyVoiceBoost(scoreMap, { shimmer: 2, coral: 2, nova: 1 }, femaleHitCount)
    }
    if (maleHitCount > 0) {
      applyVoiceBoost(scoreMap, { onyx: 2, ash: 2, echo: 1 }, maleHitCount)
    }
  }

  const selected = normalizeVoiceValue(preferredVoice, '')
  const hasExplicitPreferredVoice = Boolean(selected && selected !== DEFAULT_MEDIA_VOICE && !forcedGender)
  if (selected) {
    const isMismatch =
      (personaGender === 'female' && maleVoices.includes(selected as any)) ||
      (personaGender === 'male' && femaleVoices.includes(selected as any))
    if (hasExplicitPreferredVoice || settings.mode === 'manual_preferred' || (settings.keepPreferredVoiceFirst && !isMismatch)) {
      scoreMap.set(
        selected,
        Number(scoreMap.get(selected) || 0) + (hasExplicitPreferredVoice || settings.mode === 'manual_preferred' ? 24 : 8)
      )
    }
  }

  const strictGender = settings.mode === 'auto_strict' && !hasExplicitPreferredVoice
  let candidateVoices = allVoices
  if (strictGender && personaGender === 'female') {
    candidateVoices = allVoices.filter((voice) => !maleVoices.includes(voice as any))
  } else if (strictGender && personaGender === 'male') {
    candidateVoices = allVoices.filter((voice) => !femaleVoices.includes(voice as any))
  }

  const originalOrderMap = new Map(allVoices.map((voice, index) => [voice, index]))
  candidateVoices.sort((a, b) => {
    const scoreDelta = Number(scoreMap.get(b) || 0) - Number(scoreMap.get(a) || 0)
    if (scoreDelta !== 0) return scoreDelta
    return Number(originalOrderMap.get(a) || 0) - Number(originalOrderMap.get(b) || 0)
  })

  const finalList: string[] = []
  const seen = new Set<string>()
  const appendUnique = (voice: string) => {
    if (!voice || seen.has(voice)) return
    seen.add(voice)
    finalList.push(voice)
  }

  candidateVoices.forEach((voice) => appendUnique(voice))
  if (!strictGender) {
    appendUnique(settings.fallbackVoice)
    appendUnique('alloy')
    allVoices.forEach((voice) => appendUnique(voice))
  } else {
    if (candidateVoices.includes(settings.fallbackVoice)) appendUnique(settings.fallbackVoice)
    if (candidateVoices.includes('alloy')) appendUnique('alloy')
    neutralVoices.forEach((voice) => appendUnique(voice))
    candidateVoices.forEach((voice) => appendUnique(voice))
  }
  return finalList
}

const resolvePrimaryVoiceForPersona = (persona: Persona, settings: VoiceToolboxSettings = voiceToolboxSettings.value) => {
  const candidates = resolveVoiceCandidatesByPersona(persona, mediaVoice.value, settings)
  return normalizeVoiceValue(candidates[0], DEFAULT_MEDIA_VOICE)
}

const buildAudioVoiceInstruction = () => {
  const parts: string[] = []
  const preset = MEDIA_VOICE_STYLE_PRESETS.find((item) => item.value === mediaVoiceStylePreset.value)
  const customStyle = mediaVoiceCustomStyle.value.trim().slice(0, 120)

  if (preset?.instruction) parts.push(preset.instruction)
  if (mediaVoiceEmotion.value && mediaVoiceEmotion.value !== '中性') {
    parts.push(`整体情绪偏${mediaVoiceEmotion.value}。`)
  }
  if (customStyle) {
    parts.push(`个性化要求：${customStyle}。`)
  }
  parts.push('保持发音清晰，停顿自然。')
  return parts.join('')
}

const userDisplayName = computed(() => {
  return userProfile.name.trim() || defaultUserName()
})

const userAvatarDisplay = computed(() => {
  const preview = userProfile.avatarPreview.trim()
  if (preview) return preview
  const external = userProfile.avatarUrl.trim()
  if (external) return external
  return USER_AVATAR_URL
})

const buildUserProfilePromptContext = () => {
  const lines = [
    userDisplayName.value ? `用户名称：${userDisplayName.value}` : '',
    userProfile.gender.trim() ? `用户性别：${userProfile.gender.trim()}` : '',
    userProfile.personality.trim() ? `用户性格：${userProfile.personality.trim()}` : '',
    userProfile.traits.trim() ? `用户特点：${userProfile.traits.trim()}` : '',
    userProfile.chatStyle.trim() ? `用户聊天风格偏好：${userProfile.chatStyle.trim()}` : ''
  ].filter(Boolean)
  return lines.join('\n')
}

const buildEffectiveSystemPrompt = () => {
  let finalSystemPrompt = currentPersona.value.systemPrompt || ''
  if (currentGame.value.systemPrompt) {
    finalSystemPrompt = finalSystemPrompt.replace('{{npc_role}}', currentGame.value.systemPrompt)
  } else {
    finalSystemPrompt = finalSystemPrompt.replace('{{npc_role}}', currentGame.value.npcRole || 'Assistant')
  }

  const userContext = buildUserProfilePromptContext()
  return finalSystemPrompt
    .replace(/{{user}}/g, userDisplayName.value)
    .replace('{{current_game}}', currentGame.value.name)
    .replace('{{terminology}}', JSON.stringify(currentGame.value.terminology))
    + (userContext ? `\n\n[用户设定]\n${userContext}` : '')
}

const extractChatTextContent = (payload: any) => {
  const primary = payload?.choices?.[0]?.message?.content
  if (typeof primary === 'string' && primary.trim()) return primary.trim()
  if (Array.isArray(primary)) {
    const parts = primary
      .map((item: any) => (typeof item === 'string' ? item : pickFirstString(item?.text, item?.content)))
      .filter(Boolean)
    if (parts.length) return parts.join('').trim()
  }
  return pickFirstString(
    payload?.output_text,
    payload?.data?.[0]?.text,
    payload?.output?.[0]?.content?.[0]?.text
  )
}

const normalizeNarrationText = (raw: string) => {
  return sanitizeContextText(raw)
    .replace(/^(语音文本|语音台词|台词|旁白|回复)[:：]\s*/i, '')
    .replace(/^["“”'`]+|["“”'`]+$/g, '')
    .trim()
}

const currentQuest = computed(() => {
  // Find the last quest in messages
  const lastQuestMsg = [...messages.value].reverse().find(m => m.questData)
  if (lastQuestMsg && lastQuestMsg.questData) {
    return {
      title: lastQuestMsg.questData.quest,
      description: lastQuestMsg.questData.description
    }
  }
  return null
})

const momentsUnreadCount = computed(() => {
  return momentsPosts.value.filter((post) => post.authorId !== 'user' && post.createdAt > momentsLastViewedAt.value).length
})

const momentsInteractionLeaders = computed(() => {
  const records = Object.entries(momentsInteractionScores.value)
    .filter(([, score]) => Number(score) > 0)
    .map(([personaId, score]) => {
      const persona = personas.value.find((item) => item.id === personaId)
      return {
        personaId,
        name: persona?.name || '未知角色',
        score: Number(score) || 0
      }
    })
    .sort((a, b) => b.score - a.score)
  return records.slice(0, 8)
})

const momentsTrendSummary = computed(() => {
  const holidays = momentsTrendContext.value.holidayLabels
  const hotTopics = momentsTrendContext.value.hotTopics
  const holidayText = holidays.length > 0 ? holidays.join(' / ') : '无节假日'
  const topicText = hotTopics.length > 0 ? hotTopics.slice(0, 4).join('、') : '日常生活'
  return `节日：${holidayText}；热点：${topicText}`
})

const groupSelectableAiMembers = computed(() => {
  return personas.value.filter((persona) => persona.id && persona.id !== 'user')
})

const groupChatsSorted = computed(() => {
  return [...groupChats.value]
    .filter((room) => !room.dissolved)
    .sort((a, b) => Number(b.updatedAt || 0) - Number(a.updatedAt || 0))
})

const selectedGroupChat = computed(() => {
  const targetId = String(selectedGroupChatId.value || '')
  if (!targetId) return null
  return groupChats.value.find((room) => room.id === targetId && !room.dissolved) || null
})

const selectedGroupChatAdminMembers = computed(() => {
  if (!selectedGroupChat.value) return []
  return selectedGroupChat.value.members.filter((member) => member.isAdmin)
})

const selectedGroupChatAddableMembers = computed(() => {
  if (!selectedGroupChat.value) return []
  const existingIdSet = new Set(selectedGroupChat.value.members.map((member) => member.id))
  return groupSelectableAiMembers.value.filter((persona) => !existingIdSet.has(persona.id))
})

const groupReplyModeOptions = computed(() => {
  return GROUP_REPLY_MODE_OPTIONS.map((option) => {
    if (option.value === 'cold') {
      return {
        ...option,
        label: tr('冷漠', 'Cold'),
        description: tr('少量回复、偏文字', 'fewer replies, mostly text'),
      }
    }
    if (option.value === 'normal') {
      return {
        ...option,
        label: tr('正常', 'Normal'),
        description: tr('均衡互动、稳定回复', 'balanced interaction'),
      }
    }
    if (option.value === 'warm') {
      return {
        ...option,
        label: tr('热情', 'Warm'),
        description: tr('更多角色参与、媒体更多', 'more role participation'),
      }
    }
    if (option.value === 'frenzy') {
      return {
        ...option,
        label: tr('狂热', 'Frenzy'),
        description: tr('高频连聊、强互动', 'high-frequency interaction'),
      }
    }
    return option
  })
})
const groupEmojiCategories = GROUP_EMOJI_CATEGORIES
const activeGroupEmojiList = computed(() => {
  return GROUP_EMOJI_LIBRARY[selectedGroupEmojiCategory.value] || GROUP_EMOJI_LIBRARY.常用
})

const clampNumber = (value: number, min: number, max: number) => {
  return Math.max(min, Math.min(max, value))
}

const randomBetween = (min: number, max: number) => {
  const low = Math.min(min, max)
  const high = Math.max(min, max)
  return low + Math.floor(Math.random() * (high - low + 1))
}

const createMomentId = () => {
  return `moment_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

const createGroupChatId = () => {
  return `group_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

const createGroupChatMessageId = () => {
  return `group_msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

const normalizeGroupName = (value: string) => {
  return sanitizeContextText(String(value || '').replace(/\r/g, '\n')).slice(0, 30)
}

const normalizeGroupMessageContent = (value: string, maxLen = 220) => {
  return sanitizeContextText(String(value || '').replace(/\r/g, '\n')).slice(0, maxLen)
}

const normalizeGroupReplyMode = (value: unknown): GroupReplyMode => {
  const mode = String(value || '').toLowerCase()
  if (mode === 'cold' || mode === 'warm' || mode === 'frenzy') return mode
  return 'normal'
}

const getGroupReplyModeLabel = (mode: GroupReplyMode) => {
  const entry = groupReplyModeOptions.value.find((item) => item.value === mode)
  return entry?.label || tr('正常', 'Normal')
}

const normalizeGroupAnnouncement = (value: string) => {
  return normalizeGroupMessageContent(value, 220)
}

const normalizeGroupRules = (value: string) => {
  return normalizeGroupMessageContent(value, 520)
}

const getGroupMediaTriggerType = (triggerText: string): 'image' | 'video' | null => {
  const source = String(triggerText || '').toLowerCase()
  if (source.includes('[group_media:video]') || source.includes('[用户发送视频]')) return 'video'
  if (source.includes('[group_media:image]') || source.includes('[用户发送图片]')) return 'image'
  return null
}

const shouldBlockAiAdminActionByUserIntent = (triggerText: string) => {
  const source = String(triggerText || '').replace(/\s+/g, '')
  if (!source) return false
  const hasDenyIntent = /(不要|别|不许|禁止|先别|暂时别)/.test(source)
  const hasAdminAction = /(管理|管理员|踢|移出|改名|解散|公告|群规)/.test(source)
  return hasDenyIntent && hasAdminAction
}

const ensureGroupRoomDefaults = (room: GroupChatRoom): GroupChatRoom => {
  room.replyMode = normalizeGroupReplyMode((room as any).replyMode)
  room.announcement = normalizeGroupAnnouncement(String((room as any).announcement || ''))
  room.rules = normalizeGroupRules(String((room as any).rules || ''))
  return room
}

const buildDefaultGroupAvatar = (seed: string) => {
  const safeSeed = encodeURIComponent(seed || `group_${Date.now()}`)
  return `https://api.dicebear.com/7.x/shapes/svg?seed=${safeSeed}&backgroundColor=e2e8f0`
}

const buildUserGroupMember = (): GroupChatMember => {
  return {
    id: 'user',
    name: userDisplayName.value || '你',
    avatar: userAvatarDisplay.value || USER_AVATAR_URL,
    isAi: false,
    isAdmin: true,
  }
}

const buildPersonaGroupMember = (persona: Persona, isAdmin = false): GroupChatMember => {
  return {
    id: persona.id,
    name: persona.name,
    avatar: persona.avatar,
    isAi: true,
    isAdmin,
  }
}

const buildGroupSystemMessage = (content: string, createdAt = Date.now()): GroupChatMessage => {
  return {
    id: createGroupChatMessageId(),
    senderId: 'system',
    senderName: '系统',
    senderAvatar: '',
    type: 'system',
    content: normalizeGroupMessageContent(content, 260),
    createdAt,
  }
}

const buildGroupMessage = (
  sender: { id: string; name: string; avatar: string },
  type: GroupChatMessageType,
  content: string,
  options: { mediaUrl?: string; createdAt?: number } = {}
): GroupChatMessage => {
  return {
    id: createGroupChatMessageId(),
    senderId: sender.id,
    senderName: sender.name,
    senderAvatar: sender.avatar,
    type,
    content: normalizeGroupMessageContent(content, 260),
    mediaUrl: options.mediaUrl || '',
    createdAt: Number(options.createdAt || Date.now()),
  }
}

const shuffleArray = <T>(items: T[]) => {
  const cloned = [...items]
  for (let i = cloned.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[cloned[i], cloned[j]] = [cloned[j], cloned[i]]
  }
  return cloned
}

const normalizeMomentContent = (value: string) => {
  return sanitizeContextText(String(value || '').replace(/\r/g, '\n')).slice(0, MOMENTS_MAX_CONTENT_LENGTH)
}

const getMomentLikeCount = (post: MomentPost) => {
  return (post.likedByUser ? 1 : 0) + post.likedByPersonaIds.length
}

const formatMomentTime = (timestamp: number) => {
  const delta = Date.now() - timestamp
  if (delta < 60 * 1000) return '刚刚'
  if (delta < 60 * 60 * 1000) return `${Math.floor(delta / (60 * 1000))}分钟前`
  if (delta < 24 * 60 * 60 * 1000) return `${Math.floor(delta / (60 * 60 * 1000))}小时前`
  const date = new Date(timestamp)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hour}:${minute}`
}

const getPersonaInteractionScore = (personaId: string) => {
  return Number(momentsInteractionScores.value[personaId] || 0)
}

const getPersonaById = (personaId: string) => {
  return personas.value.find((persona) => persona.id === personaId)
}

const getMomentPostIntervalMs = (score: number, initial = false) => {
  if (score >= 6) {
    if (initial) return randomBetween(25 * 60 * 1000, 90 * 60 * 1000)
    return randomBetween(8 * 60 * 60 * 1000, 12 * 60 * 60 * 1000) // 高互动：约 2-3 次/天
  }
  if (score >= 3) {
    if (initial) return randomBetween(60 * 60 * 1000, 3 * 60 * 60 * 1000)
    return randomBetween(12 * 60 * 60 * 1000, 20 * 60 * 60 * 1000)
  }
  if (initial) return randomBetween(2 * 60 * 60 * 1000, 8 * 60 * 60 * 1000)
  return randomBetween(18 * 60 * 60 * 1000, 40 * 60 * 60 * 1000)
}

const refreshPersonaMomentSchedule = (personaId: string, now = Date.now(), initial = false) => {
  const score = getPersonaInteractionScore(personaId)
  momentsNextPostAt.value[personaId] = now + getMomentPostIntervalMs(score, initial)
}

const ensureMomentsSchedule = (now = Date.now()) => {
  syncMomentsDataWithPersonas()
  const aiPersonas = personas.value.filter((item) => item.id && item.id !== 'user')
  aiPersonas.forEach((persona) => {
    if (!momentsNextPostAt.value[persona.id]) {
      refreshPersonaMomentSchedule(persona.id, now, true)
    }
  })
}

const formatMomentsDateKey = (date: Date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const formatMomentsDateLabel = (date: Date) => {
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = WEEKDAY_LABELS[date.getDay()] || ''
  return `${month}月${day}日 ${weekday}`
}

const getNthWeekdayOfMonth = (year: number, monthIndex: number, weekday: number, nth: number) => {
  const firstDay = new Date(year, monthIndex, 1).getDay()
  const offset = (weekday - firstDay + 7) % 7
  return 1 + offset + (nth - 1) * 7
}

const getMomentsHolidayLabels = (date: Date) => {
  const month = date.getMonth() + 1
  const day = date.getDate()
  const year = date.getFullYear()
  const key = `${month}-${day}`
  const fixedHolidays: Record<string, string> = {
    '1-1': '元旦',
    '2-14': '情人节',
    '3-8': '妇女节',
    '4-1': '愚人节',
    '4-4': '清明节',
    '4-5': '清明假期',
    '5-1': '劳动节',
    '5-4': '青年节',
    '6-1': '儿童节',
    '9-10': '教师节',
    '10-1': '国庆节',
    '10-31': '万圣节',
    '11-11': '双十一',
    '12-24': '平安夜',
    '12-25': '圣诞节',
    '12-31': '跨年夜',
  }
  const labels: string[] = []
  if (fixedHolidays[key]) labels.push(fixedHolidays[key])

  const mothersDay = getNthWeekdayOfMonth(year, 4, 0, 2) // May second Sunday
  if (month === 5 && day === mothersDay) labels.push('母亲节')
  const fathersDay = getNthWeekdayOfMonth(year, 5, 0, 3) // June third Sunday
  if (month === 6 && day === fathersDay) labels.push('父亲节')
  const thanksGiving = getNthWeekdayOfMonth(year, 10, 4, 4) // Nov fourth Thursday
  if (month === 11 && day === thanksGiving) labels.push('感恩节')

  if (month === 1 || month === 2) labels.push('春节季')
  if (month >= 6 && month <= 8) labels.push('暑期档')
  if (month === 9) labels.push('开学季')
  if (month === 12) labels.push('年末季')

  return Array.from(new Set(labels))
}

const normalizeTrendTopic = (value: unknown, maxLen = 16): string => {
  return String(value || '')
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/[，,。；;|]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maxLen)
}

const mergeUniqueTopics = (items: unknown[], maxCount = 12): string[] => {
  const merged: string[] = []
  for (const item of items) {
    const text = normalizeTrendTopic(item)
    if (!text) continue
    if (merged.includes(text)) continue
    merged.push(text)
    if (merged.length >= maxCount) break
  }
  return merged
}

const buildFallbackMomentsTrendContext = (date = new Date()): MomentsTrendContext => {
  const month = date.getMonth() + 1
  const holidayLabels = getMomentsHolidayLabels(date)
  const seasonalTopics = SEASONAL_MOMENT_TOPICS_BY_MONTH[month] || ['日常记录', '生活分享']
  const holidayTopics = holidayLabels.flatMap((label) => [`${label}氛围`, `${label}活动`])
  const hotTopics = mergeUniqueTopics([...holidayTopics, ...seasonalTopics], 10)
  return {
    dateKey: formatMomentsDateKey(date),
    dateLabel: formatMomentsDateLabel(date),
    holidayLabels,
    hotTopics,
    personaAngles: [],
    source: 'local',
    updatedAt: Date.now(),
  }
}

const loadMomentsTrendContext = (): MomentsTrendContext => {
  const raw = localStorage.getItem(MOMENTS_TREND_CONTEXT_STORAGE_KEY)
  if (!raw) return buildFallbackMomentsTrendContext()
  try {
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return buildFallbackMomentsTrendContext()
    const next: MomentsTrendContext = {
      dateKey: String(parsed.dateKey || ''),
      dateLabel: String(parsed.dateLabel || ''),
      holidayLabels: mergeUniqueTopics(Array.isArray(parsed.holidayLabels) ? parsed.holidayLabels : [], 8),
      hotTopics: mergeUniqueTopics(Array.isArray(parsed.hotTopics) ? parsed.hotTopics : [], 12),
      personaAngles: mergeUniqueTopics(Array.isArray(parsed.personaAngles) ? parsed.personaAngles : [], 8),
      source: parsed.source === 'ai' || parsed.source === 'mixed' ? parsed.source : 'local',
      updatedAt: Number(parsed.updatedAt || 0),
    }
    if (!next.dateKey || next.hotTopics.length === 0) return buildFallbackMomentsTrendContext()
    return next
  } catch {
    return buildFallbackMomentsTrendContext()
  }
}

const saveMomentsTrendContext = () => {
  localStorage.setItem(MOMENTS_TREND_CONTEXT_STORAGE_KEY, JSON.stringify(momentsTrendContext.value))
}

const refreshMomentsTrendContext = async (force = false) => {
  const now = Date.now()
  const today = buildFallbackMomentsTrendContext(new Date())

  const isSameDay = momentsTrendContext.value.dateKey === today.dateKey
  const withinInterval = now - Number(momentsTrendContext.value.updatedAt || 0) < MOMENTS_TREND_REFRESH_INTERVAL_MS
  if (!force && isSameDay && withinInterval && momentsTrendContext.value.hotTopics.length > 0) {
    return
  }
  if (isRefreshingMomentsTrend.value) return

  isRefreshingMomentsTrend.value = true
  try {
    let aiTopics: string[] = []
    let aiAngles: string[] = []
    let source: MomentsTrendContext['source'] = 'local'

    if (isConnected.value) {
      try {
        const personaNames = personas.value
          .filter((item) => item.id && item.id !== 'user')
          .map((item) => item.name)
          .slice(0, 10)
        const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiSettings.value.apiKey}`
          },
          body: JSON.stringify({
            model: apiSettings.value.modelName,
            stream: false,
            temperature: 0.75,
            max_tokens: 320,
            messages: [
              {
                role: 'system',
                content: '你是热点与节日内容策划助手。只返回 JSON 对象，不要解释，不要 Markdown。'
              },
              {
                role: 'user',
                content: [
                  '请基于“今天”生成朋友圈创作参考。',
                  `今天日期：${today.dateLabel}`,
                  today.holidayLabels.length ? `节假日/时令：${today.holidayLabels.join('、')}` : '节假日/时令：无',
                  `基础热点候选：${today.hotTopics.join('、')}`,
                  personaNames.length ? `角色名单：${personaNames.join('、')}` : '',
                  '输出 JSON 格式：{"hotTopics":["..."],"personaAngles":["..."]}',
                  '要求：hotTopics 给 6-10 条，必须是中文短语；personaAngles 给 3-6 条，描述角色可以发什么类型内容；避免政治、暴力、灾难细节。'
                ].filter(Boolean).join('\n')
              }
            ]
          })
        })
        if (response.ok) {
          const payload = await response.json()
          const parsed = extractJsonObjectFromText(extractChatTextContent(payload))
          if (parsed) {
            aiTopics = mergeUniqueTopics(Array.isArray((parsed as any).hotTopics) ? (parsed as any).hotTopics : [], 12)
            aiAngles = mergeUniqueTopics(Array.isArray((parsed as any).personaAngles) ? (parsed as any).personaAngles : [], 8)
          }
        }
      } catch (error) {
        console.warn('Failed to refresh moments trend with AI:', error)
      }
    }

    const mergedTopics = mergeUniqueTopics([...today.hotTopics, ...aiTopics], 12)
    if (aiTopics.length > 0 && mergedTopics.length > 0) source = 'mixed'
    if (aiTopics.length > 0 && today.hotTopics.length === 0) source = 'ai'

    momentsTrendContext.value = {
      ...today,
      hotTopics: mergedTopics.length > 0 ? mergedTopics : today.hotTopics,
      personaAngles: aiAngles,
      source,
      updatedAt: Date.now(),
    }
    saveMomentsTrendContext()
  } finally {
    isRefreshingMomentsTrend.value = false
  }
}

const ensureMomentsTrendContext = async (force = false) => {
  const currentDateKey = formatMomentsDateKey(new Date())
  const stale = Date.now() - Number(momentsTrendContext.value.updatedAt || 0) > MOMENTS_TREND_REFRESH_INTERVAL_MS
  if (force || !momentsTrendContext.value.dateKey || momentsTrendContext.value.dateKey !== currentDateKey || stale) {
    await refreshMomentsTrendContext(force)
    return
  }
  if (momentsTrendContext.value.hotTopics.length === 0) {
    momentsTrendContext.value = buildFallbackMomentsTrendContext(new Date())
    saveMomentsTrendContext()
  }
}

const buildMomentsTrendPromptContext = () => {
  const trend = momentsTrendContext.value
  const holidayText = trend.holidayLabels.length > 0 ? trend.holidayLabels.join('、') : '无'
  const topicText = trend.hotTopics.length > 0 ? trend.hotTopics.join('、') : '日常生活'
  const angles = trend.personaAngles.length > 0 ? trend.personaAngles.join('；') : '结合角色本身经历与情绪。'
  return [
    `日期：${trend.dateLabel || formatMomentsDateLabel(new Date())}`,
    `节假日/时令：${holidayText}`,
    `热点参考：${topicText}`,
    `角色表达角度：${angles}`,
  ].join('\n')
}

const buildFallbackMomentPost = (persona: Persona, score: number) => {
  const energetic = [
    '今天状态不错，准备认真营业。',
    '记录一下此刻心情，等你来互动。',
    '刚整理完手头的事，来刷一圈朋友圈。'
  ]
  const highInteraction = [
    '刚刚想到你，顺手来发条动态。',
    '今天又是想和你多聊几句的一天。',
    '忙完第一件事就是来看看你在不在。'
  ]
  const pool = score >= 6 ? highInteraction : energetic
  const seed = pool[Math.floor(Math.random() * pool.length)] || energetic[0]
  const trend = momentsTrendContext.value
  const holiday = trend.holidayLabels[Math.floor(Math.random() * Math.max(1, trend.holidayLabels.length))] || ''
  const topic = trend.hotTopics[Math.floor(Math.random() * Math.max(1, trend.hotTopics.length))] || ''
  const extra = holiday ? `今天是${holiday}，仪式感不能少。` : topic ? `最近也在关注${topic}。` : ''
  return normalizeMomentContent(`${seed}${extra ? ` ${extra}` : ''}`)
}

const buildFallbackMomentComment = (persona: Persona) => {
  const pool = ['这个动态我很喜欢。', '看到就想点赞。', '状态很好，继续保持。', '这条我先收藏了。']
  const topic = momentsTrendContext.value.hotTopics[Math.floor(Math.random() * Math.max(1, momentsTrendContext.value.hotTopics.length))] || ''
  const base = pool[Math.floor(Math.random() * pool.length)] || `${persona.name}来打卡。`
  return normalizeMomentContent(`${base}${topic ? ` ${topic}这个点子不错。` : ''}`)
}

const generatePersonaMomentTextWithAI = async (
  persona: Persona,
  mode: 'post' | 'comment',
  contextSeed: string,
  score = 0
) => {
  await ensureMomentsTrendContext(false)

  if (!isConnected.value) {
    return mode === 'post' ? buildFallbackMomentPost(persona, score) : buildFallbackMomentComment(persona)
  }

  const trendContext = buildMomentsTrendPromptContext()
  const prompt =
    mode === 'post'
      ? [
          `你是${persona.name}，请发一条中文朋友圈动态。`,
          '要求：口吻符合角色设定；输出 1-2 句，不要带引号，不要编号，不要解释。',
          `上下文：${contextSeed}`,
          `热点与节日上下文：\n${trendContext}`,
          '要求：内容尽量结合当天节假日或热点之一，但不要生硬堆砌话题。',
          score >= 6 ? '补充：你与用户互动频繁，语气可更亲近。' : '补充：保持自然轻松。'
        ].join('\n')
      : [
          `你是${persona.name}，请对下面这条朋友圈写一句中文评论。`,
          '要求：一句话，简短自然，不要解释。',
          `原动态：${contextSeed}`,
          `热点与节日上下文：\n${trendContext}`,
          '补充：评论可轻度呼应节日或热点，但核心要围绕原动态。'
        ].join('\n')

  try {
    const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model: apiSettings.value.modelName,
        stream: false,
        temperature: 0.8,
        max_tokens: mode === 'post' ? 120 : 80,
        messages: [
          { role: 'system', content: persona.systemPrompt || `你是${persona.name}` },
          { role: 'user', content: prompt }
        ]
      })
    })

    if (!response.ok) throw new Error(await readResponseErrorMessage(response))
    const data = await response.json()
    const generated = normalizeMomentContent(extractChatTextContent(data))
    if (!generated) {
      return mode === 'post' ? buildFallbackMomentPost(persona, score) : buildFallbackMomentComment(persona)
    }
    return generated
  } catch {
    return mode === 'post' ? buildFallbackMomentPost(persona, score) : buildFallbackMomentComment(persona)
  }
}

const createMomentPost = (
  author: { id: string; name: string; avatar: string },
  content: string,
  createdAt = Date.now()
): MomentPost => {
  return {
    id: createMomentId(),
    authorId: author.id,
    authorName: author.name,
    authorAvatar: author.avatar,
    content: normalizeMomentContent(content),
    createdAt,
    likedByUser: false,
    likedByPersonaIds: [],
    comments: []
  }
}

const getUserMomentAuthor = () => {
  return {
    id: 'user',
    name: userDisplayName.value || '你',
    avatar: userAvatarDisplay.value || USER_AVATAR_URL
  }
}

const createMomentComment = (
  author: { id: string; name: string; avatar: string },
  content: string
): MomentComment => {
  return {
    id: createMomentId(),
    authorId: author.id,
    authorName: author.name,
    authorAvatar: author.avatar,
    content: normalizeMomentContent(content),
    createdAt: Date.now()
  }
}

const appendMomentPost = (post: MomentPost) => {
  const next = [post, ...momentsPosts.value].sort((a, b) => b.createdAt - a.createdAt)
  momentsPosts.value = next.slice(0, MOMENTS_MAX_POSTS_IN_MEMORY)
}

const serializeMomentPostForStorage = (post: MomentPost, maxComments = MOMENTS_MAX_COMMENTS_IN_STORAGE) => {
  const safeComments = post.comments
    .slice(-maxComments)
    .map((comment) => ({
      id: String(comment.id || createMomentId()),
      authorId: String(comment.authorId || ''),
      content: normalizeMomentContent(comment.content || ''),
      createdAt: Number(comment.createdAt || Date.now())
    }))
    .filter((comment) => Boolean(comment.authorId) && Boolean(comment.content))

  return {
    id: String(post.id || createMomentId()),
    authorId: String(post.authorId || ''),
    content: normalizeMomentContent(post.content || ''),
    createdAt: Number(post.createdAt || Date.now()),
    likedByUser: Boolean(post.likedByUser),
    likedByPersonaIds: Array.from(new Set((post.likedByPersonaIds || []).map((id) => String(id)).filter(Boolean))),
    comments: safeComments
  }
}

const saveMomentsState = () => {
  const buildSnapshot = (postLimit: number, commentLimit: number) => {
    return {
      posts: momentsPosts.value
        .slice(0, postLimit)
        .map((post) => serializeMomentPostForStorage(post, commentLimit))
        .filter((post) => Boolean(post.authorId) && Boolean(post.content)),
      interactionScores: momentsInteractionScores.value,
      nextPostAt: momentsNextPostAt.value,
      lastViewedAt: momentsLastViewedAt.value
    }
  }

  const savePlan: Array<{ postLimit: number; commentLimit: number }> = [
    { postLimit: MOMENTS_MAX_POSTS_IN_STORAGE, commentLimit: MOMENTS_MAX_COMMENTS_IN_STORAGE },
    { postLimit: 50, commentLimit: 12 },
    { postLimit: 30, commentLimit: 8 },
    { postLimit: 20, commentLimit: 4 },
    { postLimit: 10, commentLimit: 0 }
  ]

  for (const step of savePlan) {
    try {
      const snapshot = buildSnapshot(step.postLimit, step.commentLimit)
      localStorage.setItem(MOMENTS_STORAGE_KEY, JSON.stringify(snapshot))
      return
    } catch (error) {
      console.warn('Failed to persist moments snapshot, retry with smaller payload.', error)
    }
  }

  try {
    localStorage.removeItem(MOMENTS_STORAGE_KEY)
  } catch {
    // ignore remove failure
  }
  if (showMomentsPanel.value) {
    momentsError.value = '朋友圈缓存已满，已自动清理历史缓存。'
  }
}

const loadMomentsState = () => {
  const raw = localStorage.getItem(MOMENTS_STORAGE_KEY)
  if (!raw) return

  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed?.posts)) {
      momentsPosts.value = parsed.posts
        .map((item: any) => {
          if (!item || typeof item !== 'object') return null
          const comments = Array.isArray(item.comments)
            ? item.comments
                .map((comment: any) => {
                  if (!comment || typeof comment !== 'object') return null
                  const content = normalizeMomentContent(String(comment.content || ''))
                  if (!content) return null
                  const commentAuthorId = String(comment.authorId || '')
                  const commentPersona = commentAuthorId && commentAuthorId !== 'user' ? getPersonaById(commentAuthorId) : null
                  return {
                    id: String(comment.id || createMomentId()),
                    authorId: commentAuthorId,
                    authorName:
                      commentAuthorId === 'user'
                        ? getUserMomentAuthor().name
                        : String(comment.authorName || commentPersona?.name || '未知'),
                    authorAvatar:
                      commentAuthorId === 'user'
                        ? getUserMomentAuthor().avatar
                        : String(comment.authorAvatar || commentPersona?.avatar || USER_AVATAR_URL),
                    content,
                    createdAt: Number(comment.createdAt || Date.now())
                  } as MomentComment
                })
                .filter(Boolean) as MomentComment[]
            : []

          const content = normalizeMomentContent(String(item.content || ''))
          if (!content) return null
          const authorId = String(item.authorId || '')
          const persona = authorId && authorId !== 'user' ? getPersonaById(authorId) : null
          return {
            id: String(item.id || createMomentId()),
            authorId,
            authorName:
              authorId === 'user'
                ? getUserMomentAuthor().name
                : String(item.authorName || persona?.name || '未知'),
            authorAvatar:
              authorId === 'user'
                ? getUserMomentAuthor().avatar
                : String(item.authorAvatar || persona?.avatar || USER_AVATAR_URL),
            content,
            createdAt: Number(item.createdAt || Date.now()),
            likedByUser: Boolean(item.likedByUser),
            likedByPersonaIds: Array.isArray(item.likedByPersonaIds)
              ? item.likedByPersonaIds.map((id: any) => String(id)).filter(Boolean)
              : [],
            comments
          } as MomentPost
        })
        .filter(Boolean) as MomentPost[]
    }

    if (parsed?.interactionScores && typeof parsed.interactionScores === 'object') {
      momentsInteractionScores.value = Object.fromEntries(
        Object.entries(parsed.interactionScores)
          .map(([key, value]) => [String(key), clampNumber(Number(value) || 0, 0, 999)])
      )
    }

    if (parsed?.nextPostAt && typeof parsed.nextPostAt === 'object') {
      momentsNextPostAt.value = Object.fromEntries(
        Object.entries(parsed.nextPostAt)
          .map(([key, value]) => [String(key), Number(value) || 0])
          .filter(([, value]) => value > 0)
      )
    }

    momentsLastViewedAt.value = Number(parsed?.lastViewedAt || 0)
  } catch (error) {
    console.error('Failed to load moments state:', error)
  }
}

const markPersonaInteraction = (personaId: string, delta: number) => {
  if (!personaId || personaId === 'user') return
  const current = getPersonaInteractionScore(personaId)
  const next = clampNumber(current + delta, 0, 999)
  momentsInteractionScores.value[personaId] = next

  if (next >= 6) {
    const scheduled = momentsNextPostAt.value[personaId] || 0
    const soonest = Date.now() + randomBetween(90 * 60 * 1000, 4 * 60 * 60 * 1000)
    if (!scheduled || scheduled > soonest) {
      momentsNextPostAt.value[personaId] = soonest
    }
  }
}

const syncMomentsDataWithPersonas = () => {
  const personaMap = new Map(personas.value.map((persona) => [persona.id, persona]))

  momentsPosts.value = momentsPosts.value
    .filter((post) => post.authorId === 'user' || personaMap.has(post.authorId))
    .map((post) => {
      const author = post.authorId === 'user' ? null : personaMap.get(post.authorId)
      const likedByPersonaIds = Array.from(
        new Set(
          post.likedByPersonaIds.filter((id) => personaMap.has(id))
        )
      )
      const comments = post.comments
        .filter((comment) => comment.authorId === 'user' || personaMap.has(comment.authorId))
        .map((comment) => {
          if (comment.authorId === 'user') {
            return {
              ...comment,
              authorName: getUserMomentAuthor().name,
              authorAvatar: getUserMomentAuthor().avatar
            }
          }
          const commentAuthor = personaMap.get(comment.authorId)!
          return {
            ...comment,
            authorName: commentAuthor.name,
            authorAvatar: commentAuthor.avatar
          }
        })

      if (!author) {
        return {
          ...post,
          authorName: getUserMomentAuthor().name,
          authorAvatar: getUserMomentAuthor().avatar,
          likedByPersonaIds,
          comments
        }
      }

      return {
        ...post,
        authorName: author.name,
        authorAvatar: author.avatar,
        likedByPersonaIds,
        comments
      }
    })

  momentsInteractionScores.value = Object.fromEntries(
    Object.entries(momentsInteractionScores.value).filter(([personaId]) => personaMap.has(personaId))
  )
  momentsNextPostAt.value = Object.fromEntries(
    Object.entries(momentsNextPostAt.value).filter(([personaId]) => personaMap.has(personaId))
  )
}

const applyAiLikesToPost = (post: MomentPost, minLike = 1, maxLike = 5) => {
  const candidates = personas.value.filter((persona) => persona.id !== post.authorId)
  if (candidates.length === 0) return

  const weighted = shuffleArray(candidates).sort((a, b) => getPersonaInteractionScore(b.id) - getPersonaInteractionScore(a.id))
  const pickCount = clampNumber(randomBetween(minLike, maxLike), 0, weighted.length)
  post.likedByPersonaIds = Array.from(new Set(weighted.slice(0, pickCount).map((item) => item.id)))
}

const addAiCommentToPost = async (post: MomentPost, persona: Persona) => {
  const text = await generatePersonaMomentTextWithAI(persona, 'comment', post.content, getPersonaInteractionScore(persona.id))
  if (!text.trim()) return
  post.comments.push(
    createMomentComment(
      { id: persona.id, name: persona.name, avatar: persona.avatar },
      text
    )
  )
}

const addAiMutualInteractionsToPost = async (
  post: MomentPost,
  options: { minLikes?: number; maxLikes?: number; minComments?: number; maxComments?: number } = {}
) => {
  const candidates = shuffleArray(personas.value.filter((persona) => persona.id !== post.authorId && persona.id !== 'user'))
  if (candidates.length === 0) return

  const minLikes = clampNumber(Number(options.minLikes ?? 1), 0, candidates.length)
  const maxLikes = clampNumber(Number(options.maxLikes ?? 4), minLikes, candidates.length)
  const likeCount = clampNumber(randomBetween(minLikes, maxLikes), 0, candidates.length)
  const likeIds = candidates.slice(0, likeCount).map((persona) => persona.id)
  post.likedByPersonaIds = Array.from(new Set([...post.likedByPersonaIds, ...likeIds]))
  likeIds.forEach((personaId) => markPersonaInteraction(personaId, 1))

  const minComments = clampNumber(Number(options.minComments ?? 0), 0, candidates.length)
  const maxComments = clampNumber(Number(options.maxComments ?? 2), minComments, candidates.length)
  const commentCount = clampNumber(randomBetween(minComments, maxComments), 0, candidates.length)
  const commentSpeakers = candidates
    .sort((a, b) => getPersonaInteractionScore(b.id) - getPersonaInteractionScore(a.id))
    .slice(0, commentCount)

  for (const speaker of commentSpeakers) {
    await addAiCommentToPost(post, speaker)
    markPersonaInteraction(speaker.id, 1)
  }
}

let momentsAutoPublishing = false

const createPersonaAutoPost = async (persona: Persona, createdAt = Date.now()) => {
  const score = getPersonaInteractionScore(persona.id)
  const contextSeed = `当前角色：${persona.name}；最近互动分：${score}`
  const text = await generatePersonaMomentTextWithAI(persona, 'post', contextSeed, score)
  const post = createMomentPost(
    { id: persona.id, name: persona.name, avatar: persona.avatar },
    text,
    createdAt
  )
  applyAiLikesToPost(post, 0, 4)
  await addAiMutualInteractionsToPost(post, { minLikes: 1, maxLikes: 5, minComments: 1, maxComments: 3 })
  appendMomentPost(post)
  return post
}

const maybeAutoPublishMoments = async (force = false) => {
  if (momentsAutoPublishing) return
  if (!momentsHydrated.value) return

  momentsAutoPublishing = true
  try {
    const now = Date.now()
    await ensureMomentsTrendContext(force)
    ensureMomentsSchedule(now)

    const aiPersonas = personas.value.filter((item) => item.id && item.id !== 'user')
    if (aiPersonas.length === 0) return

    let duePersonas = aiPersonas.filter((persona) => force || now >= Number(momentsNextPostAt.value[persona.id] || 0))
    if (duePersonas.length === 0 && force) {
      duePersonas = shuffleArray(aiPersonas).slice(0, 1)
    }
    if (duePersonas.length === 0) return

    duePersonas = duePersonas
      .sort((a, b) => getPersonaInteractionScore(b.id) - getPersonaInteractionScore(a.id))
      .slice(0, force ? 3 : 1)

    for (const persona of duePersonas) {
      const backdatedTime = Date.now() - randomBetween(0, 6 * 60 * 1000)
      await createPersonaAutoPost(persona, backdatedTime)
      refreshPersonaMomentSchedule(persona.id)
    }

    saveMomentsState()
  } finally {
    momentsAutoPublishing = false
  }
}

const seedMomentsIfEmpty = async () => {
  if (momentsPosts.value.length > 0) return
  const aiPersonas = shuffleArray(personas.value.filter((persona) => persona.id !== 'user')).slice(0, 3)
  for (let i = 0; i < aiPersonas.length; i += 1) {
    const persona = aiPersonas[i]
    const createdAt = Date.now() - randomBetween((i + 1) * 25 * 60 * 1000, (i + 1) * 90 * 60 * 1000)
    await createPersonaAutoPost(persona, createdAt)
    refreshPersonaMomentSchedule(persona.id, Date.now(), true)
  }
  momentsLastViewedAt.value = Date.now()
  saveMomentsState()
}

const scheduleMomentsTicker = () => {
  if (momentsTimer) clearTimeout(momentsTimer)
  const delay = randomBetween(MOMENTS_TICK_MIN_DELAY_MS, MOMENTS_TICK_MAX_DELAY_MS)
  momentsTimer = setTimeout(async () => {
    await maybeAutoPublishMoments(false)
    scheduleMomentsTicker()
  }, delay)
}

const stopMomentsTicker = () => {
  if (!momentsTimer) return
  clearTimeout(momentsTimer)
  momentsTimer = null
}

const initializeMoments = async () => {
  if (momentsHydrated.value) return
  await ensureMomentsTrendContext(false)
  loadMomentsState()
  loadGroupChatsState()
  syncMomentsDataWithPersonas()
  syncGroupChatsWithPersonas()
  ensureMomentsSchedule()
  await seedMomentsIfEmpty()
  momentsHydrated.value = true
  saveMomentsState()
  ensureSelectedGroupChatReady()
  saveGroupChatsState()
  scheduleMomentsTicker()
}

const openMomentsPanel = async () => {
  if (!momentsHydrated.value) {
    await initializeMoments()
  }
  await ensureMomentsTrendContext(false)
  ensureSelectedGroupChatReady()
  showMomentsPanel.value = true
  momentsInfo.value = ''
  momentsError.value = ''
  groupChatInfo.value = ''
  groupChatError.value = ''
  momentsLastViewedAt.value = Date.now()
  saveMomentsState()
  saveGroupChatsState()
  await maybeAutoPublishMoments(false)
}

const closeMomentsPanel = () => {
  showMomentsPanel.value = false
  momentsLastViewedAt.value = Date.now()
  saveMomentsState()
  saveGroupChatsState()
}

const refreshMomentsFeed = async () => {
  await ensureMomentsTrendContext(true)
  await maybeAutoPublishMoments(true)
}

const publishMoment = async () => {
  if (isPublishingMoment.value) return
  momentsInfo.value = ''
  momentsError.value = ''

  const content = normalizeMomentContent(momentsComposerText.value)
  if (!content) {
    momentsError.value = '请输入朋友圈内容后再发布。'
    return
  }

  try {
    guardUsagePolicyContent(content, 'publish')
  } catch (error) {
    if (isUsagePolicyViolationError(error)) {
      momentsError.value = error.message
      openUsagePolicyDialog(error.message)
      return
    }
    throw error
  }

  isPublishingMoment.value = true
  try {
    const post = createMomentPost(getUserMomentAuthor(), content)
    appendMomentPost(post)
    momentsComposerText.value = ''

    const aiPersonas = shuffleArray(personas.value.filter((persona) => persona.id !== 'user'))
    const likeCount = clampNumber(randomBetween(2, 6), 0, aiPersonas.length)
    post.likedByPersonaIds = aiPersonas.slice(0, likeCount).map((item) => item.id)
    post.likedByPersonaIds.forEach((personaId) => markPersonaInteraction(personaId, 1))

    const highInteractionPersonas = aiPersonas
      .filter((persona) => getPersonaInteractionScore(persona.id) >= 6)
      .slice(0, 2)
    for (const persona of highInteractionPersonas) {
      if (Math.random() < 0.8) {
        await addAiCommentToPost(post, persona)
        markPersonaInteraction(persona.id, 1)
      }
    }
    if (post.comments.length === 0 && aiPersonas.length > 0 && Math.random() < 0.5) {
      await addAiCommentToPost(post, aiPersonas[0])
      markPersonaInteraction(aiPersonas[0].id, 1)
    }

    momentsInfo.value = '朋友圈发布成功，AI好友已开始互动。'
    saveMomentsState()
  } finally {
    isPublishingMoment.value = false
  }
}

const toggleMomentLike = async (post: MomentPost) => {
  post.likedByUser = !post.likedByUser
  if (post.authorId !== 'user') {
    markPersonaInteraction(post.authorId, post.likedByUser ? 1 : -1)
    if (post.likedByUser) {
      const authorPersona = getPersonaById(post.authorId)
      if (authorPersona && Math.random() < 0.35) {
        const reply = await generatePersonaMomentTextWithAI(
          authorPersona,
          'comment',
          `用户给你的朋友圈点了赞。原动态：${post.content}`,
          getPersonaInteractionScore(authorPersona.id)
        )
        if (reply.trim()) {
          post.comments.push(
            createMomentComment(
              { id: authorPersona.id, name: authorPersona.name, avatar: authorPersona.avatar },
              reply
            )
          )
          markPersonaInteraction(authorPersona.id, 1)
        }
      }
    }
  }
  saveMomentsState()
}

const removeMomentPost = (postId: string) => {
  const target = momentsPosts.value.find((item) => item.id === postId)
  if (!target) return
  if (target.authorId !== 'user') return
  if (!confirm('确认删除这条朋友圈吗？')) return

  momentsPosts.value = momentsPosts.value.filter((item) => item.id !== postId)
  delete momentsCommentDrafts.value[postId]
  momentsInfo.value = '已删除该条朋友圈。'
  momentsError.value = ''
  saveMomentsState()
}

const submitMomentComment = async (post: MomentPost) => {
  const draft = normalizeMomentContent(momentsCommentDrafts.value[post.id] || '')
  if (!draft) return

  try {
    guardUsagePolicyContent(draft, 'publish')
  } catch (error) {
    if (isUsagePolicyViolationError(error)) {
      momentsError.value = error.message
      openUsagePolicyDialog(error.message)
      return
    }
    throw error
  }

  post.comments.push(
    createMomentComment(getUserMomentAuthor(), draft)
  )
  momentsCommentDrafts.value[post.id] = ''

  if (post.authorId !== 'user') {
    markPersonaInteraction(post.authorId, 2)
  }

  const authorPersona = personas.value.find((item) => item.id === post.authorId)
  if (authorPersona && Math.random() < 0.75) {
    await addAiCommentToPost(post, authorPersona)
    markPersonaInteraction(authorPersona.id, 1)
  } else {
    const highPersona = personas.value
      .filter((item) => item.id !== 'user' && getPersonaInteractionScore(item.id) >= 6)
      .sort((a, b) => getPersonaInteractionScore(b.id) - getPersonaInteractionScore(a.id))[0]
    if (highPersona && Math.random() < 0.5) {
      await addAiCommentToPost(post, highPersona)
      markPersonaInteraction(highPersona.id, 1)
    }
  }
  saveMomentsState()
}

const appendGroupChatMessage = (room: GroupChatRoom, message: GroupChatMessage) => {
  room.messages.push(message)
  if (room.messages.length > GROUP_CHAT_MAX_MESSAGES) {
    room.messages = room.messages.slice(-GROUP_CHAT_MAX_MESSAGES)
  }
  room.updatedAt = Math.max(Number(room.updatedAt || 0), Number(message.createdAt || 0), Date.now())
}

const getGroupChatRoomById = (roomId: string) => {
  return groupChats.value.find((item) => item.id === roomId && !item.dissolved) || null
}

const getGroupMemberDisplayName = (room: GroupChatRoom, memberId: string) => {
  if (memberId === 'user') return userDisplayName.value || '你'
  return room.members.find((member) => member.id === memberId)?.name || '管理员'
}

const ensureGroupRoomEditorState = (room: GroupChatRoom) => {
  if (!groupRenameDraftByRoomId.value[room.id]) {
    groupRenameDraftByRoomId.value[room.id] = room.name
  }
  if (groupAnnouncementDraftByRoomId.value[room.id] === undefined) {
    groupAnnouncementDraftByRoomId.value[room.id] = room.announcement || ''
  }
  if (groupRulesDraftByRoomId.value[room.id] === undefined) {
    groupRulesDraftByRoomId.value[room.id] = room.rules || ''
  }
  if (groupAddMemberDraftByRoomId.value[room.id] === undefined) {
    groupAddMemberDraftByRoomId.value[room.id] = ''
  }

  const selectedTargetId = String(groupAdminTransferTargetByRoomId.value[room.id] || '')
  const selectedTarget = room.members.find((member) => member.id === selectedTargetId && member.isAi)
  if (!selectedTarget) {
    const aiAdmin = room.members.find((member) => member.isAi && member.isAdmin)
    const firstAi = room.members.find((member) => member.isAi)
    groupAdminTransferTargetByRoomId.value[room.id] = aiAdmin?.id || firstAi?.id || ''
  }
}

const resolveGroupAdminActorId = (room: GroupChatRoom): string | null => {
  const userMember = room.members.find((member) => member.id === 'user')
  if (userMember && !userMember.isAdmin) {
    userMember.isAdmin = true
  }
  const admins = room.members.filter((member) => member.isAdmin)
  if (admins.length === 0) return null

  let actorId = String(groupAdminActorByRoomId.value[room.id] || '')
  if (!actorId) {
    actorId = admins.some((member) => member.id === 'user') ? 'user' : admins[0].id
  }
  if (!admins.some((member) => member.id === actorId)) {
    actorId = admins.some((member) => member.id === 'user') ? 'user' : admins[0].id
  }
  groupAdminActorByRoomId.value[room.id] = actorId
  return actorId
}

const serializeGroupMessageForStorage = (msg: GroupChatMessage) => {
  const safeType: GroupChatMessageType =
    msg.type === 'audio' || msg.type === 'image' || msg.type === 'video' || msg.type === 'emoji' || msg.type === 'system'
      ? msg.type
      : 'text'
  const mediaUrl = String(msg.mediaUrl || '')
  const persistableMediaUrl = mediaUrl.startsWith('blob:') ? '' : mediaUrl.slice(0, 450000)
  return {
    id: String(msg.id || createGroupChatMessageId()),
    senderId: String(msg.senderId || 'system'),
    senderName: String(msg.senderName || '系统'),
    senderAvatar: String(msg.senderAvatar || ''),
    type: safeType,
    content: normalizeGroupMessageContent(msg.content || '', 260),
    mediaUrl: persistableMediaUrl,
    createdAt: Number(msg.createdAt || Date.now()),
  }
}

const serializeGroupRoomForStorage = (room: GroupChatRoom) => {
  const uniqueMembers = Array.from(new Map(
    room.members
      .map((member) => ({
        id: String(member.id || ''),
        name: String(member.name || ''),
        avatar: String(member.avatar || ''),
        isAi: Boolean(member.isAi),
        isAdmin: Boolean(member.isAdmin),
      }))
      .filter((member) => Boolean(member.id))
      .map((member) => [member.id, member])
  ).values())

  return {
    id: String(room.id || createGroupChatId()),
    name: normalizeGroupName(room.name || '未命名群聊'),
    avatar: String(room.avatar || ''),
    members: uniqueMembers,
    messages: room.messages.slice(-GROUP_CHAT_MAX_MESSAGES_IN_STORAGE).map((msg) => serializeGroupMessageForStorage(msg)),
    replyMode: normalizeGroupReplyMode((room as any).replyMode),
    announcement: normalizeGroupAnnouncement(String((room as any).announcement || '')),
    rules: normalizeGroupRules(String((room as any).rules || '')),
    mutedByUser: Boolean(room.mutedByUser),
    dissolved: Boolean(room.dissolved),
    createdAt: Number(room.createdAt || Date.now()),
    updatedAt: Number(room.updatedAt || Date.now()),
  }
}

const saveGroupChatsState = () => {
  const payload = {
    rooms: groupChats.value
      .filter((room) => !room.dissolved)
      .map((room) => serializeGroupRoomForStorage(room))
      .slice(0, 30),
    selectedGroupChatId: String(selectedGroupChatId.value || ''),
    panelTab: momentsPanelTab.value,
    pendingImageConsent:
      groupImageConsentPending.value && !getGroupChatRoomById(groupImageConsentPending.value.groupId)
        ? null
        : groupImageConsentPending.value,
  }
  try {
    localStorage.setItem(GROUP_CHAT_STORAGE_KEY, JSON.stringify(payload))
  } catch (error) {
    console.warn('Failed to save group chat state:', error)
  }
}

const loadGroupChatsState = () => {
  const raw = localStorage.getItem(GROUP_CHAT_STORAGE_KEY)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return
    const rooms = Array.isArray((parsed as any).rooms) ? (parsed as any).rooms : []
    groupChats.value = rooms
      .map((item: any) => {
        if (!item || typeof item !== 'object') return null
        const name = normalizeGroupName(String(item.name || ''))
        if (!name) return null
        const members = Array.isArray(item.members)
          ? item.members
              .map((member: any) => {
                if (!member || typeof member !== 'object') return null
                const id = String(member.id || '')
                if (!id) return null
                return {
                  id,
                  name: String(member.name || (id === 'user' ? userDisplayName.value || '你' : '成员')),
                  avatar: String(member.avatar || (id === 'user' ? userAvatarDisplay.value || USER_AVATAR_URL : '')),
                  isAi: id !== 'user',
                  isAdmin: Boolean(member.isAdmin),
                } as GroupChatMember
              })
              .filter(Boolean) as GroupChatMember[]
          : []

        const messages = Array.isArray(item.messages)
          ? item.messages
              .map((msg: any) => {
                if (!msg || typeof msg !== 'object') return null
                const type = ['text', 'emoji', 'audio', 'image', 'video', 'system'].includes(String(msg.type))
                  ? (String(msg.type) as GroupChatMessageType)
                  : 'text'
                return {
                  id: String(msg.id || createGroupChatMessageId()),
                  senderId: String(msg.senderId || 'system'),
                  senderName: String(msg.senderName || '系统'),
                  senderAvatar: String(msg.senderAvatar || ''),
                  type,
                  content: normalizeGroupMessageContent(String(msg.content || ''), 260),
                  mediaUrl: String(msg.mediaUrl || ''),
                  createdAt: Number(msg.createdAt || Date.now()),
                } as GroupChatMessage
              })
              .filter(Boolean) as GroupChatMessage[]
          : []

        return {
          id: String(item.id || createGroupChatId()),
          name,
          avatar: String(item.avatar || buildDefaultGroupAvatar(name)),
          members,
          messages,
          replyMode: normalizeGroupReplyMode(item.replyMode),
          announcement: normalizeGroupAnnouncement(String(item.announcement || '')),
          rules: normalizeGroupRules(String(item.rules || '')),
          mutedByUser: Boolean(item.mutedByUser),
          dissolved: Boolean(item.dissolved),
          createdAt: Number(item.createdAt || Date.now()),
          updatedAt: Number(item.updatedAt || Date.now()),
        } as GroupChatRoom
      })
      .filter(Boolean) as GroupChatRoom[]

    for (const room of groupChats.value) {
      ensureGroupRoomDefaults(room)
      ensureGroupRoomEditorState(room)
    }

    const selectedId = String((parsed as any).selectedGroupChatId || '')
    selectedGroupChatId.value = selectedId
    momentsPanelTab.value = (parsed as any).panelTab === 'group' ? 'group' : momentsPanelTab.value

    const pending = (parsed as any).pendingImageConsent
    if (pending && typeof pending === 'object') {
      groupImageConsentPending.value = {
        id: String(pending.id || createMomentId()),
        groupId: String(pending.groupId || ''),
        speakerId: String(pending.speakerId || ''),
        speakerName: String(pending.speakerName || 'AI成员'),
        prompt: normalizeGroupMessageContent(String(pending.prompt || ''), 260),
        createdAt: Number(pending.createdAt || Date.now()),
      }
    } else {
      groupImageConsentPending.value = null
    }
  } catch (error) {
    console.error('Failed to load group chat state:', error)
  }
}

const syncGroupChatsWithPersonas = () => {
  const personaMap = new Map(personas.value.filter((persona) => persona.id !== 'user').map((persona) => [persona.id, persona]))
  const userMember = buildUserGroupMember()

  groupChats.value = groupChats.value
    .map((room) => {
      const memberMap = new Map<string, GroupChatMember>()
      memberMap.set('user', { ...userMember, isAdmin: true })

      for (const member of room.members) {
        if (member.id === 'user') continue
        const persona = personaMap.get(member.id)
        if (!persona) continue
        memberMap.set(member.id, {
          id: persona.id,
          name: persona.name,
          avatar: persona.avatar,
          isAi: true,
          isAdmin: Boolean(member.isAdmin),
        })
      }

      const members = Array.from(memberMap.values())
      if (!members.some((member) => member.isAdmin)) {
        members[0].isAdmin = true
      }

      const messages = room.messages
        .map((msg) => {
          if (msg.senderId === 'user') {
            return { ...msg, senderName: userMember.name, senderAvatar: userMember.avatar }
          }
          const persona = personaMap.get(msg.senderId)
          if (!persona && msg.senderId !== 'system') {
            return null
          }
          if (persona) {
            return { ...msg, senderName: persona.name, senderAvatar: persona.avatar }
          }
          return msg
        })
        .filter(Boolean) as GroupChatMessage[]

      return ensureGroupRoomDefaults({
        ...room,
        members,
        messages,
        avatar: room.avatar || buildDefaultGroupAvatar(room.name),
        updatedAt: Number(room.updatedAt || Date.now()),
      } as GroupChatRoom)
    })
    .filter((room) => !room.dissolved)

  if (selectedGroupChatId.value && !groupChats.value.some((room) => room.id === selectedGroupChatId.value)) {
    selectedGroupChatId.value = groupChats.value[0]?.id || ''
  }

  if (groupImageConsentPending.value) {
    const pending = groupImageConsentPending.value
    const room = getGroupChatRoomById(pending.groupId)
    if (!room || !room.members.some((member) => member.id === pending.speakerId)) {
      groupImageConsentPending.value = null
    }
  }

  groupDraftMemberIds.value = groupDraftMemberIds.value.filter((id) => personaMap.has(id))
  groupDraftAiAdminIds.value = groupDraftAiAdminIds.value.filter((id) => groupDraftMemberIds.value.includes(id))

  for (const room of groupChats.value) {
    ensureGroupRoomEditorState(room)
  }

  const activeRoomIdSet = new Set(groupChats.value.map((room) => room.id))
  const pruneDraftMap = (map: Record<string, string>) => {
    Object.keys(map).forEach((roomId) => {
      if (!activeRoomIdSet.has(roomId)) {
        delete map[roomId]
      }
    })
  }
  pruneDraftMap(groupRenameDraftByRoomId.value)
  pruneDraftMap(groupAnnouncementDraftByRoomId.value)
  pruneDraftMap(groupRulesDraftByRoomId.value)
  pruneDraftMap(groupAdminActorByRoomId.value)
  pruneDraftMap(groupAdminTransferTargetByRoomId.value)
  pruneDraftMap(groupAddMemberDraftByRoomId.value)
}

const ensureSelectedGroupChatReady = () => {
  if (!selectedGroupChatId.value && groupChatsSorted.value.length > 0) {
    selectedGroupChatId.value = groupChatsSorted.value[0].id
  }
  if (selectedGroupChat.value) {
    ensureGroupRoomDefaults(selectedGroupChat.value)
    ensureGroupRoomEditorState(selectedGroupChat.value)
    resolveGroupAdminActorId(selectedGroupChat.value)
  }
}

const createGroupChat = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''

  const groupName = normalizeGroupName(groupDraftName.value)
  if (!groupName) {
    groupChatError.value = '请填写群名称。'
    return
  }

  const selectedIds = Array.from(new Set(groupDraftMemberIds.value.filter(Boolean)))
  if (selectedIds.length === 0) {
    groupChatError.value = '请至少选择 1 个 AI 成员。'
    return
  }

  const personaMap = new Map(groupSelectableAiMembers.value.map((persona) => [persona.id, persona]))
  const members: GroupChatMember[] = [buildUserGroupMember()]
  const aiAdminIdSet = new Set(groupDraftAiAdminIds.value.filter((id) => selectedIds.includes(id)))

  for (const personaId of selectedIds) {
    const persona = personaMap.get(personaId)
    if (!persona) continue
    members.push(buildPersonaGroupMember(persona, aiAdminIdSet.has(persona.id)))
  }

  if (members.length <= 1) {
    groupChatError.value = '成员列表为空，请重新选择。'
    return
  }

  const now = Date.now()
  const room: GroupChatRoom = ensureGroupRoomDefaults({
    id: createGroupChatId(),
    name: groupName,
    avatar: groupDraftAvatar.value.trim() || buildDefaultGroupAvatar(groupName),
    members,
    messages: [],
    replyMode: 'normal',
    announcement: '',
    rules: '',
    mutedByUser: false,
    dissolved: false,
    createdAt: now,
    updatedAt: now,
  })

  const adminNames = room.members.filter((member) => member.isAdmin).map((member) => member.name).join('、')
  appendGroupChatMessage(
    room,
    buildGroupSystemMessage(
      isChineseLocale.value
        ? `群聊已创建。管理员：${adminNames || defaultUserName()}；用户保留最终管理权限。`
        : `Group created. Admins: ${adminNames || defaultUserName()}; the user keeps final management authority.`,
      now
    )
  )

  groupChats.value = [room, ...groupChats.value]
  selectedGroupChatId.value = room.id
  groupRenameDraftByRoomId.value[room.id] = room.name
  groupAnnouncementDraftByRoomId.value[room.id] = room.announcement
  groupRulesDraftByRoomId.value[room.id] = room.rules
  groupAdminActorByRoomId.value[room.id] = 'user'
  groupAdminTransferTargetByRoomId.value[room.id] = room.members.find((member) => member.isAi && member.isAdmin)?.id || room.members.find((member) => member.isAi)?.id || ''
  groupAddMemberDraftByRoomId.value[room.id] = ''

  groupDraftName.value = ''
  groupDraftAvatar.value = ''
  groupDraftMemberIds.value = []
  groupDraftAiAdminIds.value = []

  groupChatInfo.value = `群聊《${room.name}》创建成功。`
  saveGroupChatsState()
}

const selectGroupChat = (roomId: string) => {
  selectedGroupChatId.value = roomId
  const room = getGroupChatRoomById(roomId)
  if (!room) return
  ensureGroupRoomDefaults(room)
  ensureGroupRoomEditorState(room)
  resolveGroupAdminActorId(room)
  showGroupEmojiPanel.value = false
  groupChatInfo.value = ''
  groupChatError.value = ''
}

const toggleGroupChatMute = (room: GroupChatRoom) => {
  room.mutedByUser = !room.mutedByUser
  appendGroupChatMessage(
    room,
    buildGroupSystemMessage(room.mutedByUser ? '用户已屏蔽该群消息。' : '用户已恢复接收该群消息。')
  )
  groupChatInfo.value = room.mutedByUser ? '已屏蔽该群消息。' : '已恢复该群消息。'
  groupChatError.value = ''
  saveGroupChatsState()
}

const renameSelectedGroupChat = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }

  const nextName = normalizeGroupName(groupRenameDraftByRoomId.value[room.id] || room.name)
  if (!nextName) {
    groupChatError.value = '群名称不能为空。'
    return
  }
  if (nextName === room.name) {
    groupChatInfo.value = '群名称未变化。'
    return
  }

  const actorName = getGroupMemberDisplayName(room, actorId)
  const prev = room.name
  room.name = nextName
  room.updatedAt = Date.now()
  appendGroupChatMessage(room, buildGroupSystemMessage(`${actorName} 将群名从「${prev}」修改为「${nextName}」。`))
  groupChatInfo.value = '群名已更新。'
  saveGroupChatsState()
}

const removeMemberFromGroupRoom = (room: GroupChatRoom, memberId: string, actorName: string, reason = '移出群聊') => {
  const target = room.members.find((member) => member.id === memberId)
  if (!target || target.id === 'user') return false

  room.members = room.members.filter((member) => member.id !== memberId)
  appendGroupChatMessage(room, buildGroupSystemMessage(`${actorName} 已将 ${target.name} ${reason}。`))

  if (groupImageConsentPending.value && groupImageConsentPending.value.groupId === room.id && groupImageConsentPending.value.speakerId === memberId) {
    groupImageConsentPending.value = null
  }

  if (!room.members.some((member) => member.isAdmin)) {
    room.members[0].isAdmin = true
  }
  room.updatedAt = Date.now()
  ensureGroupRoomEditorState(room)
  return true
}

const kickMemberFromSelectedGroup = (memberId: string) => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }
  const actorName = getGroupMemberDisplayName(room, actorId)
  const target = room.members.find((member) => member.id === memberId)
  if (!target || target.id === 'user') return

  if (target.isAdmin && room.members.filter((member) => member.isAdmin).length <= 1) {
    groupChatError.value = '至少需要保留 1 位管理员。'
    return
  }

  if (!confirm(`确认将 ${target.name} 移出群聊吗？`)) return
  const removed = removeMemberFromGroupRoom(room, memberId, actorName)
  if (!removed) return
  groupChatInfo.value = `${target.name} 已移出群聊。`
  saveGroupChatsState()
}

const addMemberToSelectedGroup = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }

  const targetId = String(groupAddMemberDraftByRoomId.value[room.id] || '')
  if (!targetId) {
    groupChatError.value = '请先选择要添加的成员。'
    return
  }
  if (room.members.some((member) => member.id === targetId)) {
    groupChatError.value = '该成员已在群内。'
    groupAddMemberDraftByRoomId.value[room.id] = ''
    return
  }

  const persona = groupSelectableAiMembers.value.find((item) => item.id === targetId)
  if (!persona) {
    groupChatError.value = '该角色不存在或已被删除。'
    groupAddMemberDraftByRoomId.value[room.id] = ''
    return
  }

  room.members = [...room.members, buildPersonaGroupMember(persona, false)]
  room.updatedAt = Date.now()

  const actorName = getGroupMemberDisplayName(room, actorId)
  appendGroupChatMessage(room, buildGroupSystemMessage(`${actorName} 邀请 ${persona.name} 加入群聊。`))
  groupAddMemberDraftByRoomId.value[room.id] = ''
  ensureGroupRoomEditorState(room)
  groupChatInfo.value = `${persona.name} 已加入群聊。`
  saveGroupChatsState()
}

const dissolveSelectedGroupChat = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }
  const actorName = getGroupMemberDisplayName(room, actorId)
  if (!confirm(`确认解散群聊「${room.name}」吗？`)) return

  groupChats.value = groupChats.value.filter((item) => item.id !== room.id)
  if (groupImageConsentPending.value?.groupId === room.id) {
    groupImageConsentPending.value = null
  }
  delete groupRenameDraftByRoomId.value[room.id]
  delete groupAnnouncementDraftByRoomId.value[room.id]
  delete groupRulesDraftByRoomId.value[room.id]
  delete groupAdminActorByRoomId.value[room.id]
  delete groupAdminTransferTargetByRoomId.value[room.id]
  delete groupAddMemberDraftByRoomId.value[room.id]
  selectedGroupChatId.value = groupChatsSorted.value[0]?.id || ''
  groupChatInfo.value = `${actorName} 已解散群聊。`
  saveGroupChatsState()
}

const changeSelectedGroupReplyMode = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return
  const nextMode = normalizeGroupReplyMode(room.replyMode)
  room.replyMode = nextMode
  room.updatedAt = Date.now()
  const actorId = resolveGroupAdminActorId(room)
  const actorName = actorId ? getGroupMemberDisplayName(room, actorId) : (userDisplayName.value || defaultUserName())
  appendGroupChatMessage(room, buildGroupSystemMessage(`${actorName} 将群聊 AI 回复模式设置为「${getGroupReplyModeLabel(nextMode)}」。`))
  groupChatInfo.value = `已切换为 ${getGroupReplyModeLabel(nextMode)} 模式。`
  saveGroupChatsState()
}

const saveSelectedGroupAnnouncement = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }
  const draft = normalizeGroupAnnouncement(groupAnnouncementDraftByRoomId.value[room.id] || '')
  if (draft === room.announcement) {
    groupChatInfo.value = '群公告未变化。'
    return
  }

  room.announcement = draft
  groupAnnouncementDraftByRoomId.value[room.id] = draft
  room.updatedAt = Date.now()

  const actorName = getGroupMemberDisplayName(room, actorId)
  appendGroupChatMessage(
    room,
    buildGroupSystemMessage(
      draft
        ? `${actorName} 更新了群公告：${draft}`
        : `${actorName} 清空了群公告。`
    )
  )
  groupChatInfo.value = draft ? '群公告已更新。' : '群公告已清空。'
  saveGroupChatsState()
}

const saveSelectedGroupRules = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }

  const draft = normalizeGroupRules(groupRulesDraftByRoomId.value[room.id] || '')
  if (draft === room.rules) {
    groupChatInfo.value = '群规则未变化。'
    return
  }

  room.rules = draft
  groupRulesDraftByRoomId.value[room.id] = draft
  room.updatedAt = Date.now()

  const actorName = getGroupMemberDisplayName(room, actorId)
  const preview = draft.split('\n').map((line) => line.trim()).find(Boolean) || draft
  appendGroupChatMessage(
    room,
    buildGroupSystemMessage(
      draft
        ? `${actorName} 更新了群规则：${normalizeGroupMessageContent(preview, 80)}`
        : `${actorName} 清空了群规则。`
    )
  )
  groupChatInfo.value = draft ? '群规则已更新。' : '群规则已清空。'
  saveGroupChatsState()
}

const transferSelectedGroupAdmin = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) return

  const actorId = resolveGroupAdminActorId(room)
  if (!actorId) {
    groupChatError.value = '当前群没有可用管理员。'
    return
  }

  const targetId = String(groupAdminTransferTargetByRoomId.value[room.id] || '')
  const target = room.members.find((member) => member.id === targetId && member.isAi)
  if (!target) {
    groupChatError.value = '请选择要转让的 AI 管理员。'
    return
  }

  const actorName = getGroupMemberDisplayName(room, actorId)
  room.members = room.members.map((member) => {
    if (member.id === 'user') return { ...member, isAdmin: true }
    if (!member.isAi) return { ...member, isAdmin: false }
    return { ...member, isAdmin: member.id === target.id }
  })
  room.updatedAt = Date.now()
  groupAdminActorByRoomId.value[room.id] = target.id
  groupAdminTransferTargetByRoomId.value[room.id] = target.id
  ensureGroupRoomEditorState(room)

  appendGroupChatMessage(
    room,
    buildGroupSystemMessage(`${actorName} 将群管理员转让给 ${target.name}。用户仍保留最终管理权限。`)
  )
  groupChatInfo.value = `管理员已转让给 ${target.name}。`
  saveGroupChatsState()
}

const openGroupMediaPicker = (mode: 'image' | 'video') => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  if (!selectedGroupChat.value) {
    groupChatError.value = '请先选择群聊。'
    return
  }
  groupMediaPickerType.value = mode
  const input = groupMediaInputRef.value
  if (!input) return
  input.value = ''
  input.accept = mode === 'video' ? 'video/*' : 'image/*'
  input.click()
}

const handleGroupMediaUpload = async (event: Event) => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!room) {
    groupChatError.value = '请先选择群聊。'
    input.value = ''
    return
  }

  const rawMediaType = getMediaTypeFromFile(file)
  if (rawMediaType !== 'image' && rawMediaType !== 'video') {
    groupChatError.value = '群聊仅支持发送图片和视频。'
    input.value = ''
    return
  }

  if (groupMediaPickerType.value !== rawMediaType) {
    groupChatError.value = groupMediaPickerType.value === 'image' ? '当前入口仅支持图片。' : '当前入口仅支持视频。'
    input.value = ''
    return
  }

  const sizeLimit = rawMediaType === 'image' ? 12 * 1024 * 1024 : 120 * 1024 * 1024
  if (file.size > sizeLimit) {
    groupChatError.value = `${rawMediaType === 'image' ? '图片' : '视频'}过大，最大支持 ${formatFileSize(sizeLimit)}。`
    input.value = ''
    return
  }

  const mediaUrl = URL.createObjectURL(file)
  registerObjectUrl(mediaUrl)
  const caption = normalizeGroupMessageContent(groupChatMessageDraft.value, 220)
  const fallbackText = rawMediaType === 'video' ? '我发送了一段视频。' : '我发送了一张图片。'
  appendGroupChatMessage(room, buildGroupMessage(buildUserGroupMember(), rawMediaType, caption || fallbackText, { mediaUrl }))
  groupChatMessageDraft.value = ''
  showGroupEmojiPanel.value = false
  input.value = ''

  if (room.mutedByUser) {
    groupChatInfo.value = `已发送${rawMediaType === 'image' ? '图片' : '视频'}（该群处于屏蔽状态，不会触发 AI 回复）。`
    saveGroupChatsState()
    return
  }

  const triggerText = `[group_media:${rawMediaType}] ${caption || file.name || (rawMediaType === 'image' ? '[用户发送图片]' : '[用户发送视频]')}`
  await runGroupAiConversation(room, triggerText)
  groupChatInfo.value = `已发送${rawMediaType === 'image' ? '图片' : '视频'}：${file.name}`
  saveGroupChatsState()
}

const buildGroupConversationContext = (room: GroupChatRoom, limit = 10) => {
  const lines = room.messages
    .slice(-limit)
    .map((msg) => {
      if (msg.type === 'system') return `系统: ${msg.content}`
      if (msg.type === 'emoji') return `${msg.senderName}: [emoji] ${msg.content}`
      if (msg.type === 'image') return `${msg.senderName}: [image] ${msg.content || '发送了一张图片'}`
      if (msg.type === 'video') return `${msg.senderName}: [video] ${msg.content || '发送了一段视频'}`
      if (msg.type === 'audio') return `${msg.senderName}: [audio] ${msg.content || '发送了一段语音'}`
      return `${msg.senderName}: ${msg.content}`
    })
    .filter(Boolean)
  return lines.join('\n').slice(-2000)
}

const buildFallbackGroupReply = (speakerName: string, triggerText: string) => {
  const source = normalizeGroupMessageContent(triggerText || '', 120)
  const pool = [
    '收到，我在群里跟进一下。',
    '这个点子不错，我补充一点细节。',
    '我赞同，后续可以按这个方向继续。',
    '我先记下了，等会儿补充更多信息。',
  ]
  const base = pool[Math.floor(Math.random() * pool.length)] || `${speakerName} 在群里回应。`
  return normalizeGroupMessageContent(source ? `${base}（关于：${source.slice(0, 28)}）` : base, 180)
}

const generateGroupReplyByAI = async (room: GroupChatRoom, speaker: GroupChatMember, triggerText: string) => {
  const persona = personas.value.find((item) => item.id === speaker.id) || null
  if (!isConnected.value || !persona) {
    return buildFallbackGroupReply(speaker.name, triggerText)
  }

  const mediaType = getGroupMediaTriggerType(triggerText)
  const mediaGuide = mediaType === 'video'
    ? '用户刚发送了视频，请围绕视频内容回应，允许追问细节，但不要假装真实看到了画面中的具体人物。'
    : mediaType === 'image'
      ? '用户刚发送了图片，请围绕图片主题回应，允许给出氛围或建议。'
      : ''
  const modeLabel = getGroupReplyModeLabel(normalizeGroupReplyMode(room.replyMode))
  const prompt = [
    `你现在在群聊「${room.name}」中发言，角色是：${persona.name}。`,
    `群成员：${room.members.map((member) => member.name).join('、')}`,
    `当前群回复模式：${modeLabel}`,
    room.announcement ? `群公告：${room.announcement}` : '',
    room.rules ? `群规则：${room.rules}` : '',
    `触发消息：${normalizeGroupMessageContent(triggerText, 120) || '（无）'}`,
    '请根据最近群聊上下文自然回复。',
    mediaGuide,
    '要求：只输出一条简短中文消息（1-2句，最多60字）；禁止输出系统描述、禁止自称AI。',
    `最近群聊：\n${buildGroupConversationContext(room, 8) || '暂无历史消息'}`,
  ]
    .filter(Boolean)
    .join('\n')

  try {
    const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`,
      },
      body: JSON.stringify({
        model: apiSettings.value.modelName,
        stream: false,
        temperature: 0.85,
        max_tokens: 120,
        messages: [
          { role: 'system', content: persona.systemPrompt || `你是${persona.name}` },
          { role: 'user', content: prompt },
        ],
      }),
    })
    if (!response.ok) throw new Error(await readResponseErrorMessage(response))
    const payload = await response.json()
    const text = normalizeGroupMessageContent(extractChatTextContent(payload), 180)
    return text || buildFallbackGroupReply(speaker.name, triggerText)
  } catch {
    return buildFallbackGroupReply(speaker.name, triggerText)
  }
}

const generateGroupAudioByText = async (text: string, speakerPersona?: Persona | null, guidanceText = '') => {
  if (!isConnected.value) throw new Error('未配置可用 API。')
  const ttsConfig = resolveTtsConfig()
  const baseUrl = apiSettings.value.baseUrl.replace(/\/+$/, '')
  const modelCandidates = buildAudioModelCandidates(apiSettings.value.modelName.trim())
  const forcedGender = detectVoiceGenderHintFromText(guidanceText)
  const voiceCandidates = resolveVoiceCandidatesByPersona(
    speakerPersona || currentPersona.value,
    mediaVoice.value,
    voiceToolboxSettings.value,
    forcedGender
  )
  let lastError = ''

  if (ttsConfig.ttsProvider === 'coqui') {
    for (const voice of voiceCandidates) {
      try {
        const coquiAudio = await requestCoquiAudioSynthesis(ttsConfig, {
          text,
          voiceHint: voice,
          speed: Number(mediaSpeechRate.value || 1),
        })
        const src = coquiAudio.src
        if (src.startsWith('blob:')) registerObjectUrl(src)
        return src
      } catch (error: any) {
        lastError = error?.message || 'Coqui 语音生成失败'
      }
    }
    throw new Error(lastError || 'Coqui 语音生成失败')
  }

  for (const model of modelCandidates) {
    for (const voice of voiceCandidates) {
      const response = await fetch(`${baseUrl}/audio/speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiSettings.value.apiKey}`,
        },
        body: JSON.stringify({
          model,
          voice,
          input: text,
          response_format: 'mp3',
        }),
      })

      if (!response.ok) {
        lastError = await readResponseErrorMessage(response)
        continue
      }

      const contentType = response.headers.get('content-type') || ''
      if (contentType.includes('audio/')) {
        const blob = await response.blob()
        return URL.createObjectURL(blob)
      }

      const payload = await response.json()
      const directUrl = extractMediaUrlFromPayload(payload)
      if (directUrl) return directUrl
      const b64 = pickFirstString(payload?.audio, payload?.audio_base64, payload?.data?.[0]?.b64_json, payload?.data?.[0]?.base64)
      if (b64) return b64.startsWith('data:audio/') ? b64 : `data:audio/mpeg;base64,${b64}`
      lastError = '语音接口返回成功，但未解析到音频数据。'
    }
  }

  throw new Error(lastError || '语音生成失败')
}

const generateGroupImageByPrompt = async (prompt: string) => {
  const imageApiConfig = resolveImageApiConfig()
  if (!imageApiConfig.baseUrl || !imageApiConfig.apiKey) {
    throw new Error('未配置可用 AI 生图接口。')
  }
  const modelCandidates = buildImageModelCandidates(imageApiConfig)
  let lastError = ''

  for (const model of modelCandidates) {
    try {
      const decoded = await requestImageWithModel(imageApiConfig, model, prompt)
      if (decoded?.src) return decoded.src
      lastError = '图片接口返回成功，但未解析到图片数据。'
    } catch (error: any) {
      lastError = error?.message || '图片生成失败'
      continue
    }
  }
  throw new Error(lastError || '图片生成失败，请确认 AI 生图接口支持 Gemini v1beta 或 /images/generations。')
}

const queueGroupImageConsentRequest = (room: GroupChatRoom, speaker: GroupChatMember, triggerText: string) => {
  const triggerPlainText = String(triggerText || '').replace(/\[group_media:(image|video)\]/gi, '').trim()
  const basePrompt = normalizeGroupMessageContent(triggerPlainText, 120) || '群聊当前讨论内容'
  const prompt = `请为群聊「${room.name}」生成一张配图，角色：${speaker.name}，场景要贴合讨论内容：${basePrompt}，画面干净，无违规元素。`
  groupImageConsentPending.value = {
    id: createMomentId(),
    groupId: room.id,
    speakerId: speaker.id,
    speakerName: speaker.name,
    prompt,
    createdAt: Date.now(),
  }
  appendGroupChatMessage(room, buildGroupSystemMessage(`${speaker.name} 请求发送 AI 图片，等待用户同意。`))
}

const maybeRunAiAdminAction = (
  room: GroupChatRoom,
  speaker: GroupChatMember,
  triggerText: string,
  profile: GroupReplyModeProfile
) => {
  if (!speaker.isAdmin) return false
  if (shouldBlockAiAdminActionByUserIntent(triggerText)) return false
  if (Math.random() > profile.adminActionChance) return false

  const moderationHint = /(刷屏|广告|违规|辱骂|踢|移出|清理|封禁|管理)/.test(triggerText)
  if (moderationHint && Math.random() < profile.autoKickChance && room.members.length > 3) {
    const removable = room.members.filter((member) => member.isAi && member.id !== speaker.id && !member.isAdmin)
    if (removable.length > 0) {
      const target = removable[Math.floor(Math.random() * removable.length)]
      if (target && removeMemberFromGroupRoom(room, target.id, speaker.name, '因群规问题移出群聊')) {
        return true
      }
    }
  }

  const notices: string[] = []
  if (room.announcement) {
    notices.push(`公告提醒：${normalizeGroupMessageContent(room.announcement, 90)}`)
  }
  if (room.rules) {
    const firstRule = room.rules.split('\n').map((line) => line.trim()).find(Boolean) || room.rules
    notices.push(`群规提醒：${normalizeGroupMessageContent(firstRule, 90)}`)
  }
  if (notices.length === 0) return false

  const notice = notices[Math.floor(Math.random() * notices.length)] || ''
  if (!notice) return false
  appendGroupChatMessage(room, buildGroupSystemMessage(`${speaker.name}（AI管理员）执行管理动作：${notice}`))
  return true
}

const runGroupAiConversation = async (room: GroupChatRoom, triggerText: string, forcedCount = 0) => {
  ensureGroupRoomDefaults(room)
  if (room.mutedByUser) return
  const aiMembers = shuffleArray(room.members.filter((member) => member.isAi))
  if (aiMembers.length === 0) return

  const profile = GROUP_REPLY_MODE_PROFILES[room.replyMode] || GROUP_REPLY_MODE_PROFILES.normal
  const mediaTriggerType = getGroupMediaTriggerType(triggerText)
  const randomSpeakerCount = randomBetween(
    profile.minSpeakers,
    Math.min(aiMembers.length, profile.maxSpeakers + (mediaTriggerType ? 1 : 0))
  )
  const maxCount = clampNumber(forcedCount || randomSpeakerCount, 1, aiMembers.length)
  const speakers = aiMembers.slice(0, maxCount)
  const emojiPool = [...GROUP_EMOJI_LIBRARY.常用, ...GROUP_EMOJI_LIBRARY.情绪]
  let followUpBudget = profile.maxFollowUps
  let adminActionBudget = profile.adminActionCount

  for (const speaker of speakers) {
    if (!room.members.some((member) => member.id === speaker.id)) continue
    const leaveChance = speaker.isAdmin ? 0 : profile.leaveChance
    if (Math.random() < leaveChance && room.members.length > 2) {
      removeMemberFromGroupRoom(room, speaker.id, speaker.name, '主动退群')
      continue
    }

    const emojiChance = mediaTriggerType ? Math.max(0.03, profile.emojiChance - 0.08) : profile.emojiChance
    const imageChance = mediaTriggerType === 'image' ? profile.imageRequestChance + 0.06 : profile.imageRequestChance
    const audioChance = mediaTriggerType ? profile.audioChance + 0.06 : profile.audioChance
    const imageThreshold = Math.min(0.92, emojiChance + imageChance)
    const audioThreshold = Math.min(0.96, imageThreshold + audioChance)
    const roll = Math.random()
    if (roll < emojiChance) {
      const emoji = emojiPool[Math.floor(Math.random() * emojiPool.length)] || '🙂'
      appendGroupChatMessage(room, buildGroupMessage(speaker, 'emoji', emoji))
    } else if (roll < imageThreshold && !groupImageConsentPending.value) {
      queueGroupImageConsentRequest(room, speaker, triggerText)
    } else {
      const text = await generateGroupReplyByAI(room, speaker, triggerText)
      if (roll < audioThreshold && isConnected.value) {
        try {
          isGroupGeneratingAudio.value = true
          const speakerPersona = personas.value.find((item) => item.id === speaker.id) || currentPersona.value
          const audioUrl = await generateGroupAudioByText(text, speakerPersona, triggerText)
          registerObjectUrl(audioUrl)
          appendGroupChatMessage(room, buildGroupMessage(speaker, 'audio', text, { mediaUrl: audioUrl }))
        } catch {
          appendGroupChatMessage(room, buildGroupMessage(speaker, 'text', text))
        } finally {
          isGroupGeneratingAudio.value = false
        }
      } else {
        appendGroupChatMessage(room, buildGroupMessage(speaker, 'text', text))
      }
    }

    if (speaker.isAdmin && adminActionBudget > 0) {
      if (maybeRunAiAdminAction(room, speaker, triggerText, profile)) {
        adminActionBudget -= 1
      }
    }

    if (followUpBudget > 0 && Math.random() < profile.followUpChance) {
      const candidates = room.members.filter((member) => member.isAi && member.id !== speaker.id)
      const followUpSpeaker = candidates[Math.floor(Math.random() * candidates.length)]
      if (followUpSpeaker) {
        const followUpTrigger = normalizeGroupMessageContent(`${speaker.name} 刚发言：${triggerText}`, 180)
        const followUpText = await generateGroupReplyByAI(room, followUpSpeaker, followUpTrigger)
        appendGroupChatMessage(room, buildGroupMessage(followUpSpeaker, 'text', followUpText))
        followUpBudget -= 1

        if (followUpSpeaker.isAdmin && adminActionBudget > 0) {
          if (maybeRunAiAdminAction(room, followUpSpeaker, followUpTrigger, profile)) {
            adminActionBudget -= 1
          }
        }
      }
    }
  }
}

const triggerGroupAiConversation = async (room: GroupChatRoom) => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  ensureGroupRoomDefaults(room)
  if (room.mutedByUser) {
    groupChatError.value = '该群已屏蔽消息，取消屏蔽后再触发互动。'
    return
  }
  await runGroupAiConversation(room, '用户主动触发群内互动', 2)
  groupChatInfo.value = '群内 AI 互动已触发。'
  saveGroupChatsState()
}

const sendGroupChatMessage = async () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const room = selectedGroupChat.value
  if (!room) {
    groupChatError.value = '请先选择群聊。'
    return
  }

  const text = normalizeGroupMessageContent(groupChatMessageDraft.value, 220)
  if (!text) return

  ensureGroupRoomDefaults(room)
  appendGroupChatMessage(room, buildGroupMessage(buildUserGroupMember(), 'text', text))
  groupChatMessageDraft.value = ''

  if (room.mutedByUser) {
    groupChatInfo.value = '你已发送消息（该群处于屏蔽状态，不会触发 AI 回复）。'
    saveGroupChatsState()
    return
  }

  await runGroupAiConversation(room, text)
  saveGroupChatsState()
}

const sendGroupEmoji = async (emoji: string) => {
  const room = selectedGroupChat.value
  if (!room) return
  ensureGroupRoomDefaults(room)
  appendGroupChatMessage(room, buildGroupMessage(buildUserGroupMember(), 'emoji', emoji || '😀'))
  if (!room.mutedByUser) {
    await runGroupAiConversation(room, emoji || 'emoji')
  }
  saveGroupChatsState()
}

const approveGroupImageRequest = async () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const pending = groupImageConsentPending.value
  if (!pending) return
  const room = getGroupChatRoomById(pending.groupId)
  if (!room) {
    groupImageConsentPending.value = null
    return
  }
  const speaker = room.members.find((member) => member.id === pending.speakerId)
  if (!speaker) {
    groupImageConsentPending.value = null
    return
  }
  const imageApiConfig = resolveImageApiConfig()
  if (!imageApiConfig.baseUrl || !imageApiConfig.apiKey) {
    groupChatError.value = '未配置 AI 生图接口，无法生成群聊图片。'
    return
  }

  isGroupGeneratingImage.value = true
  try {
    const imageUrl = await generateGroupImageByPrompt(pending.prompt)
    appendGroupChatMessage(
      room,
      buildGroupMessage(
        speaker,
        'image',
        `${speaker.name} 发送了一张图片。`,
        { mediaUrl: imageUrl }
      )
    )
    groupImageConsentPending.value = null
    groupChatInfo.value = '已同意并发送 AI 图片。'
    saveGroupChatsState()
  } catch (error: any) {
    groupChatError.value = error?.message || '群聊图片生成失败'
  } finally {
    isGroupGeneratingImage.value = false
  }
}

const rejectGroupImageRequest = () => {
  groupChatInfo.value = ''
  groupChatError.value = ''
  const pending = groupImageConsentPending.value
  if (!pending) return
  const room = getGroupChatRoomById(pending.groupId)
  if (!room) {
    groupImageConsentPending.value = null
    return
  }
  appendGroupChatMessage(room, buildGroupSystemMessage(`用户拒绝了 ${pending.speakerName} 的发图请求。`))
  groupImageConsentPending.value = null
  groupChatInfo.value = '已拒绝该发图请求。'
  saveGroupChatsState()
}

const sanitizeUserProfileForStorage = () => {
  const payload: UserProfileForm = {
    name: userProfile.name.trim() || defaultUserName(),
    gender: userProfile.gender.trim(),
    personality: userProfile.personality.trim(),
    traits: userProfile.traits.trim(),
    chatStyle: userProfile.chatStyle.trim(),
    avatarPreview: userProfile.avatarPreview.startsWith('data:image/') && userProfile.avatarPreview.length <= 360000
      ? userProfile.avatarPreview
      : '',
    avatarUrl: userProfile.avatarUrl.trim(),
    avatarPrompt: userProfile.avatarPrompt.trim()
  }
  return payload
}

const saveUserProfile = () => {
  localStorage.setItem(USER_PROFILE_STORAGE_KEY, JSON.stringify(sanitizeUserProfileForStorage()))
  if (momentsHydrated.value) {
    syncMomentsDataWithPersonas()
    syncGroupChatsWithPersonas()
    ensureSelectedGroupChatReady()
    saveMomentsState()
    saveGroupChatsState()
  }
}

const loadUserProfile = () => {
  const raw = localStorage.getItem(USER_PROFILE_STORAGE_KEY)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return
    const parsedNameRaw = String(parsed.name || '').trim()
    const parsedName = !parsedNameRaw
      ? defaultUserName()
      : (!isChineseLocale.value && parsedNameRaw === '用户' ? defaultUserName() : parsedNameRaw)
    Object.assign(userProfile, {
      ...createDefaultUserProfile(),
      name: parsedName,
      gender: String(parsed.gender || ''),
      personality: String(parsed.personality || ''),
      traits: String(parsed.traits || ''),
      chatStyle: String(parsed.chatStyle || ''),
      avatarPreview: String(parsed.avatarPreview || ''),
      avatarUrl: String(parsed.avatarUrl || ''),
      avatarPrompt: String(parsed.avatarPrompt || '')
    })
  } catch (error) {
    console.error('Failed to load user profile:', error)
  }
}

const openUserProfileEditor = () => {
  userProfileInfo.value = ''
  userProfileError.value = ''
  showUserProfileEditor.value = true
}

const closeUserProfileEditor = () => {
  showUserProfileEditor.value = false
  userProfileInfo.value = ''
  userProfileError.value = ''
}

const handleUserAvatarUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  userProfileInfo.value = ''
  userProfileError.value = ''

  const allowedTypes = ['image/png', 'image/jpeg', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    userProfileError.value = '头像仅支持 PNG / JPG / WebP。'
    input.value = ''
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    userProfileError.value = '头像大小不能超过 2MB。'
    input.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    userProfile.avatarPreview = String(reader.result || '')
    userProfile.avatarUrl = ''
    saveUserProfile()
  }
  reader.onerror = () => {
    userProfileError.value = '头像读取失败，请重试。'
  }
  reader.readAsDataURL(file)
}

const clearUserAvatar = () => {
  userProfile.avatarPreview = ''
  userProfile.avatarUrl = ''
  userProfileInfo.value = ''
  userProfileError.value = ''
  saveUserProfile()
}

const buildUserAvatarPrompt = () => {
  const seeds = [
    userProfile.name.trim() ? `名字：${userProfile.name.trim()}` : '',
    userProfile.gender.trim() ? `性别：${userProfile.gender.trim()}` : '',
    userProfile.personality.trim() ? `性格：${userProfile.personality.trim()}` : '',
    userProfile.traits.trim() ? `特点：${userProfile.traits.trim()}` : '',
    userProfile.chatStyle.trim() ? `聊天风格：${userProfile.chatStyle.trim()}` : ''
  ].filter(Boolean)

  return [
    '请生成一个用于聊天软件头像的单人角色形象。',
    '要求：主体居中、面部清晰、光线自然、无水印无文字、风格统一。',
    ...seeds
  ].join('\n')
}

const generateUserAvatarWithAI = async () => {
  if (isGeneratingUserAvatar.value) return
  userProfileInfo.value = ''
  userProfileError.value = ''

  const imageApiConfig = resolveImageApiConfig()
  if (!imageApiConfig.baseUrl || !imageApiConfig.apiKey) {
    userProfileError.value = '请先在设置中填写并保存可用的 AI 生图接口（Base URL 与 API Key）。'
    return
  }

  const prompt = userProfile.avatarPrompt.trim() || buildUserAvatarPrompt()
  if (!prompt.trim()) {
    userProfileError.value = '请先补充用户设定信息或头像提示词。'
    return
  }

  const candidateModels = buildImageModelCandidates(imageApiConfig)

  isGeneratingUserAvatar.value = true
  try {
    let imageResult: { src: string; mimeType?: string } | null = null
    let successModel = ''
    let lastError = ''

    for (const model of candidateModels) {
      try {
        imageResult = await requestImageWithModel(imageApiConfig, model, prompt)
      } catch (error: any) {
        lastError = error?.message || '图片生成失败'
        imageResult = null
      }
      if (!imageResult?.src) {
        if (!lastError) lastError = '图片接口返回成功，但未解析到图片数据。'
        continue
      }
      successModel = model
      break
    }

    if (!imageResult) {
      throw new Error(lastError || '用户头像生成失败，请确认 AI 生图接口支持 Gemini v1beta 或 images/generations。')
    }

    if (imageResult.src.startsWith('data:image/')) {
      userProfile.avatarPreview = imageResult.src
      userProfile.avatarUrl = ''
    } else {
      userProfile.avatarUrl = imageResult.src
      userProfile.avatarPreview = ''
    }
    saveUserProfile()
    userProfileInfo.value = `头像生成成功${successModel ? `（模型：${successModel}）` : ''}。`
  } catch (error: any) {
    userProfileError.value = error?.message || 'AI 头像生成失败，请稍后重试。'
  } finally {
    isGeneratingUserAvatar.value = false
  }
}

const applyUserProfileFields = (parsed: Record<string, unknown>, overwriteAll = false) => {
  const toText = (value: unknown) => normalizeAutoFillText(value)
  const assign = (key: keyof UserProfileForm, next: string) => {
    if (!next) return false
    const current = userProfile[key]
    if (!overwriteAll && typeof current === 'string' && current.trim()) return false
    ;(userProfile[key] as string) = next
    return true
  }

  let changed = 0
  if (assign('name', toText(parsed.name))) changed += 1
  if (assign('gender', toText(parsed.gender))) changed += 1
  if (assign('personality', toText(parsed.personality))) changed += 1
  if (assign('traits', toText(parsed.traits))) changed += 1
  if (assign('chatStyle', toText(parsed.chatStyle))) changed += 1
  if (assign('avatarPrompt', toText(parsed.avatarPrompt))) changed += 1
  return changed
}

const generateUserNameWithAI = async () => {
  if (isGeneratingUserProfileText.value) return
  userProfileInfo.value = ''
  userProfileError.value = ''

  if (!isConnected.value) {
    userProfileError.value = '请先在设置中填写并保存可用的 API（Base URL 与 API Key）。'
    return
  }

  isGeneratingUserProfileText.value = true
  try {
    const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model: apiSettings.value.modelName,
        stream: false,
        temperature: 0.9,
        max_tokens: 80,
        messages: [
          { role: 'system', content: '你是取名助手，只输出一个中文名字，不要解释。' },
          {
            role: 'user',
            content: [
              '请生成一个适合聊天场景的用户名字。',
              userProfile.gender.trim() ? `性别偏好：${userProfile.gender.trim()}` : '',
              userProfile.personality.trim() ? `性格偏好：${userProfile.personality.trim()}` : '',
              userProfile.chatStyle.trim() ? `聊天风格：${userProfile.chatStyle.trim()}` : ''
            ].filter(Boolean).join('\n')
          }
        ]
      })
    })

    if (!response.ok) throw new Error(await readResponseErrorMessage(response))
    const data = await response.json()
    const name = normalizeMomentContent(extractChatTextContent(data)).replace(/["“”'`]/g, '').slice(0, 16)
    if (!name) throw new Error('AI 未生成可用名字，请重试。')
    userProfile.name = name
    saveUserProfile()
    userProfileInfo.value = `名字已生成：${name}`
  } catch (error: any) {
    userProfileError.value = error?.message || 'AI 名字生成失败，请稍后重试。'
  } finally {
    isGeneratingUserProfileText.value = false
  }
}

const generateUserProfileTextWithAI = async (overwriteAll = false) => {
  if (isGeneratingUserProfileText.value) return 0
  userProfileInfo.value = ''
  userProfileError.value = ''

  if (!isConnected.value) {
    userProfileError.value = '请先在设置中填写并保存可用的 API（Base URL 与 API Key）。'
    return 0
  }

  const hasAnyInput = [
    userProfile.name,
    userProfile.gender,
    userProfile.personality,
    userProfile.traits,
    userProfile.chatStyle
  ].some((value) => String(value || '').trim())

  if (!hasAnyInput && !overwriteAll) {
    userProfileError.value = '请先填写至少一项用户信息，或直接使用“一键 AI 生成”。'
    return 0
  }

  isGeneratingUserProfileText.value = true
  try {
    const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model: apiSettings.value.modelName,
        stream: false,
        temperature: 0.85,
        messages: [
          {
            role: 'system',
            content: '你是用户设定生成助手。只能返回 JSON 对象，不要返回 Markdown 或解释。'
          },
          {
            role: 'user',
            content: [
              '请生成或补全聊天用户设定。',
              '输出 JSON 键仅允许：name,gender,personality,traits,chatStyle,avatarPrompt。',
              '要求：中文、自然、不低俗、不暴力。',
              overwriteAll ? '当前模式：一键完整生成，可覆盖已有字段。' : '当前模式：只补全未填写字段。',
              `当前设定：${JSON.stringify({
                name: userProfile.name,
                gender: userProfile.gender,
                personality: userProfile.personality,
                traits: userProfile.traits,
                chatStyle: userProfile.chatStyle
              })}`
            ].join('\n')
          }
        ]
      })
    })

    if (!response.ok) throw new Error(await readResponseErrorMessage(response))
    const data = await response.json()
    const parsed = extractJsonObjectFromText(extractChatTextContent(data))
    if (!parsed) throw new Error('AI 返回格式无法解析，请重试。')

    const changed = applyUserProfileFields(parsed, overwriteAll)
    if (changed <= 0) {
      userProfileError.value = 'AI 未返回可用内容，请调整输入后重试。'
      return 0
    }
    saveUserProfile()
    userProfileInfo.value = overwriteAll ? '用户设定已一键生成。' : `已补全 ${changed} 项用户设定。`
    return changed
  } catch (error: any) {
    userProfileError.value = error?.message || 'AI 用户设定生成失败，请稍后重试。'
    return 0
  } finally {
    isGeneratingUserProfileText.value = false
  }
}

const oneClickGenerateUserProfile = async () => {
  if (isGeneratingUserProfileOneClick.value) return
  isGeneratingUserProfileOneClick.value = true
  userProfileInfo.value = ''
  userProfileError.value = ''

  try {
    await generateUserProfileTextWithAI(true)
    await generateUserAvatarWithAI()
    if (!userProfileError.value) {
      userProfileInfo.value = tr(
        '已完成一键 AI 生成（名称、性别、性格、特点、聊天风格、头像）。',
        'One-click AI generation completed (name, gender, personality, traits, chat style, avatar).'
      )
    }
  } finally {
    isGeneratingUserProfileOneClick.value = false
  }
}

const saveUserProfileFromEditor = () => {
  if (!userProfile.name.trim()) {
    userProfile.name = defaultUserName()
  }
  saveUserProfile()
  userProfileInfo.value = tr('用户设定已保存。', 'User profile saved.')
}

const readStorageJson = (key: string): any | null => {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const normalizeStorageText = (value: unknown): string => {
  if (typeof value === 'string') return value.trim()
  if (typeof value === 'number') return String(value)
  return ''
}

const decodeUriComponentSafe = (value: string): string => {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

const normalizeImportedAvatarUrl = (value: unknown): string => {
  const raw = normalizeStorageText(value)
  if (!raw) return ''
  const prefix = '/characters/avatars/'
  if (!raw.startsWith(prefix)) return raw
  const fileName = raw.slice(prefix.length).replace(/^\/+/, '')
  if (!fileName) return raw
  const decodedFileName = decodeUriComponentSafe(fileName)
  return `${prefix}${encodeURIComponent(decodedFileName)}`
}

const loadBrokenImportedPersonaIds = () => {
  brokenImportedPersonaIds.clear()
  const payload = readStorageJson(BROKEN_IMPORTED_PERSONAS_STORAGE_KEY)
  if (!Array.isArray(payload)) return
  payload.forEach((item) => {
    const personaId = normalizeStorageText(item)
    if (personaId) brokenImportedPersonaIds.add(personaId)
  })
}

const saveBrokenImportedPersonaIds = () => {
  localStorage.setItem(
    BROKEN_IMPORTED_PERSONAS_STORAGE_KEY,
    JSON.stringify(Array.from(brokenImportedPersonaIds))
  )
}

const extractPersonaGenderFromDescription = (description: string): string => {
  const match = String(description || '').match(/性别\s*[:：]\s*([^\n|,，;；]+)/i)
  return match?.[1] ? String(match[1]).trim().slice(0, 12) : ''
}

const extractPersonaPersonalityFromDescription = (description: string): string => {
  const match = String(description || '').match(/性格\s*[:：]\s*([^\n|]+)/i)
  return match?.[1] ? String(match[1]).trim().slice(0, 64) : ''
}

const normalizeLoadedCustomPersona = (item: any, index: number): Persona | null => {
  if (!item || typeof item !== 'object') return null
  const name = normalizeStorageText(item.name)
  if (!name) return null

  const personaId = normalizeStorageText(item.id) || `custom_load_${index}`
  const systemPrompt = normalizeStorageText(item.systemPrompt) || tr(`你是${name}，请保持人设并与用户自然互动。`, `You are ${name}. Stay in character and interact naturally with the user.`)
  const avatar =
    normalizeImportedAvatarUrl(normalizeStorageText(item.avatar)) ||
    `https://api.dicebear.com/7.x/notionists/svg?seed=${encodeURIComponent(name)}&backgroundColor=e0e7ff`
  const description = normalizeStorageText(item.description) || tr(`${name} 的自定义角色`, `${name}'s custom role`)
  const gender = normalizeStorageText(item.gender) || extractPersonaGenderFromDescription(description)
  const personality = normalizeStorageText(item.personality) || extractPersonaPersonalityFromDescription(description)

  return {
    id: personaId,
    name,
    avatar,
    description,
    systemPrompt,
    gender,
    personality,
    group: normalizeStorageText(item.group) || defaultCustomPersonaGroup(),
    firstMessage: normalizeStorageText(item.firstMessage),
    source: 'custom'
  }
}

const parseApiSettingsPayload = (payload: unknown): Partial<ApiSettings> => {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return {}
  const root = payload as Record<string, unknown>
  const apiPayload =
    root.apiSettings && typeof root.apiSettings === 'object' && !Array.isArray(root.apiSettings)
      ? (root.apiSettings as Record<string, unknown>)
      : root

  const parsed: Partial<ApiSettings> = {}
  const baseUrl = normalizeStorageText(apiPayload.baseUrl)
  const apiKey = normalizeStorageText(apiPayload.apiKey)
  const modelName = normalizeStorageText(apiPayload.modelName || apiPayload.chatModel)
  const imageBaseUrl = normalizeStorageText(apiPayload.imageBaseUrl || apiPayload.image_base_url)
  const imageApiKey = normalizeStorageText(apiPayload.imageApiKey || apiPayload.image_api_key)
  const imageModelName = normalizeStorageText(apiPayload.imageModelName || apiPayload.imageModel || apiPayload.image_model)
  const imageApiTypeRaw = normalizeStorageText(
    apiPayload.imageApiType || apiPayload.image_api_type || apiPayload.imageProvider || apiPayload.image_provider
  )
  const ttsProviderRaw = normalizeStorageText(
    apiPayload.ttsProvider || apiPayload.tts_provider || apiPayload.voiceProvider || apiPayload.voice_provider
  )
  const coquiBaseUrl = normalizeStorageText(
    apiPayload.coquiBaseUrl || apiPayload.coqui_base_url || apiPayload.coquiUrl || apiPayload.coqui_url
  )
  const coquiModelName = normalizeStorageText(
    apiPayload.coquiModelName || apiPayload.coqui_model_name || apiPayload.ttsModelName || apiPayload.tts_model_name
  )
  const coquiLanguage = normalizeStorageText(
    apiPayload.coquiLanguage || apiPayload.coqui_language || apiPayload.ttsLanguage || apiPayload.tts_language
  )
  const coquiSpeaker = normalizeCoquiSpeakerValue(
    apiPayload.coquiSpeaker || apiPayload.coqui_speaker
  )

  if (baseUrl) parsed.baseUrl = baseUrl
  if (apiKey) parsed.apiKey = apiKey
  if (modelName) parsed.modelName = modelName
  if (imageBaseUrl) parsed.imageBaseUrl = imageBaseUrl
  if (imageApiKey) parsed.imageApiKey = imageApiKey
  if (imageModelName) parsed.imageModelName = imageModelName
  if (imageApiTypeRaw) parsed.imageApiType = normalizeImageApiType(imageApiTypeRaw)
  if (ttsProviderRaw) parsed.ttsProvider = normalizeTtsProvider(ttsProviderRaw)
  if (coquiBaseUrl) parsed.coquiBaseUrl = normalizeRelativeOrAbsoluteUrl(coquiBaseUrl, '/api/tts/coqui/synthesize/')
  if (coquiModelName) parsed.coquiModelName = coquiModelName
  if (coquiLanguage) parsed.coquiLanguage = coquiLanguage
  if (coquiSpeaker) parsed.coquiSpeaker = coquiSpeaker
  return parsed
}

const resolveSavedApiSettings = (): ApiSettings | null => {
  const legacyParsed = parseApiSettingsPayload(readStorageJson(SETTINGS_STORAGE_KEY))
  const v2Parsed = parseApiSettingsPayload(readStorageJson(SETTINGS_STORAGE_KEY_V2))
  const hasAnyValue = Boolean(
    legacyParsed.baseUrl || legacyParsed.apiKey || legacyParsed.modelName ||
    legacyParsed.imageBaseUrl || legacyParsed.imageApiKey || legacyParsed.imageModelName || legacyParsed.imageApiType ||
    legacyParsed.ttsProvider || legacyParsed.coquiBaseUrl || legacyParsed.coquiModelName || legacyParsed.coquiLanguage || legacyParsed.coquiSpeaker ||
    v2Parsed.baseUrl || v2Parsed.apiKey || v2Parsed.modelName ||
    v2Parsed.imageBaseUrl || v2Parsed.imageApiKey || v2Parsed.imageModelName || v2Parsed.imageApiType ||
    v2Parsed.ttsProvider || v2Parsed.coquiBaseUrl || v2Parsed.coquiModelName || v2Parsed.coquiLanguage || v2Parsed.coquiSpeaker
  )
  if (!hasAnyValue) return null

  const resolvedBaseUrl = legacyParsed.baseUrl || v2Parsed.baseUrl || apiSettings.value.baseUrl
  const resolvedApiKey = legacyParsed.apiKey || v2Parsed.apiKey || apiSettings.value.apiKey
  const resolvedModelName = legacyParsed.modelName || v2Parsed.modelName || apiSettings.value.modelName
  const resolvedImageApiType = normalizeImageApiType(
    legacyParsed.imageApiType ||
      v2Parsed.imageApiType ||
      inferImageApiTypeFromModel(legacyParsed.imageModelName || v2Parsed.imageModelName || resolvedModelName || apiSettings.value.imageModelName)
  )
  const resolvedImageModelName =
    legacyParsed.imageModelName ||
    v2Parsed.imageModelName ||
    resolvedModelName ||
    apiSettings.value.imageModelName ||
    defaultImageModelByType(resolvedImageApiType)
  const resolvedTtsProvider = normalizeTtsProvider(
    legacyParsed.ttsProvider ||
      v2Parsed.ttsProvider ||
      apiSettings.value.ttsProvider
  )

  return {
    baseUrl: resolvedBaseUrl,
    apiKey: resolvedApiKey,
    modelName: resolvedModelName,
    imageBaseUrl: legacyParsed.imageBaseUrl || v2Parsed.imageBaseUrl || resolvedBaseUrl || apiSettings.value.imageBaseUrl,
    imageApiKey: legacyParsed.imageApiKey || v2Parsed.imageApiKey || resolvedApiKey || apiSettings.value.imageApiKey,
    imageModelName: resolvedImageModelName,
    imageApiType: resolvedImageApiType,
    ttsProvider: resolvedTtsProvider,
    coquiBaseUrl: normalizeRelativeOrAbsoluteUrl(
      legacyParsed.coquiBaseUrl || v2Parsed.coquiBaseUrl || apiSettings.value.coquiBaseUrl,
      '/api/tts/coqui/synthesize/'
    ),
    coquiModelName:
      legacyParsed.coquiModelName ||
      v2Parsed.coquiModelName ||
      apiSettings.value.coquiModelName ||
      'tts_models/multilingual/multi-dataset/xtts_v2',
    coquiLanguage:
      legacyParsed.coquiLanguage ||
      v2Parsed.coquiLanguage ||
      apiSettings.value.coquiLanguage ||
      'zh-cn',
    coquiSpeaker: normalizeCoquiSpeakerValue(
      legacyParsed.coquiSpeaker ||
      v2Parsed.coquiSpeaker ||
      apiSettings.value.coquiSpeaker
    ),
  }
}

const resolveSavedVoiceToolboxSettings = (): VoiceToolboxSettings => {
  const raw = readStorageJson(VOICE_TOOLBOX_STORAGE_KEY)
  if (!raw) return { ...DEFAULT_VOICE_TOOLBOX_SETTINGS }
  return normalizeVoiceToolboxSettings(raw)
}

const persistVoiceToolboxSettings = (payload: VoiceToolboxSettings) => {
  const normalized = normalizeVoiceToolboxSettings(payload)
  voiceToolboxSettings.value = normalized
  localStorage.setItem(VOICE_TOOLBOX_STORAGE_KEY, JSON.stringify(normalized))
}

const resolveSavedSelectedPersonaId = (): string => {
  const legacy = normalizeStorageText(localStorage.getItem(SELECTED_PERSONA_STORAGE_KEY))
  const v2 = normalizeStorageText(localStorage.getItem(SELECTED_PERSONA_STORAGE_KEY_V2))
  return legacy || v2
}

const persistSelectedPersonaId = (personaId: string) => {
  const normalizedId = normalizeStorageText(personaId)
  if (!normalizedId) return
  localStorage.setItem(SELECTED_PERSONA_STORAGE_KEY, normalizedId)
  localStorage.setItem(SELECTED_PERSONA_STORAGE_KEY_V2, normalizedId)
}

const applySavedSelectedPersona = (fallbackToFirst = true): Persona | null => {
  const savedId = resolveSavedSelectedPersonaId()
  const selected = savedId
    ? personas.value.find((item) => String(item.id) === savedId) || null
    : null

  if (selected) {
    currentPersona.value = selected
    persistSelectedPersonaId(selected.id)
    return selected
  }

  if (fallbackToFirst && personas.value.length > 0) {
    currentPersona.value = personas.value[0]
    persistSelectedPersonaId(currentPersona.value.id)
    return currentPersona.value
  }

  return null
}

const saveCustomPersonas = () => {
  const payload = JSON.stringify(customPersonas.value)
  try {
    localStorage.setItem(CUSTOM_PERSONAS_STORAGE_KEY_V2, payload)
  } catch (error) {
    try {
      // Release legacy storage first, then retry v2 once.
      localStorage.removeItem(CUSTOM_PERSONAS_STORAGE_KEY)
      localStorage.setItem(CUSTOM_PERSONAS_STORAGE_KEY_V2, payload)
    } catch {
      throw error
    }
  }

  // Keep legacy key as best-effort compatibility, but never block the flow.
  try {
    localStorage.setItem(CUSTOM_PERSONAS_STORAGE_KEY, payload)
  } catch {
    try {
      localStorage.removeItem(CUSTOM_PERSONAS_STORAGE_KEY)
    } catch {
      // ignore
    }
  }
}

const loadCustomPersonas = (): Persona[] => {
  const legacy = readStorageJson(CUSTOM_PERSONAS_STORAGE_KEY)
  const v2 = readStorageJson(CUSTOM_PERSONAS_STORAGE_KEY_V2)
  const merged = [...(Array.isArray(legacy) ? legacy : []), ...(Array.isArray(v2) ? v2 : [])]
  const deduped: Persona[] = []
  const seenIds = new Set<string>()

  merged.forEach((item, index) => {
    const persona = normalizeLoadedCustomPersona(item, index)
    if (!persona) return
    if (seenIds.has(persona.id)) return
    seenIds.add(persona.id)
    deduped.push(persona)
  })

  return deduped
}

const normalizeLocationStatusText = (value: unknown): string => {
  return String(value || '')
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/[，,]/g, '·')
    .replace(/[|]/g, '·')
    .replace(/\s+/g, '')
    .replace(/·{2,}/g, '·')
    .replace(/^·+|·+$/g, '')
    .slice(0, 18)
}

const loadPersonaLocationStatusMap = (): Record<string, string> => {
  const raw = localStorage.getItem(PERSONA_LOCATION_STATUS_STORAGE_KEY)
  if (!raw) return {}
  try {
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {}
    const next: Record<string, string> = {}
    Object.entries(parsed as Record<string, unknown>).forEach(([key, value]) => {
      const personaId = String(key || '').trim()
      if (!personaId) return
      const status = normalizeLocationStatusText(value)
      if (!status) return
      if (!isChineseLocale.value && containsHanChars(status)) return
      next[personaId] = status
    })
    return next
  } catch {
    return {}
  }
}

const savePersonaLocationStatusMap = () => {
  localStorage.setItem(PERSONA_LOCATION_STATUS_STORAGE_KEY, JSON.stringify(personaLocationStatusMap.value))
}

const parseLocationStatusList = (content: string): string[] => {
  const cleaned = String(content || '').trim()
  if (!cleaned) return []

  const parsed = extractJsonObjectFromText(cleaned)
  let values: string[] = []
  if (parsed) {
    const obj = parsed as Record<string, unknown>
    const list = Array.isArray(obj.locations)
      ? obj.locations
      : Array.isArray(obj.items)
      ? obj.items
      : []
    values = list.map((item) => normalizeLocationStatusText(item)).filter(Boolean)
  }

  if (values.length > 0) return values

  return cleaned
    .split(/\n+/)
    .map((line) => line.replace(/^\s*[-*#\d.、]+\s*/, ''))
    .map((line) => normalizeLocationStatusText(line))
    .filter(Boolean)
}

const generateLocationStatusesWithAI = async (
  count: number,
  usedStatuses: Set<string>,
  personaNames: string[]
): Promise<string[]> => {
  if (!isConnected.value || count <= 0) return []

  const safeCount = Math.max(1, Math.min(count, 48))
  const baseUrl = apiSettings.value.baseUrl.replace(/\/+$/, '')
  const modelCandidates = Array.from(new Set([apiSettings.value.modelName.trim(), 'gpt-4o-mini', 'gpt-3.5-turbo'].filter(Boolean)))
  const separator = isChineseLocale.value ? '、' : ', '
  const usedText = Array.from(usedStatuses).slice(0, 80).join(separator)
  const namesText = personaNames.slice(0, safeCount).join(separator)
  let lastError = ''

  for (const model of modelCandidates) {
    const response = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model,
        temperature: 0.9,
        max_tokens: 420,
        stream: false,
        messages: [
          {
            role: 'system',
            content: tr(
              '你是地址状态生成器。必须返回 JSON 对象，格式：{"locations":["城市·地点",...]}。不要返回解释。',
              'You generate online location statuses. Return ONLY JSON in this format: {"locations":["City·Place", ...]}. No explanation.'
            )
          },
          {
            role: 'user',
            content: [
              tr(
                `请生成 ${safeCount} 个不重复的中文“地址状态”短语，用于聊天角色在线状态显示。`,
                `Generate ${safeCount} unique online status phrases in English for chat role presence.`
              ),
              tr(
                '格式要求：每项 6-14 字，风格类似“上海·静安寺”“杭州·西湖边”。',
                'Format: each item should be 6-30 chars, similar to "Tokyo·Shibuya" or "New York·SoHo".'
              ),
              namesText ? tr(`角色名参考：${namesText}`, `Role name reference: ${namesText}`) : '',
              usedText ? tr(`禁止重复以下地址：${usedText}`, `Do not repeat these statuses: ${usedText}`) : ''
            ].filter(Boolean).join('\n')
          }
        ]
      })
    })

    if (!response.ok) {
      lastError = await readResponseErrorMessage(response)
      continue
    }

    const payload = await response.json()
    const content = extractChatTextContent(payload)
    const candidates = parseLocationStatusList(content)
    const uniq: string[] = []
    for (const item of candidates) {
      const normalized = normalizeLocationStatusText(item)
      if (!normalized) continue
      if (usedStatuses.has(normalized)) continue
      if (uniq.includes(normalized)) continue
      uniq.push(normalized)
      if (uniq.length >= safeCount) break
    }
    if (uniq.length > 0) return uniq
    lastError = tr('AI 返回成功，但未解析到可用地址状态。', 'AI returned successfully but no valid location statuses were parsed.')
  }

  if (lastError) {
    console.warn('[PersonaLocationStatus] AI generation fallback:', lastError)
  }
  return []
}

const buildFallbackLocationStatus = (seed: number): string => {
  const city = FALLBACK_LOCATION_CITY_POOL[seed % FALLBACK_LOCATION_CITY_POOL.length] || tr('城市', 'City')
  const scene = FALLBACK_LOCATION_SCENE_POOL[Math.floor(seed / FALLBACK_LOCATION_CITY_POOL.length) % FALLBACK_LOCATION_SCENE_POOL.length] || tr('地标', 'Landmark')
  return `${city}·${scene}`
}

const assignPersonaLocationStatuses = async (personaList: Persona[], rebuildAll = false) => {
  const list = Array.isArray(personaList) ? personaList.filter((item) => item && item.id) : []
  if (list.length === 0) return

  const token = ++personaLocationAssignToken
  const nextMap: Record<string, string> = rebuildAll ? {} : { ...personaLocationStatusMap.value }
  const used = new Set<string>()
  const missing: Persona[] = []

  for (const persona of list) {
    const personaId = String(persona.id)
    const existing = normalizeLocationStatusText(nextMap[personaId])
    const shouldKeepExisting = !rebuildAll && existing && !used.has(existing) && (isChineseLocale.value || !containsHanChars(existing))
    if (shouldKeepExisting) {
      nextMap[personaId] = existing
      used.add(existing)
      continue
    }
    delete nextMap[personaId]
    missing.push(persona)
  }

  const localCandidates = shuffleArray([...LOCAL_PERSONA_LOCATION_POOL])
    .map((item) => normalizeLocationStatusText(item))
    .filter((item) => item && !used.has(item))

  while (missing.length > 0 && localCandidates.length > 0) {
    const persona = missing.shift()!
    const candidate = localCandidates.shift()!
    nextMap[String(persona.id)] = candidate
    used.add(candidate)
  }

  if (missing.length > 0 && isConnected.value) {
    const aiCandidates = await generateLocationStatusesWithAI(
      Math.min(missing.length, 48),
      used,
      missing.map((item) => item.name)
    )
    if (token !== personaLocationAssignToken) return

    for (const candidate of aiCandidates) {
      if (missing.length <= 0) break
      if (used.has(candidate)) continue
      const persona = missing.shift()!
      nextMap[String(persona.id)] = candidate
      used.add(candidate)
    }
  }

  let fallbackSeed = 0
  while (missing.length > 0) {
    const candidate = normalizeLocationStatusText(buildFallbackLocationStatus(fallbackSeed))
    fallbackSeed += 1
    if (!candidate || used.has(candidate)) continue
    const persona = missing.shift()!
    nextMap[String(persona.id)] = candidate
    used.add(candidate)
  }

  if (token !== personaLocationAssignToken) return
  personaLocationStatusMap.value = nextMap
  savePersonaLocationStatusMap()
}

const resetPersonaForm = () => {
  Object.assign(personaForm, createEmptyPersonaForm())
  personaCreateError.value = ''
  personaCardImportInfo.value = ''
  personaCardImportError.value = ''
  personaAutoFillInfo.value = ''
  personaAutoFillError.value = ''
  avatarGeneratePrompt.value = ''
  avatarGenerateInfo.value = ''
  avatarGenerateError.value = ''
}

const pickRandomNetworkStatus = () => {
  const candidates = NETWORK_STATUS_OPTIONS.filter((item) => item !== networkStatusLabel.value)
  const next = candidates[Math.floor(Math.random() * candidates.length)] || networkStatusLabel.value
  networkStatusLabel.value = next
}

const scheduleNetworkStatusTicker = () => {
  if (networkStatusTimer) clearTimeout(networkStatusTimer)
  const delay = 1800 + Math.floor(Math.random() * 3200)
  networkStatusTimer = setTimeout(() => {
    pickRandomNetworkStatus()
    scheduleNetworkStatusTicker()
  }, delay)
}

const stopNetworkStatusTicker = () => {
  if (!networkStatusTimer) return
  clearTimeout(networkStatusTimer)
  networkStatusTimer = null
}

const onHtmlFrameMessage = (event: MessageEvent) => {
  const payload = event.data
  if (!payload || payload.source !== HTML_FRAME_SOURCE) return
  if (typeof payload.frameId !== 'string' || typeof payload.height !== 'number') return

  const clampedHeight = Math.max(
    MIN_HTML_FRAME_HEIGHT,
    Math.min(MAX_HTML_FRAME_HEIGHT, Math.ceil(payload.height))
  )
  messageHtmlFrameHeights.value[payload.frameId] = clampedHeight
}

// --- Lifecycle ---
onMounted(() => {
  scheduleNetworkStatusTicker()
  window.addEventListener('message', onHtmlFrameMessage)
  loadUserProfile()
  momentsTrendContext.value = loadMomentsTrendContext()
  personaLocationStatusMap.value = loadPersonaLocationStatusMap()
  customPersonas.value = loadCustomPersonas()
  loadBrokenImportedPersonaIds()
  if (customPersonas.value.length > 0) {
    personas.value = [...customPersonas.value, ...personas.value]
  }
  applySavedSelectedPersona(true)
  void assignPersonaLocationStatuses(personas.value)

  const savedApiSettings = resolveSavedApiSettings()
  if (savedApiSettings) {
    apiSettings.value = savedApiSettings
    tempSettings.value = { ...savedApiSettings }
  } else {
    showSettings.value = true
  }

  const savedVoiceToolbox = resolveSavedVoiceToolboxSettings()
  voiceToolboxSettings.value = savedVoiceToolbox
  tempVoiceToolboxSettings.value = { ...savedVoiceToolbox }

  const savedGames = localStorage.getItem('cypher_tavern_games')
  if (savedGames) {
    try {
      games.value = JSON.parse(savedGames)
      currentGame.value = games.value[0]
    } catch (e) { console.error(e) }
  }

  // Load Characters
  fetch('/characters/index.json')
    .then(res => res.json())
    .then(data => {
      // Merge with default personas, avoiding duplicates if any.
      const importedList = Array.isArray(data) ? data : []
      const newPersonas = importedList
        .map((c: any) => ({
          id: c.id,
          name: c.name,
          avatar: normalizeImportedAvatarUrl(c.avatar),
          description: c.description,
          systemPrompt: c.systemPrompt,
          gender: String(c.gender || '').trim(),
          personality: String(c.personality || '').trim(),
          group: c.group || PERSONA_GROUP_CHARACTER,
          firstMessage: c.firstMessage,
          file: c.file,
          source: 'imported' as const
        }))
        .filter((persona) => {
          const personaId = normalizeStorageText(persona.id)
          if (!personaId) return false
          return !brokenImportedPersonaIds.has(personaId)
        })
      
      // Combine defaults with imported
      personas.value = [...customPersonas.value, ...newPersonas]
      if (personas.value.length === 0) {
        personas.value = [...DEFAULT_PERSONAS]
      }
      if (collapsedGroups.value[PERSONA_GROUP_NOVEL] === undefined) {
        collapsedGroups.value[PERSONA_GROUP_NOVEL] = true
      }
      applySavedSelectedPersona(true)
      void assignPersonaLocationStatuses(personas.value)
      syncMomentsDataWithPersonas()
      initializeMoments().catch((error) => console.error('Failed to initialize moments:', error))
    })
    .catch(e => {
      console.error('Failed to load characters:', e)
      applySavedSelectedPersona(true)
      void assignPersonaLocationStatuses(personas.value)
      syncMomentsDataWithPersonas()
      initializeMoments().catch((error) => console.error('Failed to initialize moments:', error))
    })
})

onBeforeUnmount(() => {
  stopNetworkStatusTicker()
  stopMomentsTicker()
  window.removeEventListener('message', onHtmlFrameMessage)
  releaseAllMessageMedia(messages.value)
  trackedObjectUrls.value.forEach((src) => URL.revokeObjectURL(src))
  trackedObjectUrls.value = []
})

// --- Methods ---

const openPersonaCreator = () => {
  resetPersonaForm()
  showPersonaCreator.value = true
}

const closePersonaCreator = () => {
  showPersonaCreator.value = false
}

const pickFirstString = (...values: unknown[]): string => {
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) {
      return value.trim()
    }
  }
  return ''
}

const decodeBase64Utf8 = (value: string): string => {
  const compact = value.replace(/\s+/g, '')
  const binary = window.atob(compact)
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0))
  return new TextDecoder('utf-8').decode(bytes)
}

const tryParseCharacterPayload = (rawText: string): any | null => {
  if (!rawText || typeof rawText !== 'string') return null
  const trimmed = rawText.trim()
  if (!trimmed) return null

  const attempts: string[] = [trimmed]
  if (/^[A-Za-z0-9+/=\r\n]+$/.test(trimmed) && trimmed.length >= 32) {
    try {
      attempts.unshift(decodeBase64Utf8(trimmed))
    } catch {
      // Ignore and continue JSON parse fallback.
    }
  }

  for (const candidate of attempts) {
    try {
      return JSON.parse(candidate)
    } catch {
      // continue
    }
  }
  return null
}

const extractJsonObjectFromText = (text: string): Record<string, unknown> | null => {
  const source = String(text || '').trim()
  if (!source) return null

  const candidates: string[] = [source]
  const fenceMatch = source.match(/```(?:json)?\s*([\s\S]*?)```/i)
  if (fenceMatch?.[1]) {
    candidates.push(fenceMatch[1].trim())
  }
  const firstBrace = source.indexOf('{')
  const lastBrace = source.lastIndexOf('}')
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    candidates.push(source.slice(firstBrace, lastBrace + 1).trim())
  }

  for (const candidate of candidates) {
    try {
      const parsed = JSON.parse(candidate)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return parsed as Record<string, unknown>
      }
    } catch {
      // continue
    }
  }
  return null
}

const normalizeAutoFillText = (value: unknown): string => {
  if (typeof value === 'string') return value.trim()
  if (typeof value === 'number') return String(value)
  return ''
}

const buildAvatarPromptFromPersona = () => {
  const name = personaForm.name.trim()
  const personality = personaForm.personality.trim()
  const background = personaForm.background.trim()
  const description = personaForm.description.trim()
  const gender = personaForm.gender.trim()
  const title = personaForm.title.trim()

  const seeds = [
    name ? `角色名：${name}` : '',
    gender ? `性别：${gender}` : '',
    title ? `定位：${title}` : '',
    personality ? `性格关键词：${personality}` : '',
    background ? `背景关键词：${background}` : '',
    description ? `角色简介：${description}` : ''
  ].filter(Boolean)

  return [
    '请生成一张高质量的二次元角色头像。',
    '要求：单人、半身或近景、主体居中、面部清晰、干净背景、无文字水印、无logo、风格统一。',
    ...seeds
  ].join('\n')
}

const decodeImageDataFromResponse = (payload: any): { src: string; mimeType?: string } | null => {
  const first = payload?.data?.[0] || payload?.output?.[0] || null
  if (first && typeof first === 'object') {
    const url = pickFirstString(first.url, first.image_url, first.output_url)
    if (url) return { src: url }

    const b64 = pickFirstString(
      first.b64_json,
      first.base64,
      first.image_base64,
      first.image?.b64_json,
      first.image?.base64
    )
    if (b64) {
      if (b64.startsWith('data:image/')) {
        return { src: b64 }
      }

      const mimeType = pickFirstString(first.mime_type, first.image?.mime_type) || 'image/png'
      return { src: `data:${mimeType};base64,${b64}`, mimeType }
    }
  }

  const candidates = Array.isArray(payload?.candidates) ? payload.candidates : []
  for (const candidate of candidates) {
    const parts = Array.isArray(candidate?.content?.parts) ? candidate.content.parts : []
    for (const part of parts) {
      const inlineData = part?.inline_data || part?.inlineData || null
      const imageUrl = pickFirstString(part?.url, part?.image_url)
      if (imageUrl) return { src: imageUrl }

      const b64 = pickFirstString(inlineData?.data, part?.data)
      if (!b64) continue

      if (b64.startsWith('data:image/')) return { src: b64 }
      const mimeType =
        pickFirstString(inlineData?.mime_type, inlineData?.mimeType, part?.mime_type, part?.mimeType) || 'image/png'
      return { src: `data:${mimeType};base64,${b64}`, mimeType }
    }
  }

  return null
}

const readResponseErrorMessage = async (response: Response) => {
  try {
    const data = await response.json()
    const message = pickFirstString(
      data?.error?.message,
      data?.message,
      typeof data?.error === 'string' ? data.error : ''
    )
    if (message) return message
  } catch {
    // ignore JSON parse failure
  }
  try {
    const text = (await response.text()).trim()
    if (text) return text.slice(0, 220)
  } catch {
    // ignore
  }
  return `HTTP ${response.status}`
}

const resolveTokenAuthorizationHeader = (): string => {
  if (typeof window === 'undefined') return ''
  const token = String(window.localStorage.getItem('authToken') || window.localStorage.getItem('token') || '').trim()
  if (!token) return ''
  if (/^(Token|Bearer)\s+/i.test(token)) return token
  return `Token ${token}`
}

const requestCoquiAudioSynthesis = async (
  ttsConfig: ResolvedTtsConfig,
  payload: {
    text: string
    voiceHint?: string
    speed?: number
  }
): Promise<{ src: string; speakerUsed: string }> => {
  const endpoint = ensureTrailingSlash(
    normalizeRelativeOrAbsoluteUrl(ttsConfig.coquiBaseUrl, '/api/tts/coqui/synthesize/')
  )
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  const authHeader = resolveTokenAuthorizationHeader()
  if (authHeader) {
    headers.Authorization = authHeader
  }

  const response = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      text: String(payload.text || ''),
      model_name: ttsConfig.coquiModelName,
      language: ttsConfig.coquiLanguage,
      speaker: ttsConfig.coquiSpeaker || undefined,
      voice_hint: String(payload.voiceHint || '').trim() || undefined,
      speed: Number(payload.speed || 1),
    }),
  })
  if (!response.ok) throw new Error(await readResponseErrorMessage(response))

  const speakerUsed = String(response.headers.get('X-Coqui-Speaker') || '').trim()
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('audio/')) {
    const blob = await response.blob()
    return { src: URL.createObjectURL(blob), speakerUsed }
  }

  const json = await response.json()
  const directUrl = pickFirstString(json?.audio_url, json?.url, json?.data?.audio_url, json?.data?.url)
  if (directUrl) return { src: directUrl, speakerUsed }

  const b64 = pickFirstString(json?.audio_base64, json?.audio, json?.data?.audio_base64, json?.data?.audio)
  if (b64) {
    if (b64.startsWith('data:audio/')) return { src: b64, speakerUsed }
    const mimeType = pickFirstString(json?.mime_type, json?.content_type, json?.data?.mime_type) || 'audio/wav'
    return { src: `data:${mimeType};base64,${b64}`, speakerUsed }
  }

  throw new Error('Coqui 语音接口返回成功，但未解析到音频数据。')
}

const resolveGeminiNativeBase = (baseUrl: string) => {
  const trimmed = String(baseUrl || '').trim().replace(/\/+$/, '')
  return trimmed.replace(/\/v1(?:beta)?$/i, '')
}

const fileToBase64Data = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = String(reader.result || '')
      const commaIndex = result.indexOf(',')
      resolve(commaIndex >= 0 ? result.slice(commaIndex + 1) : result)
    }
    reader.onerror = () => reject(new Error('参考图读取失败'))
    reader.readAsDataURL(file)
  })
}

const requestImageWithModel = async (
  imageApiConfig: ResolvedImageApiConfig,
  model: string,
  prompt: string,
  options?: { referenceFile?: File | null }
): Promise<{ src: string; mimeType?: string }> => {
  const trimmedModel = String(model || '').trim()
  if (!trimmedModel) throw new Error('未配置有效的生图模型。')

  if (imageApiConfig.imageApiType === 'gemini_native') {
    const geminiBase = resolveGeminiNativeBase(imageApiConfig.baseUrl)
    const endpoint = `${geminiBase}/v1beta/models/${encodeURIComponent(trimmedModel)}:generateContent`
    const parts: any[] = [{ text: prompt }]
    if (options?.referenceFile) {
      const base64Data = await fileToBase64Data(options.referenceFile)
      parts.push({
        inline_data: {
          mime_type: options.referenceFile.type || 'image/png',
          data: base64Data,
        },
      })
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': imageApiConfig.apiKey,
      },
      body: JSON.stringify({
        contents: [{ role: 'user', parts }],
        generationConfig: { responseModalities: ['TEXT', 'IMAGE'] },
      }),
    })
    if (!response.ok) throw new Error(await readResponseErrorMessage(response))
    const payload = await response.json()
    const decoded = decodeImageDataFromResponse(payload)
    if (!decoded?.src) throw new Error('图片接口返回成功，但未解析到图片数据。')
    return decoded
  }

  if (options?.referenceFile) {
    const editForm = new FormData()
    editForm.append('model', trimmedModel)
    editForm.append('prompt', prompt)
    editForm.append('size', '1024x1024')
    editForm.append('n', '1')
    editForm.append('image', options.referenceFile, options.referenceFile.name)

    const editResponse = await fetch(`${imageApiConfig.baseUrl}/images/edits`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${imageApiConfig.apiKey}`,
      },
      body: editForm,
    })
    if (!editResponse.ok) throw new Error(await readResponseErrorMessage(editResponse))
    const editPayload = await editResponse.json()
    const editDecoded = decodeImageDataFromResponse(editPayload)
    if (!editDecoded?.src) throw new Error('图片编辑接口返回成功，但未解析到图片数据。')
    return editDecoded
  }

  const response = await fetch(`${imageApiConfig.baseUrl}/images/generations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${imageApiConfig.apiKey}`,
    },
    body: JSON.stringify({
      model: trimmedModel,
      prompt,
      size: '1024x1024',
      n: 1,
    }),
  })
  if (!response.ok) throw new Error(await readResponseErrorMessage(response))
  const payload = await response.json()
  const decoded = decodeImageDataFromResponse(payload)
  if (!decoded?.src) throw new Error('图片接口返回成功，但未解析到图片数据。')
  return decoded
}

const generatePersonaAvatarWithAI = async () => {
  if (isGeneratingAvatar.value) return

  avatarGenerateInfo.value = ''
  avatarGenerateError.value = ''
  personaCreateError.value = ''

  const imageApiConfig = resolveImageApiConfig()
  if (!imageApiConfig.baseUrl || !imageApiConfig.apiKey) {
    avatarGenerateError.value = '请先在设置中填写并保存可用的 AI 生图接口（Base URL 与 API Key）。'
    return
  }

  const prompt = avatarGeneratePrompt.value.trim() || buildAvatarPromptFromPersona()
  if (!prompt.trim()) {
    avatarGenerateError.value = '请先填写角色信息或头像提示词后再生成。'
    return
  }

  const candidateModels = buildImageModelCandidates(imageApiConfig)

  isGeneratingAvatar.value = true
  try {
    let imageResult: { src: string; mimeType?: string } | null = null
    let successModel = ''
    let lastError = ''

    for (const model of candidateModels) {
      try {
        imageResult = await requestImageWithModel(imageApiConfig, model, prompt)
      } catch (error: any) {
        lastError = error?.message || '图片生成失败'
        imageResult = null
      }
      if (!imageResult?.src) {
        if (!lastError) lastError = '图片接口返回成功，但未解析到图片数据。'
        continue
      }

      successModel = model
      break
    }

    if (!imageResult) {
      throw new Error(lastError || '图片生成失败，请确认 AI 生图接口支持 Gemini v1beta 或 images/generations。')
    }

    if (imageResult.src.startsWith('data:image/')) {
      personaForm.avatarPreview = imageResult.src
      personaForm.avatarUrl = ''
    } else {
      personaForm.avatarUrl = imageResult.src
      personaForm.avatarPreview = ''
    }

    avatarGenerateInfo.value = `头像生成成功${successModel ? `（模型：${successModel}）` : ''}。`
  } catch (error: any) {
    avatarGenerateError.value = error?.message || 'AI 头像生成失败，请稍后重试。'
  } finally {
    isGeneratingAvatar.value = false
  }
}

const autoCompletePersonaForm = async () => {
  if (isAutoCompletingPersona.value) return

  personaAutoFillInfo.value = ''
  personaAutoFillError.value = ''
  personaCreateError.value = ''

  if (!isConnected.value) {
    personaAutoFillError.value = '请先在设置中填写并保存可用的 API（Base URL 与 API Key）。'
    return
  }

  const missingFields = personaMissingFieldKeys.value
  if (missingFields.length === 0) {
    personaAutoFillInfo.value = '当前所有字段都已填写，无需补全。'
    return
  }

  const filledData: Record<string, string> = {}
  PERSONA_AUTOFILL_FIELDS.forEach((field) => {
    const value = personaForm[field]
    if (typeof value === 'string' && value.trim()) {
      filledData[field] = value.trim()
    }
  })

  isAutoCompletingPersona.value = true
  try {
    const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model: apiSettings.value.modelName,
        stream: false,
        temperature: 0.7,
        messages: [
          {
            role: 'system',
            content:
              '你是角色卡补全助手。你只能返回一个 JSON 对象，不要返回 Markdown、解释或多余文本。'
          },
          {
            role: 'user',
            content: [
              '请基于已填写角色信息，补全缺失字段。',
              '要求：',
              '1) 仅输出 JSON 对象。',
              '2) 仅可包含这些键：name,nickname,age,gender,title,description,personality,background,firstMessage,systemPrompt,group。',
              '3) 内容使用中文，贴合已填写设定，避免违法/低俗/暴力内容。',
              '4) 字段若无法判断可返回空字符串。',
              '',
              `已填写字段(JSON): ${JSON.stringify(filledData)}`,
              `待补全字段: ${missingFields.map((field) => PERSONA_FIELD_LABELS[field]).join('、')}`
            ].join('\n')
          }
        ]
      })
    })

    if (!response.ok) throw new Error(`API Error: ${response.status}`)

    const data = await response.json()
    const content = String(data?.choices?.[0]?.message?.content || '')
    const parsed = extractJsonObjectFromText(content)
    if (!parsed) {
      throw new Error('AI 返回格式无法解析，请重试。')
    }

    let filledCount = 0
    const filledLabels: string[] = []
    PERSONA_AUTOFILL_FIELDS.forEach((field) => {
      if (typeof personaForm[field] === 'string' && personaForm[field].trim()) return
      const next = normalizeAutoFillText(parsed[field])
      if (!next) return
      ;(personaForm[field] as string) = next
      filledCount += 1
      filledLabels.push(PERSONA_FIELD_LABELS[field])
    })

    if (filledCount === 0) {
      throw new Error('AI 未返回可用补全内容，请补充更多信息后重试。')
    }

    if (personaForm.systemPrompt.trim()) {
      personaCardImportError.value = ''
    }
    personaAutoFillInfo.value = `AI 已补全 ${filledCount} 项：${filledLabels.join('、')}`
  } catch (error: any) {
    personaAutoFillError.value = error?.message || 'AI 自动补全失败，请稍后重试。'
  } finally {
    isAutoCompletingPersona.value = false
  }
}

const normalizePersonaCardPayload = (payload: any, fallbackName: string): PersonaCardImportData => {
  const data = payload?.data && typeof payload.data === 'object' ? payload.data : payload
  const explicitSystemPrompt = pickFirstString(
    data?.systemPrompt,
    payload?.systemPrompt,
    data?.system_prompt,
    payload?.system_prompt,
    data?.char_persona,
    payload?.char_persona,
    data?.persona,
    payload?.persona,
    data?.post_history_instructions,
    payload?.post_history_instructions,
    data?.creator_notes,
    payload?.creator_notes,
    data?.extensions?.system_prompt,
    payload?.extensions?.system_prompt
  )
  const fallbackSystemPrompt = [
    pickFirstString(data?.description, payload?.description),
    pickFirstString(data?.personality, payload?.personality),
    pickFirstString(data?.scenario, payload?.scenario),
  ]
    .filter(Boolean)
    .join('\n')

  return {
    name: pickFirstString(data?.name, payload?.name, fallbackName),
    description: pickFirstString(
      data?.description,
      payload?.description,
      data?.personality,
      payload?.personality,
      data?.scenario,
      payload?.scenario
    ),
    systemPrompt: pickFirstString(explicitSystemPrompt, fallbackSystemPrompt),
    firstMessage: pickFirstString(
      data?.firstMessage,
      payload?.firstMessage,
      data?.first_mes,
      payload?.first_mes,
      data?.mes_example,
      payload?.mes_example
    ),
    group: pickFirstString(data?.group, payload?.group),
    avatar: pickFirstString(data?.avatar, payload?.avatar, data?.avatar_url, payload?.avatar_url)
  }
}

const readFileAsDataUrl = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error('读取文件失败，请重试。'))
    reader.readAsDataURL(file)
  })
}

const inflateDeflateText = async (bytes: Uint8Array): Promise<string> => {
  const DS = (globalThis as any).DecompressionStream
  if (!DS) {
    throw new Error('当前浏览器不支持解析压缩 PNG 角色卡，请改用 JSON 或未压缩 PNG。')
  }
  const stream = new Blob([bytes]).stream().pipeThrough(new DS('deflate'))
  const buffer = await new Response(stream).arrayBuffer()
  return new TextDecoder('utf-8').decode(new Uint8Array(buffer))
}

const parsePngCardTextChunks = async (file: File): Promise<string> => {
  const buffer = await file.arrayBuffer()
  const bytes = new Uint8Array(buffer)
  const signature = [137, 80, 78, 71, 13, 10, 26, 10]
  for (let i = 0; i < signature.length; i += 1) {
    if (bytes[i] !== signature[i]) {
      throw new Error('文件不是有效的 PNG 图片。')
    }
  }

  const view = new DataView(buffer)
  const utf8Decoder = new TextDecoder('utf-8')
  const latinDecoder = new TextDecoder('latin1')
  let offset = 8

  while (offset + 8 <= bytes.length) {
    const length = view.getUint32(offset, false)
    const type = String.fromCharCode(
      bytes[offset + 4],
      bytes[offset + 5],
      bytes[offset + 6],
      bytes[offset + 7]
    )
    const dataStart = offset + 8
    const dataEnd = dataStart + length
    if (dataEnd + 4 > bytes.length) break
    const chunkData = bytes.subarray(dataStart, dataEnd)

    if (type === 'tEXt') {
      const sep = chunkData.indexOf(0)
      if (sep > 0) {
        const keyword = latinDecoder.decode(chunkData.subarray(0, sep))
        if (keyword === 'chara') {
          return latinDecoder.decode(chunkData.subarray(sep + 1))
        }
      }
    } else if (type === 'zTXt') {
      const sep = chunkData.indexOf(0)
      if (sep > 0 && sep + 2 <= chunkData.length) {
        const keyword = latinDecoder.decode(chunkData.subarray(0, sep))
        if (keyword === 'chara') {
          const compressed = chunkData.subarray(sep + 2)
          return await inflateDeflateText(compressed)
        }
      }
    } else if (type === 'iTXt') {
      const keywordEnd = chunkData.indexOf(0)
      if (keywordEnd > 0 && keywordEnd + 3 <= chunkData.length) {
        const keyword = utf8Decoder.decode(chunkData.subarray(0, keywordEnd))
        if (keyword === 'chara') {
          const compressedFlag = chunkData[keywordEnd + 1]
          let cursor = keywordEnd + 3
          const languageEnd = chunkData.indexOf(0, cursor)
          if (languageEnd < 0) {
            throw new Error('PNG 角色卡语言标签损坏。')
          }
          cursor = languageEnd + 1
          const translatedEnd = chunkData.indexOf(0, cursor)
          if (translatedEnd < 0) {
            throw new Error('PNG 角色卡标题字段损坏。')
          }
          cursor = translatedEnd + 1
          const textBytes = chunkData.subarray(cursor)
          if (compressedFlag === 1) {
            return await inflateDeflateText(textBytes)
          }
          return utf8Decoder.decode(textBytes)
        }
      }
    }

    offset = dataEnd + 4
  }

  throw new Error('未在 PNG 中找到角色卡数据（chara）。')
}

const applyPersonaCardToForm = (card: PersonaCardImportData, fallbackAvatar = '') => {
  if (card.name) personaForm.name = card.name
  if (card.description) personaForm.description = card.description
  if (card.systemPrompt) personaForm.systemPrompt = card.systemPrompt
  if (card.firstMessage) personaForm.firstMessage = card.firstMessage
  if (card.group) personaForm.group = card.group

  const avatar = card.avatar.trim()
  if (avatar) {
    personaForm.avatarUrl = avatar
    personaForm.avatarPreview = avatar.startsWith('data:image/') ? avatar : ''
  } else if (fallbackAvatar) {
    personaForm.avatarPreview = fallbackAvatar
    personaForm.avatarUrl = ''
  }
}

const handlePersonaCardUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  personaCardImportInfo.value = ''
  personaCardImportError.value = ''
  personaAutoFillInfo.value = ''
  personaAutoFillError.value = ''
  avatarGenerateInfo.value = ''
  avatarGenerateError.value = ''
  personaCreateError.value = ''

  try {
    if (file.size > 10 * 1024 * 1024) {
      throw new Error('角色卡文件不能超过 10MB。')
    }

    const ext = file.name.toLowerCase()
    let rawPayloadText = ''
    let fallbackAvatar = ''

    if (file.type === 'application/json' || ext.endsWith('.json')) {
      rawPayloadText = await file.text()
    } else if (file.type === 'image/png' || ext.endsWith('.png')) {
      rawPayloadText = await parsePngCardTextChunks(file)
      fallbackAvatar = await readFileAsDataUrl(file)
    } else {
      throw new Error('角色卡仅支持 JSON 或 PNG 文件。')
    }

    const parsedPayload = tryParseCharacterPayload(rawPayloadText)
    if (!parsedPayload) {
      throw new Error('无法解析角色卡内容，请确认文件格式。')
    }

    const fallbackName = file.name.replace(/\.[^/.]+$/, '')
    const card = normalizePersonaCardPayload(parsedPayload, fallbackName)
    applyPersonaCardToForm(card, fallbackAvatar)

    if (!personaForm.systemPrompt.trim()) {
      personaCardImportError.value = '角色卡已导入，但缺少系统提示词，可手动补充或使用“AI自动补全未填写项”。'
    } else {
      personaCardImportInfo.value = `角色卡导入成功：${file.name}`
    }
  } catch (error: any) {
    personaCardImportError.value = error?.message || '角色卡导入失败，请重试。'
  } finally {
    input.value = ''
  }
}

const clearPersonaAvatar = () => {
  personaForm.avatarPreview = ''
  personaForm.avatarUrl = ''
  avatarGenerateInfo.value = ''
  avatarGenerateError.value = ''
}

const handlePersonaAvatarUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  avatarGenerateInfo.value = ''
  avatarGenerateError.value = ''

  const allowedTypes = ['image/png', 'image/jpeg', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    personaCreateError.value = '头像格式仅支持 PNG / JPG / WebP。'
    input.value = ''
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    personaCreateError.value = '头像大小不能超过 2MB。'
    input.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    personaForm.avatarPreview = String(reader.result || '')
    personaCreateError.value = ''
  }
  reader.onerror = () => {
    personaCreateError.value = '头像读取失败，请重试。'
  }
  reader.readAsDataURL(file)
}

const buildPersonaDescription = () => {
  const briefParts = [
    personaForm.nickname ? `昵称: ${personaForm.nickname}` : '',
    personaForm.age ? `年龄: ${personaForm.age}` : '',
    personaForm.gender ? `性别: ${personaForm.gender}` : '',
    personaForm.title ? `头衔: ${personaForm.title}` : ''
  ].filter(Boolean)

  const fullParts = [
    personaForm.description.trim(),
    briefParts.join(' | '),
    personaForm.personality.trim() ? `性格: ${personaForm.personality.trim()}` : '',
    personaForm.background.trim() ? `背景: ${personaForm.background.trim()}` : ''
  ].filter(Boolean)

  return fullParts.join('\n')
}

const focusPersonaCreatorField = async (
  field: 'name' | 'systemPrompt'
) => {
  await nextTick()
  const target = field === 'name' ? personaNameInputRef.value : personaSystemPromptRef.value
  if (!target) return
  target.focus()
  target.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

const createPersona = async () => {
  personaCreateError.value = ''

  if (!personaForm.name.trim()) {
    personaCreateError.value = '请填写角色名称。'
    await focusPersonaCreatorField('name')
    return
  }

  if (!personaForm.systemPrompt.trim()) {
    personaCreateError.value = '请填写系统提示词。'
    await focusPersonaCreatorField('systemPrompt')
    return
  }

  const avatar =
    personaForm.avatarPreview.trim() ||
    personaForm.avatarUrl.trim() ||
    `https://api.dicebear.com/7.x/notionists/svg?seed=${encodeURIComponent(personaForm.name.trim())}&backgroundColor=e0e7ff`

  const newPersona: Persona = {
    id: `custom_${Date.now()}`,
    name: personaForm.name.trim(),
    avatar,
    description: buildPersonaDescription() || tr('用户自定义角色', 'User custom role'),
    systemPrompt: personaForm.systemPrompt.trim(),
    gender: personaForm.gender.trim(),
    personality: personaForm.personality.trim(),
    firstMessage: personaForm.firstMessage.trim(),
    group: personaForm.group.trim() || defaultCustomPersonaGroup(),
    source: 'custom'
  }

  try {
    customPersonas.value = [newPersona, ...customPersonas.value]
    saveCustomPersonas()

    personas.value = [newPersona, ...personas.value]
    void assignPersonaLocationStatuses(personas.value)
    if (momentsHydrated.value) {
      syncMomentsDataWithPersonas()
      syncGroupChatsWithPersonas()
      refreshPersonaMomentSchedule(newPersona.id, Date.now(), true)
      ensureSelectedGroupChatReady()
      saveMomentsState()
      saveGroupChatsState()
    }
    await switchPersona(newPersona)
    showPersonaCreator.value = false
    resetPersonaForm()
  } catch (error: any) {
    personaCreateError.value = error?.message || '创建角色失败，请稍后重试。'
    if (showPersonaCreator.value && personaCreatorBodyRef.value) {
      await nextTick()
      personaCreatorBodyRef.value.scrollTo({ top: personaCreatorBodyRef.value.scrollHeight, behavior: 'smooth' })
    }
  }
}

const removeCustomPersona = async (persona: Persona) => {
  if (persona.source !== 'custom') return
  if (!confirm(`确认删除自定义角色「${persona.name}」吗？`)) return

  const wasCurrent = currentPersona.value.id === persona.id

  customPersonas.value = customPersonas.value.filter((item) => item.id !== persona.id)
  personas.value = personas.value.filter((item) => item.id !== persona.id)
  if (personas.value.length === 0) {
    personas.value = [...DEFAULT_PERSONAS]
  }
  void assignPersonaLocationStatuses(personas.value)

  try {
    saveCustomPersonas()
  } catch (error) {
    console.error('保存自定义角色失败:', error)
  }

  if (momentsHydrated.value) {
    syncMomentsDataWithPersonas()
    syncGroupChatsWithPersonas()
    ensureSelectedGroupChatReady()
    saveMomentsState()
    saveGroupChatsState()
  }

  if (wasCurrent && personas.value.length > 0) {
    try {
      await switchPersona(personas.value[0])
    } catch (error) {
      console.error('切换删除后的角色失败:', error)
      applySavedSelectedPersona(true)
    }
  }
}

const removePersonaAfterAvatarError = async (persona: Persona) => {
  const personaId = normalizeStorageText(persona?.id)
  if (!personaId) return

  const wasCurrent = normalizeStorageText(currentPersona.value?.id) === personaId
  const wasCustom = persona.source === 'custom'

  customPersonas.value = customPersonas.value.filter((item) => normalizeStorageText(item.id) !== personaId)
  personas.value = personas.value.filter((item) => normalizeStorageText(item.id) !== personaId)
  delete personaLocationStatusMap.value[personaId]
  savePersonaLocationStatusMap()

  if (personas.value.length === 0) {
    personas.value = [...DEFAULT_PERSONAS]
  }
  void assignPersonaLocationStatuses(personas.value)

  if (wasCustom) {
    try {
      saveCustomPersonas()
    } catch (error) {
      console.error('保存自定义角色失败:', error)
    }
  }

  if (momentsHydrated.value) {
    syncMomentsDataWithPersonas()
    syncGroupChatsWithPersonas()
    ensureSelectedGroupChatReady()
    saveMomentsState()
    saveGroupChatsState()
  }

  if (wasCurrent && personas.value.length > 0) {
    try {
      await switchPersona(personas.value[0])
    } catch (error) {
      console.error('切换删除后的角色失败:', error)
      applySavedSelectedPersona(true)
    }
    return
  }

  applySavedSelectedPersona(true)
}

const onPersonaAvatarError = (persona: Persona) => {
  const personaId = normalizeStorageText(persona?.id)
  if (!personaId) return
  if (personaAvatarErrorLock.has(personaId)) return
  personaAvatarErrorLock.add(personaId)

  if (persona.source === 'imported') {
    brokenImportedPersonaIds.add(personaId)
    saveBrokenImportedPersonaIds()
  }

  void removePersonaAfterAvatarError(persona).finally(() => {
    personaAvatarErrorLock.delete(personaId)
  })
}

const applyTheme = async (theme: ThemeItem) => {
  // Theme logic disabled for this layout
  alert('Third-party theme switching is disabled in this layout.')
}

const toggleScript = (script: Script) => {
  script.enabled = !script.enabled
  scriptEngine.saveScripts()
  if (script.enabled) {
    scriptEngine.runScript(script)
  } else {
    scriptEngine.stopScript(script)
  }
}

const editScript = (script: Script) => {
  Object.assign(currentScript, JSON.parse(JSON.stringify(script)))
  showScriptEditor.value = true
}

const createScript = () => {
  currentScript.id = Date.now().toString()
  currentScript.name = 'New Script'
  currentScript.version = '1.0.0'
  currentScript.enabled = true
  currentScript.code = '// SillyTavernAPI is available globally\nSillyTavernAPI.log("Script Loaded")\n'
  currentScript.description = ''
  showScriptEditor.value = true
}

const saveScript = () => {
  const index = scripts.value.findIndex(s => s.id === currentScript.id)
  if (index !== -1) {
    scripts.value[index] = { ...currentScript }
  } else {
    scripts.value.push({ ...currentScript })
  }
  scriptEngine.saveScripts()
  showScriptEditor.value = false
}

const deleteScript = (id: string) => {
  if (confirm('Are you sure you want to delete this script?')) {
    scripts.value = scripts.value.filter(s => s.id !== id)
    scriptEngine.saveScripts()
  }
}

const escapeHtml = (text: string) => {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

const sanitizeRenderedHtml = (html: string) => {
  if (typeof window === 'undefined') return html

  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')

  const blockedTags = [
    'style',
    'script',
    'iframe',
    'object',
    'embed',
    'link',
    'meta',
    'base',
    'form',
    'input',
    'button',
    'textarea',
    'select',
    'svg',
    'math',
    'video',
    'audio',
    'canvas'
  ]

  doc.querySelectorAll(blockedTags.join(',')).forEach((node) => node.remove())

  const allElements = Array.from(doc.body.querySelectorAll('*'))
  for (const element of allElements) {
    for (const attr of Array.from(element.attributes)) {
      const attrName = attr.name.toLowerCase()
      const attrValue = attr.value.trim()

      if (attrName === 'style' || attrName === 'class' || attrName === 'id' || attrName.startsWith('on')) {
        element.removeAttribute(attr.name)
        continue
      }

      if ((attrName === 'href' || attrName === 'src' || attrName === 'xlink:href') && /^(javascript:|vbscript:|data:text\/html)/i.test(attrValue)) {
        element.removeAttribute(attr.name)
      }
    }

    if (element.tagName === 'A') {
      element.setAttribute('target', '_blank')
      element.setAttribute('rel', 'noopener noreferrer nofollow')
    }
  }

  return doc.body.innerHTML
}

const renderMarkdown = (text: string) => {
  const escaped = escapeHtml(text ?? '')
  try {
    return sanitizeRenderedHtml(String(marked.parse(escaped)))
  } catch (e) {
    return sanitizeRenderedHtml(`<p>${escaped}</p>`)
  }
}

const decodeHtmlEntities = (input: string) => {
  if (typeof window === 'undefined') return input
  const textarea = document.createElement('textarea')
  textarea.innerHTML = input
  return textarea.value
}

const escapeClosingScriptTag = (input: string) => {
  return input.replace(/<\/script/gi, '<\\/script')
}

const collectFencedBlocks = (source: string) => {
  const blocks: Array<{ lang: string; code: string }> = []
  const regex = /```([a-zA-Z0-9_-]+)?\s*\n?([\s\S]*?)```/g
  let match: RegExpExecArray | null = null
  while ((match = regex.exec(source)) !== null) {
    blocks.push({
      lang: String(match[1] || '').toLowerCase(),
      code: String(match[2] || '').trim()
    })
  }
  return blocks
}

const composeHtmlFromFencedBlocks = (source: string) => {
  const blocks = collectFencedBlocks(source)
  if (blocks.length === 0) return null

  const htmlBlocks: string[] = []
  const cssBlocks: string[] = []
  const jsBlocks: string[] = []

  for (const block of blocks) {
    if (!block.code) continue
    if (block.lang === 'html' || block.lang === 'htm') {
      htmlBlocks.push(block.code)
      continue
    }
    if (block.lang === 'css') {
      cssBlocks.push(block.code)
      continue
    }
    if (block.lang === 'js' || block.lang === 'javascript' || block.lang === 'ts' || block.lang === 'typescript') {
      jsBlocks.push(block.code)
      continue
    }
    if (!block.lang && /<\/?(div|style|script|audio|video|img|table|form|input|button|iframe|section|main|header|footer|p|span|a)\b/i.test(block.code)) {
      htmlBlocks.push(block.code)
    }
  }

  if (htmlBlocks.length === 0) return null

  let combined = htmlBlocks.join('\n')
  if (cssBlocks.length > 0) {
    combined += `\n<style>\n${cssBlocks.join('\n\n')}\n</style>`
  }
  if (jsBlocks.length > 0) {
    combined += `\n<script>\n${escapeClosingScriptTag(jsBlocks.join('\n\n'))}\n<\\/script>`
  }
  return combined
}

const isLikelyRenderableHtml = (candidate: string) => {
  const standardTagMatches =
    candidate.match(
      /<\/?(?:html|head|body|style|script|div|span|p|a|img|audio|video|source|table|thead|tbody|tr|td|th|ul|ol|li|section|article|main|header|footer|nav|form|input|button|textarea|select|option|label|canvas|iframe|br|hr|h[1-6]|figure|figcaption|details|summary)\b[^>]*>/gi
    ) || []

  if (standardTagMatches.length === 0) return false

  const hasInteractiveOrMediaTag = /<(style|script|audio|video|iframe|canvas|svg|table|form|input|button|textarea|select)\b/i.test(candidate)
  const hasStyledContainer = /<(div|p|span|section|article|main|header|footer|a|img|table)\b[^>]*(style|class|id)\s*=/i.test(candidate)
  const hasAnyStandardClosingTag =
    /<\/(?:div|span|p|a|audio|video|table|tr|td|th|ul|ol|li|section|article|main|header|footer|nav|form|button|textarea|select|h[1-6]|figure|figcaption|details|summary|body|html)>/i.test(
      candidate
    )
  const hasRenderableInlineTag = /<(p|div|span|h[1-6]|br|hr)\b/i.test(candidate)

  if (hasInteractiveOrMediaTag || hasStyledContainer) return true
  return standardTagMatches.length >= 2 && (hasAnyStandardClosingTag || hasRenderableInlineTag)
}

const extractHtmlSnippet = (text: string) => {
  if (!text) return null

  const source = String(text).trim()
  if (!source) return null

  const composedFromBlocks = composeHtmlFromFencedBlocks(source)
  if (composedFromBlocks) {
    const decodedComposed = decodeHtmlEntities(composedFromBlocks)
    if (isLikelyRenderableHtml(decodedComposed)) {
      return decodedComposed
    }
  }

  const fencedMatches = Array.from(source.matchAll(/```(?:html|htm)?\s*([\s\S]*?)```/gi))
  const candidates = fencedMatches.length > 0 ? fencedMatches.map((match) => match[1]) : [source]

  for (const rawCandidate of candidates) {
    const decodedCandidate = decodeHtmlEntities(String(rawCandidate || '').trim())
    if (!decodedCandidate) continue
    if (isLikelyRenderableHtml(decodedCandidate)) {
      return decodedCandidate
    }
  }

  return null
}

const hasIsolatedHtmlSnippet = (text: string) => {
  return Boolean(extractHtmlSnippet(text))
}

const getMessageFrameId = (idx: number) => `msg-html-${idx}`

const getMessageFrameHeight = (idx: number) => {
  const id = getMessageFrameId(idx)
  return messageHtmlFrameHeights.value[id] || DEFAULT_HTML_FRAME_HEIGHT
}

const buildIsolatedHtmlDocument = (rawHtml: string, frameId: string) => {
  const safeFrameId = frameId.replace(/[^a-zA-Z0-9_-]/g, '')
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    html, body {
      margin: 0;
      padding: 0;
      background: #ffffff;
      overflow-x: hidden;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: #1f2937;
      line-height: 1.5;
    }
    * {
      box-sizing: border-box;
      max-width: 100%;
    }
    img, video, canvas, svg {
      max-width: 100%;
      height: auto;
    }
    table {
      display: block;
      overflow-x: auto;
      max-width: 100%;
    }
  </style>
</head>
<body>
${rawHtml}
<script>
  (function () {
    var source = '${HTML_FRAME_SOURCE}';
    var frameId = '${safeFrameId}';
    function postHeight() {
      try {
        var body = document.body;
        var doc = document.documentElement;
        var height = Math.max(
          body ? body.scrollHeight : 0,
          body ? body.offsetHeight : 0,
          doc ? doc.scrollHeight : 0,
          doc ? doc.offsetHeight : 0
        );
        parent.postMessage({ source: source, frameId: frameId, height: height }, '*');
      } catch (e) {}
    }
    window.addEventListener('load', postHeight);
    window.addEventListener('resize', postHeight);
    if (window.ResizeObserver && document.body) {
      var ro = new ResizeObserver(postHeight);
      ro.observe(document.body);
    }
    setTimeout(postHeight, 50);
    setTimeout(postHeight, 300);
    setTimeout(postHeight, 900);
  })();
<\/script>
</body>
</html>`
}

const getMessageHtmlSrcdoc = (msg: Message, idx: number) => {
  const snippet = extractHtmlSnippet(msg.content)
  if (!snippet) return ''
  return buildIsolatedHtmlDocument(snippet, getMessageFrameId(idx))
}

const isMessageCollapsible = (msg: Message) => {
  if (msg.isTyping) return false
  if (hasIsolatedHtmlSnippet(msg.content)) return false
  return (msg.content?.length || 0) > MESSAGE_COLLAPSE_THRESHOLD
}

const getRenderableMessageContent = (msg: Message) => {
  if (!isMessageCollapsible(msg) || msg.expanded) return msg.content
  return `${msg.content.slice(0, MESSAGE_COLLAPSE_THRESHOLD)}\n\n...`
}

const toggleMessageExpanded = (msg: Message) => {
  msg.expanded = !msg.expanded
}

const adjustHeight = () => {
  if (inputTextarea.value) {
    inputTextarea.value.style.height = 'auto'
    inputTextarea.value.style.height = `${Math.min(inputTextarea.value.scrollHeight, 160)}px`
  }
}

const insertVariable = (variable: string) => {
  const el = inputTextarea.value
  if (!el) return
  
  const start = el.selectionStart
  const end = el.selectionEnd
  const text = inputMessage.value
  
  inputMessage.value = text.substring(0, start) + variable + text.substring(end)
  showVariablePicker.value = false
  
  nextTick(() => {
    el.focus()
    el.selectionStart = el.selectionEnd = start + variable.length
  })
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    sendMessage()
  }
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const sanitizeContextText = (raw: string) => {
  return raw
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const buildRecentConversationContext = (limit = 8) => {
  const recent = messages.value.slice(-limit)
  if (recent.length === 0) return '暂无最近对话。'

  const lines: string[] = []
  for (const msg of recent) {
    const roleLabel = msg.role === 'assistant' ? currentPersona.value.name : msg.role === 'user' ? userDisplayName.value : '系统'
    const raw = msg.questData
      ? `[任务] ${msg.questData.quest || ''} ${msg.questData.description || ''}`
      : msg.mediaData
        ? `[${msg.mediaData.origin === 'user_upload' ? '用户上传' : 'AI生成'}${mediaLabelByType(msg.mediaData.type)}] ${msg.mediaData.name || ''} ${msg.content || ''}`
        : msg.content
    const clean = sanitizeContextText(String(raw || ''))
    if (!clean) continue
    lines.push(`${roleLabel}: ${clean.slice(0, 180)}`)
  }
  return lines.length > 0 ? lines.join('\n') : '暂无最近对话。'
}

const isSelfieLikeImageRequest = (text: string) => {
  const source = text.trim()
  if (!source) return false
  return /(自拍|自拍照|自拍图|本人照|大头照|自画像|发我照片|来张照|来张自拍|发张自拍|拍张照|拍照)/i.test(source)
}

const resolvePersonaAvatarUrl = (avatar: string) => {
  const raw = avatar.trim()
  if (!raw) return ''
  if (/^(https?:|data:|blob:)/i.test(raw)) return raw
  if (raw.startsWith('/')) return `${window.location.origin}${raw}`
  return `${window.location.origin}/${raw.replace(/^\.?\//, '')}`
}

const buildImageIdentityHint = (userGuidance: string) => {
  const avatarUrl = resolvePersonaAvatarUrl(currentPersona.value.avatar || '')
  const selfieHint = isSelfieLikeImageRequest(userGuidance)
    ? '用户需求偏自拍，请使用近景/半身自拍构图，保留自然生活感。'
    : '请保持角色核心外观稳定，避免出现与角色卡明显不一致的人物特征。'

  const lines = [
    '生成要求：以当前角色卡头像为主参考，保持五官、发型、年龄气质与角色身份一致。',
    selfieHint,
    avatarUrl ? `参考头像URL：${avatarUrl}` : ''
  ].filter(Boolean)
  return lines.join('\n')
}

const loadPersonaAvatarReferenceFile = async () => {
  const avatarUrl = resolvePersonaAvatarUrl(currentPersona.value.avatar || '')
  if (!avatarUrl) return null

  try {
    const response = await fetch(avatarUrl)
    if (!response.ok) return null
    const blob = await response.blob()
    if (!blob.type || !blob.type.startsWith('image/')) return null

    const extension =
      blob.type === 'image/png'
        ? 'png'
        : blob.type === 'image/jpeg'
          ? 'jpg'
          : blob.type === 'image/webp'
            ? 'webp'
            : 'png'
    return new File([blob], `persona-reference.${extension}`, { type: blob.type || 'image/png' })
  } catch {
    return null
  }
}

const buildMediaPromptFromContext = (type: MediaType, userGuidance: string) => {
  const typeHint =
    type === 'image'
      ? '请生成一张符合当前剧情氛围的角色相关图片，构图清晰，主体突出。'
      : type === 'video'
        ? '请生成一段短视频分镜提示，突出角色动作、镜头运动和环境氛围。'
        : '请生成适合语音播报的台词内容，语气自然，贴合当前剧情。'

  const personaSystemPrompt = sanitizeContextText(currentPersona.value.systemPrompt || '').slice(0, 360)
  const personaDescription = sanitizeContextText(currentPersona.value.description || '').slice(0, 240)
  const context = buildRecentConversationContext()
  const guidance = userGuidance.trim() || '无额外要求'
  const imageIdentityHint = type === 'image' ? buildImageIdentityHint(guidance) : ''

  return [
    typeHint,
    `当前角色：${currentPersona.value.name}`,
    personaDescription ? `角色简介：${personaDescription}` : '',
    personaSystemPrompt ? `角色设定摘要：${personaSystemPrompt}` : '',
    imageIdentityHint,
    `最近对话：\n${context}`,
    `用户补充要求：${guidance}`
  ]
    .filter(Boolean)
    .join('\n')
}

const extractMediaUrlFromPayload = (payload: any) => {
  return pickFirstString(
    payload?.url,
    payload?.data?.[0]?.url,
    payload?.output?.[0]?.url,
    payload?.image_url,
    payload?.video?.url,
    payload?.audio?.url
  )
}

const openMediaGenerator = (type: MediaType) => {
  if (showMediaGenerator.value && activeMediaType.value === type) {
    showMediaGenerator.value = false
    return
  }
  activeMediaType.value = type
  showMediaGenerator.value = true
  mediaGenerateInfo.value = ''
  mediaGenerateError.value = ''
}

const detectMediaIntentFromText = (text: string): MediaType | null => {
  const source = text.trim()
  if (!source) return null

  const hasAction = /(发|来|给我|帮我|生成|做|制作|创建|整|弄|画|绘|播报|朗读|读|说|配)/i.test(source)
  const audioNegated =
    /(?:不是|不要|别|不想|无需|不需要|并非)\s*(?:发|来|做|生成|播报|朗读|读|说|配)?\s*(?:语音|音频|voice|tts)/i.test(source) ||
    /(?:语音|音频|voice|tts)\s*(?:不用|不要|别|不需要|无需)/i.test(source)
  const askAudio =
    /(语音|音频|voice|tts)/i.test(source) &&
    hasAction &&
    !audioNegated
  const askVideo =
    /(视频|动画|短片|录像|mv)/i.test(source) &&
    hasAction
  const askImage =
    /(图片|图像|插画|海报|壁纸|头像|照片|相片|自拍|自拍照|拍照|写真|发图|来图|配图|发张图|来张图|画一张|生成图|出图|ai图|photo|pic)/i.test(source) &&
    hasAction
  const askPhotoLike =
    /(自拍|自拍照|拍照|来张照|发张照|来张自拍|发张自拍)/i.test(source) &&
    /(发|来|给我|帮我|生成|拍|做|整|弄)/i.test(source)

  if (askAudio || /发条语音|语音条|读给我听|说给我听|来段语音/i.test(source)) return 'audio'
  if (askVideo) return 'video'
  if (askImage || askPhotoLike) return 'image'
  return null
}

const sanitizeMediaCommandGuidance = (text: string) => {
  return text
    .replace(/(请|帮我|给我|来|发|整|弄|生成|做|制作|创建|输出|播报|朗读|读|说|配|一下|一段|一条|一个|吧|呀|啊)/gi, ' ')
    .replace(/(语音|音频|voice|tts|视频|动画|短片|录像|mv|图片|图像|插画|海报|壁纸|头像|照片|发图|来图|配图)/gi, ' ')
    .replace(/[，。！？,.!?]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const buildAudioConversationContext = (limit = 8) => {
  const recent = messages.value.slice(-limit)
  if (recent.length === 0) return '暂无最近对话。'

  const lines: string[] = []
  for (const msg of recent) {
    const raw = sanitizeContextText(msg.content || '')
    if (!raw) continue
    if (msg.role === 'user' && detectMediaIntentFromText(raw) === 'audio') continue
    const roleLabel = msg.role === 'assistant' ? currentPersona.value.name : msg.role === 'user' ? userDisplayName.value : '系统'
    lines.push(`${roleLabel}: ${raw.slice(0, 180)}`)
  }
  return lines.length > 0 ? lines.join('\n') : '暂无最近对话。'
}

const registerObjectUrl = (src: string) => {
  if (!src.startsWith('blob:')) return
  if (trackedObjectUrls.value.includes(src)) return
  trackedObjectUrls.value.push(src)
}

const revokeObjectUrl = (src: string) => {
  if (!src.startsWith('blob:')) return
  const index = trackedObjectUrls.value.indexOf(src)
  if (index < 0) return
  URL.revokeObjectURL(src)
  trackedObjectUrls.value.splice(index, 1)
}

const releaseMessageMedia = (msg: Message | undefined) => {
  if (!msg?.mediaData?.src) return
  revokeObjectUrl(msg.mediaData.src)
}

const releaseAllMessageMedia = (items: Message[]) => {
  items.forEach((msg) => releaseMessageMedia(msg))
}

const formatFileSize = (size: number) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const getMediaTypeFromFile = (file: File): MediaType | null => {
  if (file.type.startsWith('image/')) return 'image'
  if (file.type.startsWith('video/')) return 'video'
  if (file.type.startsWith('audio/')) return 'audio'

  const name = file.name.toLowerCase()
  if (/\.(png|jpg|jpeg|webp|gif|bmp)$/.test(name)) return 'image'
  if (/\.(mp4|webm|mov|mkv|avi)$/.test(name)) return 'video'
  if (/\.(mp3|wav|ogg|m4a|aac|flac)$/.test(name)) return 'audio'
  return null
}

const serializeMessageForModel = (msg: Message) => {
  if (msg.questData) {
    return `[QUEST: ${msg.questData.quest}] ${msg.questData.description || ''}`.trim()
  }
  if (msg.mediaData) {
    const mediaSummary = `[MEDIA:${msg.mediaData.type}] ${msg.mediaData.origin === 'user_upload' ? 'user-uploaded' : 'ai-generated'} ${msg.mediaData.name || ''}`.trim()
    return msg.content ? `${mediaSummary}\n${msg.content}` : mediaSummary
  }
  return msg.content
}

const openUserMediaPicker = () => {
  userMediaUploadInfo.value = ''
  userMediaUploadError.value = ''
  const input = userMediaInputRef.value
  if (!input) return
  input.value = ''
  input.click()
}

const handleUserMediaUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  userMediaUploadInfo.value = ''
  userMediaUploadError.value = ''

  const mediaType = getMediaTypeFromFile(file)
  if (!mediaType) {
    userMediaUploadError.value = '仅支持上传图片、视频或语音文件。'
    input.value = ''
    return
  }

  const sizeLimit = mediaType === 'image' ? 10 * 1024 * 1024 : mediaType === 'audio' ? 30 * 1024 * 1024 : 80 * 1024 * 1024
  if (file.size > sizeLimit) {
    const limitLabel = formatFileSize(sizeLimit)
    userMediaUploadError.value = `${mediaLabelByType(mediaType)}文件过大，最大支持 ${limitLabel}。`
    input.value = ''
    return
  }

  const src = URL.createObjectURL(file)
  registerObjectUrl(src)

  const caption = inputMessage.value.trim()
  inputMessage.value = ''
  if (inputTextarea.value) inputTextarea.value.style.height = 'auto'

  messages.value.push({
    role: 'user',
    content: caption,
    mediaData: {
      type: mediaType,
      src,
      name: file.name,
      mimeType: file.type,
      sizeLabel: formatFileSize(file.size),
      origin: 'user_upload'
    }
  })

  userMediaUploadInfo.value = `已发送${mediaLabelByType(mediaType)}：${file.name}`
  await scrollToBottom()
  input.value = ''
  await fetchAssistantResponse()
}

const pushMediaResultMessage = (
  type: MediaType,
  mediaSrc: string,
  prompt: string,
  narrationText = '',
  options: { fromChatRequest?: boolean } = {}
) => {
  registerObjectUrl(mediaSrc)
  if (type === 'audio') {
    const transcript = normalizeNarrationText(narrationText)
    messages.value.push({
      role: 'assistant',
      content: transcript || (options.fromChatRequest ? '' : '（语音已生成）'),
      mediaData: {
        type,
        src: mediaSrc,
        origin: 'ai_generated'
      }
    })
    return
  }

  const textParts = [`提示词：${prompt}`]
  messages.value.push({
    role: 'assistant',
    content: textParts.join('\n'),
    mediaData: {
      type,
      src: mediaSrc,
      origin: 'ai_generated'
    }
  })
}

const buildAudioNarrationFallback = (guidance: string) => {
  const latestAssistantText = [...messages.value]
    .reverse()
    .find((msg) => msg.role === 'assistant' && !msg.mediaData && !msg.questData && msg.content.trim())?.content
  const cleanedAssistant = normalizeNarrationText(latestAssistantText || '')
  if (cleanedAssistant) return cleanedAssistant.slice(0, 280)

  const cleanedGuidance = sanitizeContextText(guidance || '')
  if (cleanedGuidance && !detectMediaIntentFromText(cleanedGuidance)) {
    return cleanedGuidance.slice(0, 180)
  }
  return '我在这里，继续和你聊刚才的话题。'
}

const generateAudioNarrationText = async (baseUrl: string, userGuidance: string) => {
  const guidance = sanitizeMediaCommandGuidance(userGuidance)
  const context = buildAudioConversationContext(8)
  const personaDescription = sanitizeContextText(currentPersona.value.description || '').slice(0, 240)
  const systemPrompt = buildEffectiveSystemPrompt()
  const configuredModel = apiSettings.value.modelName.trim()
  const textModelCandidates = Array.from(new Set([configuredModel, 'gpt-4o-mini', 'gpt-4.1-mini', 'gpt-3.5-turbo'].filter(Boolean)))
  let lastError = ''

  const narrationInstruction = [
    '请输出一段可直接用于语音播放的角色回复台词。',
    '要求：仅输出最终台词，不要解释，不要加引号，不要出现“提示词/系统/上下文”等字样。',
    '要求：贴合角色设定与最近剧情，不要复述“发语音/生成语音”等操作指令。',
    `当前角色：${currentPersona.value.name}`,
    personaDescription ? `角色简介：${personaDescription}` : '',
    `最近对话：\n${context}`,
    `用户偏好：${guidance || '无额外偏好'}`,
    '长度建议：1-3句话，80字以内。'
  ]
    .filter(Boolean)
    .join('\n')

  for (const model of textModelCandidates) {
    try {
      const response = await fetch(`${baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiSettings.value.apiKey}`
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: narrationInstruction }
          ],
          max_tokens: 180,
          temperature: 0.9,
          stream: false
        })
      })

      if (!response.ok) {
        lastError = await readResponseErrorMessage(response)
        continue
      }

      const payload = await response.json()
      const content = normalizeNarrationText(extractChatTextContent(payload))
      if (content) return content.slice(0, 280)
      lastError = '台词生成接口返回成功，但内容为空。'
    } catch (error: any) {
      lastError = error?.message || '台词生成请求失败'
    }
  }

  if (lastError) {
    console.warn('[AudioNarration] fallback to local text:', lastError)
  }
  return buildAudioNarrationFallback(guidance)
}

const generateAudioFromContext = async (baseUrl: string, modelCandidates: string[], userGuidance: string) => {
  const narrationText = await generateAudioNarrationText(baseUrl, userGuidance)
  const voiceInstruction = buildAudioVoiceInstruction()
  const speechRate = Math.min(1.35, Math.max(0.75, Number(mediaSpeechRate.value) || 1))
  const forcedGender = detectVoiceGenderHintFromText(userGuidance)
  const ttsConfig = resolveTtsConfig()
  const voiceCandidates = resolveVoiceCandidatesByPersona(
    currentPersona.value,
    mediaVoice.value,
    voiceToolboxSettings.value,
    forcedGender
  )
  let lastError = ''

  if (ttsConfig.ttsProvider === 'coqui') {
    if (!ttsConfig.coquiBaseUrl) {
      throw new Error('请先在设置中填写 Coqui 接口地址。')
    }

    for (const voice of voiceCandidates) {
      try {
        const coquiAudio = await requestCoquiAudioSynthesis(ttsConfig, {
          text: narrationText,
          voiceHint: voice,
          speed: speechRate
        })
        return {
          src: coquiAudio.src,
          model: ttsConfig.coquiModelName,
          narrationText,
          voiceUsed: coquiAudio.speakerUsed || voice
        }
      } catch (error: any) {
        lastError = error?.message || 'Coqui 语音生成失败'
      }
    }

    throw new Error(lastError || 'Coqui 语音生成失败，请检查 Coqui 模型和 Speaker 配置。')
  }

  for (const model of modelCandidates) {
    for (const voice of voiceCandidates) {
      const basePayload = {
        model,
        voice,
        input: narrationText,
        response_format: 'mp3'
      }
      const payloadVariants = [
        voiceInstruction ? { ...basePayload, instructions: voiceInstruction, speed: speechRate } : null,
        { ...basePayload, speed: speechRate },
        basePayload
      ].filter(Boolean) as Record<string, any>[]

      for (const payloadBody of payloadVariants) {
        const response = await fetch(`${baseUrl}/audio/speech`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiSettings.value.apiKey}`
          },
          body: JSON.stringify(payloadBody)
        })

        if (!response.ok) {
          lastError = await readResponseErrorMessage(response)
          continue
        }

        const contentType = response.headers.get('content-type') || ''
        if (contentType.includes('audio/')) {
          const blob = await response.blob()
          return {
            src: URL.createObjectURL(blob),
            model,
            narrationText,
            voiceUsed: voice
          }
        }

        const payload = await response.json()
        const directUrl = extractMediaUrlFromPayload(payload)
        if (directUrl) {
          return { src: directUrl, model, narrationText, voiceUsed: voice }
        }

        const b64 = pickFirstString(
          payload?.audio,
          payload?.audio_base64,
          payload?.data?.[0]?.b64_json,
          payload?.data?.[0]?.base64
        )
        if (b64) {
          const src = b64.startsWith('data:audio/') ? b64 : `data:audio/mpeg;base64,${b64}`
          return { src, model, narrationText, voiceUsed: voice }
        }

        lastError = '语音接口返回成功，但未解析到音频数据。'
      }
    }
  }

  throw new Error(lastError || '语音生成失败，请确认 API 支持 /audio/speech。')
}

const generateVideoFromContext = async (baseUrl: string, modelCandidates: string[], prompt: string) => {
  let lastError = ''

  for (const model of modelCandidates) {
    const createResponse = await fetch(`${baseUrl}/videos/generations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model,
        prompt,
        duration: 5
      })
    })

    if (!createResponse.ok) {
      lastError = await readResponseErrorMessage(createResponse)
      continue
    }

    const payload = await createResponse.json()
    const directUrl = extractMediaUrlFromPayload(payload)
    if (directUrl) {
      return { src: directUrl, model }
    }

    const videoJobId = pickFirstString(payload?.id, payload?.data?.[0]?.id, payload?.output?.[0]?.id)
    if (!videoJobId) {
      lastError = '视频任务已创建，但未返回可查询的任务ID。'
      continue
    }

    for (let attempt = 0; attempt < 15; attempt += 1) {
      await sleep(2500)
      const pollResponse = await fetch(`${baseUrl}/videos/generations/${encodeURIComponent(videoJobId)}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiSettings.value.apiKey}`
        }
      })

      if (!pollResponse.ok) {
        lastError = await readResponseErrorMessage(pollResponse)
        break
      }

      const pollPayload = await pollResponse.json()
      const pollUrl = extractMediaUrlFromPayload(pollPayload)
      if (pollUrl) {
        return { src: pollUrl, model }
      }

      const status = pickFirstString(pollPayload?.status, pollPayload?.data?.[0]?.status).toLowerCase()
      if (status === 'failed' || status === 'cancelled' || status === 'canceled') {
        lastError = pickFirstString(pollPayload?.error?.message, pollPayload?.message, '视频生成任务失败。')
        break
      }
    }
  }

  throw new Error(lastError || '视频生成失败，请确认 API 支持 /videos/generations。')
}

const generateMediaFromContext = async (
  forcedType?: MediaType,
  forcedGuidance?: string,
  fromChatRequest = false
) => {
  if (isGeneratingMedia.value) return
  mediaGenerateInfo.value = ''
  mediaGenerateError.value = ''

  const normalizedForcedType: MediaType | undefined =
    forcedType === 'image' || forcedType === 'video' || forcedType === 'audio'
      ? forcedType
      : undefined
  const targetType = normalizedForcedType || activeMediaType.value
  const targetLabel = mediaLabelByType(targetType)
  const textApiConfig = resolveTextApiConfig()
  const imageApiConfig = resolveImageApiConfig()
  const ttsConfig = resolveTtsConfig()
  const requiresImageApi = targetType === 'image'
  const requiresAudioApi = targetType === 'audio'
  const requiresTextApi = !requiresImageApi

  if (requiresImageApi && (!imageApiConfig.baseUrl || !imageApiConfig.apiKey)) {
    mediaGenerateError.value = '请先在设置中填写并保存可用的 AI 生图接口（Base URL 与 API Key）。'
    if (fromChatRequest) {
      messages.value.push({ role: 'assistant', content: `[System]: ${mediaGenerateError.value}` })
      await scrollToBottom()
    }
    return
  }

  if (requiresTextApi && (!textApiConfig.baseUrl || !textApiConfig.apiKey)) {
    mediaGenerateError.value = targetType === 'audio'
      ? '请先在设置中填写并保存文本接口（Base URL 与 API Key），用于生成语音台词。'
      : '请先在设置中填写并保存可用的文本接口（Base URL 与 API Key）。'
    if (fromChatRequest) {
      messages.value.push({ role: 'assistant', content: `[System]: ${mediaGenerateError.value}` })
      await scrollToBottom()
    }
    return
  }

  if (requiresAudioApi && ttsConfig.ttsProvider === 'coqui' && !ttsConfig.coquiBaseUrl) {
    mediaGenerateError.value = '当前语音引擎为 Coqui，请先配置 Coqui 接口地址。'
    if (fromChatRequest) {
      messages.value.push({ role: 'assistant', content: `[System]: ${mediaGenerateError.value}` })
      await scrollToBottom()
    }
    return
  }

  const baseUrl = textApiConfig.baseUrl
  const guidance = typeof forcedGuidance === 'string' ? forcedGuidance.trim() : mediaPromptInput.value.trim()
  const prompt = buildMediaPromptFromContext(targetType, guidance)
  const configuredModel = textApiConfig.modelName
  const imageModels = buildImageModelCandidates(imageApiConfig)
  const videoModels = Array.from(new Set([configuredModel, 'gpt-video-1'].filter(Boolean)))
  const audioModels = buildAudioModelCandidates(configuredModel)

  isGeneratingMedia.value = true
  try {
    if (targetType === 'image') {
      let lastError = ''
      let result: { src: string; model: string; via?: 'edits' | 'generations' } | null = null
      const shouldPreferAvatarReference = isSelfieLikeImageRequest(guidance)
      const avatarReferenceFile = shouldPreferAvatarReference ? await loadPersonaAvatarReferenceFile() : null

      if (avatarReferenceFile) {
        for (const model of imageModels) {
          try {
            const decoded = await requestImageWithModel(imageApiConfig, model, prompt, { referenceFile: avatarReferenceFile })
            result = { src: decoded.src, model, via: 'edits' }
            break
          } catch (error: any) {
            lastError = error?.message || '图片编辑失败'
            continue
          }
        }
      }

      if (!result) {
        for (const model of imageModels) {
          try {
            const decoded = await requestImageWithModel(imageApiConfig, model, prompt)
            result = { src: decoded.src, model, via: 'generations' }
            break
          } catch (error: any) {
            lastError = error?.message || '图片生成失败'
            continue
          }
        }
      }

      if (!result) throw new Error(lastError || '图片生成失败，请确认 AI 生图接口支持 Gemini v1beta 或 /images/generations。')

      pushMediaResultMessage('image', result.src, prompt)
      mediaGenerateInfo.value = shouldPreferAvatarReference
        ? `图片生成成功（模型：${result.model}，${result.via === 'edits' ? '已参考角色头像' : '已回退普通生图'}）。`
        : `图片生成成功（模型：${result.model}）。`
      await scrollToBottom()
      return
    }

    if (targetType === 'video') {
      const result = await generateVideoFromContext(baseUrl, videoModels, prompt)
      pushMediaResultMessage('video', result.src, prompt)
      mediaGenerateInfo.value = `视频生成成功（模型：${result.model}）。`
      await scrollToBottom()
      return
    }

    const audioResult = await generateAudioFromContext(baseUrl, audioModels, guidance)
    pushMediaResultMessage('audio', audioResult.src, prompt, audioResult.narrationText, { fromChatRequest })
    const voiceLabel = ttsConfig.ttsProvider === 'coqui' ? audioResult.voiceUsed : getVoiceLabel(audioResult.voiceUsed)
    mediaGenerateInfo.value = `语音生成成功（引擎：${ttsConfig.ttsProvider === 'coqui' ? 'Coqui' : 'OpenAI兼容'}，模型：${audioResult.model}，音色：${voiceLabel}）。`
    await scrollToBottom()
  } catch (error: any) {
    mediaGenerateError.value = error?.message || `AI${targetLabel}生成失败，请稍后重试。`
    if (fromChatRequest) {
      messages.value.push({ role: 'assistant', content: `[System]: ${mediaGenerateError.value}` })
      await scrollToBottom()
    }
  } finally {
    isGeneratingMedia.value = false
  }
}

const switchPersona = async (persona: Persona) => {
  currentPersona.value = persona
  persistSelectedPersonaId(persona.id)
  if (!personaLocationStatusMap.value[String(persona.id)]) {
    void assignPersonaLocationStatuses([persona])
  }
  
  // Clear history for new chat
  releaseAllMessageMedia(messages.value)
  messages.value = []
  
  // 1. Send Character Card
  messages.value.push({
    role: 'assistant',
    content: '',
    cardData: {
      name: persona.name,
      description: persona.description,
      avatar: persona.avatar,
      systemPrompt: persona.systemPrompt
    }
  })
  
  // 2. Send First Message
  try {
    let firstMes = (persona as any).firstMessage || ''
    
    if (!firstMes && persona.file) {
        const res = await fetch(`/characters/${persona.file}`)
        if (res.ok) {
            const data = await res.json()
            if (data.originalData) {
                const od = data.originalData
                firstMes = od.first_mes || od.data?.first_mes || od.char_persona?.first_mes || ''
            }
            if (!firstMes && data.systemPrompt) {
               // If fetched but no first_mes, use system prompt as fallback basis? 
               // Maybe not, as system prompt is for the AI.
            }
        }
    }
    
    // Fallback if no first_mes found in file or no file
    if (!firstMes) {
       firstMes = `*${persona.name} looks at you and waits for your reply.*`
    }
    
    if (firstMes) {
        // Replace {{user}} variable
        firstMes = firstMes.replace(/{{user}}/g, userDisplayName.value)
        
        messages.value.push({
            role: 'assistant',
            content: firstMes
        })
    }
  } catch (e) {
      console.error('Failed to load character details:', e)
  }
}

const switchGame = (game: GameConfig) => {
  currentGame.value = game
  showGameSelector.value = false
  messages.value.push({
    role: 'system',
    content: `[System]: switched to ${game.name}.`
  })
}

const openGameEditor = (game?: GameConfig) => {
  if (game) {
    Object.assign(tempGame, JSON.parse(JSON.stringify(game)))
    tempGameQuests.value = JSON.stringify(game.quests, null, 2)
  } else {
    tempGame.id = Date.now().toString()
    tempGame.name = 'New Game'
    tempGame.themeColor = '#22c55e'
    tempGame.bgGradient = ''
    tempGame.npcRole = ''
    tempGame.bgImage = ''
    tempGameQuests.value = '[\n  { "title": "任务示例", "reward": "100积分", "link": "#" }\n]'
  }
  showGameEditor.value = true
  showGameSelector.value = false
}

const saveGame = () => {
  try {
    const quests: Quest[] = JSON.parse(tempGameQuests.value)
    const newGame = { ...tempGame, quests }
    
    const index = games.value.findIndex(g => g.id === newGame.id)
    if (index !== -1) {
      games.value[index] = newGame
    } else {
      games.value.push(newGame)
    }
    
    localStorage.setItem('cypher_tavern_games', JSON.stringify(games.value))
    currentGame.value = newGame
    showGameEditor.value = false
  } catch (e) {
    alert('任务 JSON 格式错误，请检查后重试。')
  }
}

const clearHistory = () => {
  if (confirm('Clear current chat history?')) {
    releaseAllMessageMedia(messages.value)
    messages.value = []
  }
}

const quickStart = (text: string) => {
  inputMessage.value = text
  sendMessage()
}

const openSettingsPanel = () => {
  tempSettings.value = { ...apiSettings.value }
  tempVoiceToolboxSettings.value = { ...voiceToolboxSettings.value }
  testStatus.value = { success: false, message: '' }
  imageTestStatus.value = { success: false, message: '' }
  showSettings.value = true
}

const openNovelStoryPage = () => {
  showSettings.value = false
  router.push('/novel-story').catch(() => undefined)
}

const openPlazaPage = () => {
  showSettings.value = false
  router.push('/plaza').catch(() => undefined)
}

const openCharacterModal = (data: CharacterCardData) => {
  characterModalData.value = data
  showCharacterModal.value = true
}

const saveSettings = () => {
  apiSettings.value = {
    ...tempSettings.value,
    coquiSpeaker: normalizeCoquiSpeakerValue(tempSettings.value.coquiSpeaker),
  }
  localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(apiSettings.value))
  localStorage.setItem(SETTINGS_STORAGE_KEY_V2, JSON.stringify({ apiSettings: { ...apiSettings.value } }))
  persistVoiceToolboxSettings(tempVoiceToolboxSettings.value)
  tempVoiceToolboxSettings.value = { ...voiceToolboxSettings.value }
  if (personas.value.length > LOCAL_PERSONA_LOCATION_POOL.length && isConnected.value) {
    void assignPersonaLocationStatuses(personas.value, true)
  }
  if (isConnected.value) {
    void ensureMomentsTrendContext(true)
  }
  showSettings.value = false
}

const resetVisualSettings = () => {
  // Deprecated
}

const testConnection = async () => {
  if (!tempSettings.value.apiKey || !tempSettings.value.baseUrl) {
    testStatus.value = { success: false, message: 'Please fill Base URL and API Key first.' }
    return
  }

  isTesting.value = true
  testStatus.value = { success: false, message: '' }

  try {
    const response = await fetch(`${tempSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tempSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model: tempSettings.value.modelName,
        messages: [{ role: 'user', content: 'Test' }],
        max_tokens: 5
      })
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    testStatus.value = { success: true, message: 'Connection successful.' }
  } catch (e: any) {
    testStatus.value = { success: false, message: `Connection failed: ${e.message}` }
  } finally {
    isTesting.value = false
  }
}

const resolveTempImageApiConfig = (): ResolvedImageApiConfig => {
  const imageApiType = normalizeImageApiType(tempSettings.value.imageApiType)
  return {
    baseUrl: normalizeApiBaseUrl(tempSettings.value.imageBaseUrl || tempSettings.value.baseUrl),
    apiKey: String(tempSettings.value.imageApiKey || tempSettings.value.apiKey || '').trim(),
    modelName:
      String(tempSettings.value.imageModelName || tempSettings.value.modelName || '').trim() ||
      defaultImageModelByType(imageApiType),
    imageApiType,
  }
}

const testImageConnection = async () => {
  const imageConfig = resolveTempImageApiConfig()
  if (!imageConfig.baseUrl || !imageConfig.apiKey) {
    imageTestStatus.value = { success: false, message: '请先填写 Image Base URL 和 Image API Key。' }
    return
  }

  isTestingImage.value = true
  imageTestStatus.value = { success: false, message: '' }

  const modelCandidates = buildImageModelCandidates(imageConfig)
  let lastError = ''

  try {
    for (const model of modelCandidates) {
      try {
        const decoded = await requestImageWithModel(
          imageConfig,
          model,
          '请生成一张白色背景的蓝色圆形图标，简洁风格。'
        )
        if (decoded?.src) {
          imageTestStatus.value = { success: true, message: `生图连接成功（模型：${model}）。` }
          return
        }
        lastError = '接口已响应，但未返回可用图片数据。'
      } catch (error: any) {
        lastError = error?.message || '生图连接失败'
      }
    }
    throw new Error(lastError || '生图连接失败')
  } catch (error: any) {
    imageTestStatus.value = { success: false, message: `生图连接失败：${error?.message || '未知错误'}` }
  } finally {
    isTestingImage.value = false
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const typeText = async (fullText: string) => {
  const msgIndex = messages.value.length - 1
  messages.value[msgIndex].isTyping = true
  
  let contentToType = fullText

  // Try parsing JSON first
  try {
    const jsonMatch = fullText.match(/\{[\s\S]*"quest"[\s\S]*\}/)
    if (jsonMatch) {
      const jsonContent = JSON.parse(jsonMatch[0])
      if (jsonContent.quest && jsonContent.type) {
        messages.value[msgIndex].questData = jsonContent
        // Remove JSON from the text to be typed, but keep surrounding text
        contentToType = fullText.replace(jsonMatch[0], '').trim()
      }
    }
  } catch (e) {
    // Not valid JSON, continue normal typing
  }  // Try parsing Text Format [Quest]
  if (!messages.value[msgIndex].questData) {
    const questMatch = fullText.match(/\[Quest\]\s*\*\*?(.*?)\*\*?[\r\n]+-.*?:\s*(.*?)(?:[\r\n]+|$)-.*?:\s*(.*?)(?:[\r\n]+|$)-.*?:\s*(?:\[(.*?)\]\((.*?)\))?/)
    if (questMatch) {
      messages.value[msgIndex].questData = {
        quest: questMatch[1],
        type: 'quest',
        description: questMatch[2],
        reward: questMatch[3],
        link: questMatch[5],
        linkText: questMatch[4]
      }
      // Remove the quest block from visible text to avoid duplication
      contentToType = fullText.replace(questMatch[0], '').trim()
    }
  }

  messages.value[msgIndex].content = ''
  
  if (!contentToType) {
    // Sanitize link if it's a placeholder or invalid
    if (messages.value[msgIndex].questData && messages.value[msgIndex].questData.link) {
      const link = messages.value[msgIndex].questData.link
      const questTitle = messages.value[msgIndex].questData.quest
      if (link.includes('example.com') || link.includes('community.com') || link.includes('wiki.com') || link === '#') {
        messages.value[msgIndex].questData.link = `https://www.google.com/search?q=${encodeURIComponent(questTitle)}`
      }
    }

    messages.value[msgIndex].isTyping = false
    return
  }

  const chunkSize = 2
  let current = 0
  
  return new Promise<void>((resolve) => {
    const interval = setInterval(() => {
      if (current >= contentToType.length) {
        clearInterval(interval)
        messages.value[msgIndex].isTyping = false
        resolve()
        return
      }
      messages.value[msgIndex].content += contentToType.slice(current, current + chunkSize)
      current += chunkSize
      scrollToBottom()
    }, 10)
  })
}

const fetchAssistantResponse = async () => {
  isTyping.value = true
  const finalSystemPrompt = buildEffectiveSystemPrompt()

  try {
    const response = await fetch(`${apiSettings.value.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiSettings.value.apiKey}`
      },
      body: JSON.stringify({
        model: apiSettings.value.modelName,
        messages: [
          { role: 'system', content: finalSystemPrompt },
          ...messages.value.map(m => ({ 
            role: m.role, 
            content: serializeMessageForModel(m)
          }))
        ],
        stream: false
      })
    })

    if (!response.ok) throw new Error(`API Error: ${response.status}`)

    const data = await response.json()
    const reply = data.choices?.[0]?.message?.content || '(No response)'
    
    messages.value.push({ role: 'assistant', content: '' })
    await typeText(reply)
    
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `[System Error]: ${error.message}` })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const regenerateLast = async () => {
  if (isTyping.value || messages.value.length === 0) return
  
  // If last message is assistant, remove it
  if (messages.value[messages.value.length - 1].role === 'assistant') {
    const removed = messages.value.pop()
    releaseMessageMedia(removed)
  }
  
  // Check if we have a user message to reply to
  if (messages.value.length > 0) {
    await fetchAssistantResponse()
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return

  const userText = inputMessage.value.trim()
  try {
    guardUsagePolicyContent(userText, 'chat')
  } catch (error) {
    if (isUsagePolicyViolationError(error)) {
      messages.value.push({ role: 'system', content: error.message })
      openUsagePolicyDialog(error.message)
      scrollToBottom()
      return
    }
    throw error
  }

  messages.value.push({ role: 'user', content: userText })
  inputMessage.value = ''
  if (inputTextarea.value) inputTextarea.value.style.height = 'auto'
  scrollToBottom()

  const requestedMediaType = detectMediaIntentFromText(userText)
  if (requestedMediaType) {
    activeMediaType.value = requestedMediaType
    const mediaGuidance = requestedMediaType === 'audio' ? sanitizeMediaCommandGuidance(userText) : userText
    mediaPromptInput.value = mediaGuidance
    showMediaGenerator.value = true
    await generateMediaFromContext(requestedMediaType, mediaGuidance, true)
    return
  }
  
  await fetchAssistantResponse()
}
</script>

<style scoped>
#tavern-root {
  max-width: 1024px;
  height: calc(100vh - 168px);
  min-height: 420px;
  max-height: 760px;
  margin: 12px auto 24px;
  border: 1px solid #d5e3f3;
  border-radius: 18px;
  background:
    radial-gradient(circle at 7% -6%, color-mix(in srgb, var(--primary-color) 13%, transparent) 0%, transparent 34%),
    radial-gradient(circle at 94% -4%, color-mix(in srgb, #22c55e 13%, transparent) 0%, transparent 34%),
    linear-gradient(180deg, #f9fcff 0%, #f4f8ff 100%);
  box-shadow: 0 28px 48px -36px rgba(15, 23, 42, 0.42);
}

@media (max-width: 1023px) {
  #tavern-root {
    max-width: none;
    height: calc(100vh - 124px);
    margin: 0;
    border-left: 0;
    border-right: 0;
    border-radius: 0;
  }
}

.tavern-galaxy :deep(.sidebar-panel) {
  background:
    radial-gradient(circle at -10% 0%, rgba(34, 197, 94, 0.08) 0%, transparent 44%),
    linear-gradient(180deg, #f9fcff 0%, #f4f8ff 100%) !important;
  border-right-color: #d8e3f2 !important;
}

.tavern-galaxy :deep(main) {
  background:
    radial-gradient(circle at 98% 0%, rgba(14, 165, 233, 0.08) 0%, transparent 32%),
    linear-gradient(180deg, #fafdff 0%, #f6faff 100%) !important;
}

.tavern-galaxy :deep(header),
.tavern-galaxy :deep(.bg-\[\#f5f5f5\]),
.tavern-galaxy :deep(.bg-\[\#f7f7f7\]) {
  background:
    linear-gradient(180deg, color-mix(in srgb, #ffffff 90%, #f3f9ff 10%) 0%, #f8fbff 100%) !important;
  border-color: #dbe5f3 !important;
}

.tavern-galaxy :deep(button) {
  border-color: #d2e0f2 !important;
  background: linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
  color: #0f172a !important;
  box-shadow: 0 12px 22px -22px rgba(15, 23, 42, 0.42);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.tavern-galaxy :deep(button:hover:not(:disabled)) {
  transform: translateY(-1px);
  border-color: #95d7ff !important;
  box-shadow: 0 16px 26px -20px rgba(3, 105, 161, 0.38);
}

.tavern-galaxy :deep(button[class*='bg-[#07c160]']),
.tavern-galaxy :deep(button[class*='bg-slate-900']),
.tavern-galaxy :deep(.bg-\[\#07c160\]) {
  background: linear-gradient(180deg, #22b1f0 0%, #0284c7 100%) !important;
  border-color: transparent !important;
  color: #ffffff !important;
}

.tavern-galaxy :deep(input),
.tavern-galaxy :deep(textarea),
.tavern-galaxy :deep(select) {
  border-color: #cfe0f2 !important;
  border-radius: 12px !important;
  background: linear-gradient(180deg, #ffffff 0%, #f5faff 100%) !important;
  color: #0f172a !important;
}

.tavern-galaxy :deep(input:focus),
.tavern-galaxy :deep(textarea:focus),
.tavern-galaxy :deep(select:focus) {
  outline: none;
  border-color: #7dd3fc !important;
  box-shadow: 0 0 0 4px rgba(125, 211, 252, 0.2) !important;
}

.tavern-galaxy :deep(.text-slate-500),
.tavern-galaxy :deep(.text-slate-600) {
  color: #51627a !important;
}

.tavern-galaxy :deep(.text-slate-700),
.tavern-galaxy :deep(.text-slate-800),
.tavern-galaxy :deep(.text-slate-900) {
  color: #0f172a !important;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

:deep(.prose) { color: #334155; }
:deep(.prose p) { margin: 0.5em 0; }
:deep(.prose code) { 
  color: var(--primary-color, #4f46e5);
  background: #f1f5f9;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  font-weight: 600;
}
:deep(.prose strong) { color: #1e293b; }

/* Fix for overflow content in bubbles */
:deep(.prose) {
  word-wrap: break-word;
  overflow-wrap: break-word;
  width: 100%;
}

:deep(.prose pre) {
  white-space: pre-wrap;
  word-break: break-all;
  overflow-x: auto;
  background-color: #f8fafc;
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
  font-size: 0.85em;
  border: 1px solid #e2e8f0;
}

:deep(.prose pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
  font-weight: normal;
}

:deep(.prose img),
:deep(.prose video),
:deep(.prose iframe),
:deep(.prose table) {
  max-width: 100%;
}

:deep(.prose table) {
  display: block;
  overflow-x: auto;
}

.status-roll-enter-active,
.status-roll-leave-active {
  transition: transform 0.28s ease, opacity 0.28s ease;
}

.status-roll-enter-from {
  transform: translateY(55%);
  opacity: 0;
}

.status-roll-leave-to {
  transform: translateY(-55%);
  opacity: 0;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

