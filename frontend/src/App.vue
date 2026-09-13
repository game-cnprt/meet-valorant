<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ROLES, AGENTS_BY_ROLE, ALL_AGENTS, RANKS, RATING_TYPES, COMMON_TAGS } from './data/valorantData'

// State
const teammates = ref([])
const stats = ref({
  total_teammates: 0,
  favorites_count: 0,
  role_distribution: {},
  rank_distribution: {},
  rating_distribution: {},
  most_common_role: 'None'
})
const loading = ref(true)
const searchQuery = ref('')
const selectedRole = ref('All')
const selectedRank = ref('All')
const selectedRating = ref('All')
const onlyFavorites = ref(false)

// Modal State for Teammate Add/Edit
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const customTagInput = ref('')

// Riot API verification state inside Add/Edit modal
const verifyingRiot = ref(false)
const riotVerificationStatus = ref(null)

// Dedicated Riot Info Modal State
const showRiotInfoModal = ref(false)
const riotInfoMode = ref('me') // 'me' or 'lookup'
const lookupGameName = ref('TenZ')
const lookupTagline = ref('NA1')
const riotApiLoading = ref(false)
const riotApiResponse = ref(null)

// Dedicated HenrikDev Match History & Players Modal State
const showMatchModal = ref(false)
const matchUserGameName = ref('ThanHuCongTu')
const matchUserTagline = ref('hohoh')
const matchRegion = ref('ap')
const matchLoading = ref(false)
const importingAll = ref(false)
const matchResults = ref(null)

const defaultFormData = {
  game_name: '',
  tagline: 'VN1',
  role: 'Duelist',
  main_agent: 'Jett',
  rank_tier: 'Gold',
  rating_type: 'duo_buddy',
  tags: [],
  discord: '',
  notes: '',
  matches_played: 1,
  win_rate: 50,
  is_favorite: false
}

const formData = reactive({ ...defaultFormData })

// Toast notification state
const toast = reactive({
  show: false,
  message: '',
  type: 'info'
})

const showToast = (message, type = 'info') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3500)
}

// Fetch teammates and stats
const fetchTeammates = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) params.append('q', searchQuery.value)
    if (selectedRole.value !== 'All') params.append('role', selectedRole.value)
    if (selectedRank.value !== 'All') params.append('rank_tier', selectedRank.value)
    if (selectedRating.value !== 'All') params.append('rating_type', selectedRating.value)
    if (onlyFavorites.value) params.append('is_favorite', 'true')

    const res = await fetch(`/api/teammates?${params.toString()}`)
    if (res.ok) {
      teammates.value = await res.json()
    }
  } catch (err) {
    console.error('Lỗi tải danh sách đồng đội:', err)
    showToast('Không thể kết nối máy chủ API. Vui lòng kiểm tra backend.', 'error')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await fetch('/api/stats')
    if (res.ok) {
      stats.value = await res.json()
    }
  } catch (err) {
    console.error('Lỗi tải thống kê:', err)
  }
}

// Dedicated HenrikDev Match History & Players Modal Handlers
const openMatchModal = () => {
  showMatchModal.value = true
  if (!matchResults.value) {
    fetchHenrikMatches()
  }
}

const fetchHenrikMatches = async () => {
  if (!matchUserGameName.value.trim() || !matchUserTagline.value.trim()) {
    showToast('Vui lòng nhập Tên Game và Tagline!', 'error')
    return
  }

  matchLoading.value = true
  matchResults.value = null

  try {
    const url = `/api/henrik/matches/${encodeURIComponent(matchUserGameName.value.trim())}/${encodeURIComponent(matchUserTagline.value.trim())}?region=${matchRegion.value}`
    const res = await fetch(url)
    const data = await res.json()

    if (res.ok && data.success) {
      matchResults.value = data
      showToast(`Đã lấy thành công ${data.total_matches} trận đấu vừa chơi cho ${data.game_name}#${data.tagline}!`, 'success')
    } else {
      matchResults.value = {
        success: false,
        error: data.detail || 'Không lấy được lịch sử trận đấu'
      }
      showToast(data.detail || 'Lỗi tra cứu trận đấu', 'error')
    }
  } catch (err) {
    matchResults.value = {
      success: false,
      error: 'Lỗi kết nối máy chủ API'
    }
    showToast('Không thể kết nối máy chủ', 'error')
  } finally {
    matchLoading.value = false
  }
}

// Import all teammates from recent matches into database automatically
const importAllTeammates = async () => {
  if (!matchUserGameName.value.trim() || !matchUserTagline.value.trim()) {
    showToast('Vui lòng nhập Tên Game và Tagline!', 'error')
    return
  }

  importingAll.value = true
  try {
    const url = `/api/henrik/import-teammates/${encodeURIComponent(matchUserGameName.value.trim())}/${encodeURIComponent(matchUserTagline.value.trim())}?region=${matchRegion.value}`
    const res = await fetch(url, { method: 'POST' })
    const data = await res.json()

    if (res.ok && data.success) {
      showToast(`Đã lưu ${data.added_count} đồng đội mới vào sổ tay! (${data.existing_updated_count} đồng đội đã cập nhật số trận)`, 'success')
      showMatchModal.value = false
      await fetchTeammates()
      await fetchStats()
    } else {
      showToast(data.detail || 'Lỗi khi lưu đồng đội', 'error')
    }
  } catch (err) {
    showToast('Lỗi kết nối máy chủ API', 'error')
  } finally {
    importingAll.value = false
  }
}

// Save player met in a match directly to roster form
const savePlayerFromMatch = (player) => {
  showMatchModal.value = false
  openCreateModal()

  formData.game_name = player.game_name
  formData.tagline = player.tagline
  
  if (player.agent_name && player.agent_name !== 'Unknown') {
    formData.main_agent = player.agent_name
    // Auto detect role from agent name
    for (const [role, agents] of Object.entries(AGENTS_BY_ROLE)) {
      if (agents.includes(player.agent_name)) {
        formData.role = role
        break
      }
    }
  }

  formData.notes = `Vừa gặp trong trận đấu! KDA: ${player.kills}/${player.deaths}/${player.assists}, Điểm số: ${player.score}`
  formData.tags = ['Vừa Gặp', player.is_teammate ? 'Cùng Team' : 'Đối Thủ']
  showToast(`Đã tự động điền đồng đội ${player.game_name}#${player.tagline} (${player.agent_name}) vào form!`, 'info')
}

// Dedicated Get Riot API Info Modal Handlers
const openRiotInfoModal = () => {
  showRiotInfoModal.value = true
  riotApiResponse.value = null
  fetchRiotApiMe()
}

const fetchRiotApiMe = async () => {
  riotApiLoading.value = true
  riotApiResponse.value = null
  try {
    const res = await fetch('/api/riot/account/me')
    const data = await res.json()
    if (res.ok && data.success) {
      riotApiResponse.value = data
      showToast('Đã lấy thành công thông tin Riot qua API /accounts/me!', 'success')
    } else {
      riotApiResponse.value = {
        success: false,
        error: data.detail || 'Không thể lấy thông tin /accounts/me từ Riot API'
      }
    }
  } catch (err) {
    riotApiResponse.value = {
      success: false,
      error: 'Không thể kết nối tới máy chủ Backend API'
    }
  } finally {
    riotApiLoading.value = false
  }
}

const fetchRiotApiLookup = async () => {
  if (!lookupGameName.value.trim() || !lookupTagline.value.trim()) {
    showToast('Vui lòng nhập Tên Game và Tagline!', 'error')
    return
  }
  riotApiLoading.value = true
  riotApiResponse.value = null
  try {
    const res = await fetch(`/api/riot/search/${encodeURIComponent(lookupGameName.value.trim())}/${encodeURIComponent(lookupTagline.value.trim())}`)
    const data = await res.json()
    if (res.ok && data.success) {
      riotApiResponse.value = data
      showToast(`Đã tìm thấy Riot ID ${data.game_name}#${data.tagline}!`, 'success')
    } else {
      riotApiResponse.value = {
        success: false,
        error: data.detail || 'Không tìm thấy người chơi'
      }
    }
  } catch (err) {
    riotApiResponse.value = {
      success: false,
      error: 'Lỗi kết nối API'
    }
  } finally {
    riotApiLoading.value = false
  }
}

// Quick add fetched Riot Account into Teammate roster
const addFetchedToRoster = () => {
  if (!riotApiResponse.value || !riotApiResponse.value.success) return
  showRiotInfoModal.value = false
  openCreateModal()
  formData.game_name = riotApiResponse.value.game_name
  formData.tagline = riotApiResponse.value.tagline
  showToast(`Đã tự động điền Riot ID ${formData.game_name}#${formData.tagline} vào form thêm mới!`, 'info')
}

// Verify Riot ID inside Create/Edit Modal
const verifyRiotAccount = async () => {
  if (!formData.game_name.trim() || !formData.tagline.trim()) {
    showToast('Vui lòng nhập đầy đủ Tên Game và Tagline trước khi kiểm tra!', 'error')
    return
  }

  verifyingRiot.value = true
  riotVerificationStatus.value = null

  try {
    const res = await fetch(`/api/riot/search/${encodeURIComponent(formData.game_name.trim())}/${encodeURIComponent(formData.tagline.trim())}`)
    const data = await res.json()

    if (res.ok && data.success) {
      riotVerificationStatus.value = {
        success: true,
        message: `Xác minh thành công! PUUID: ${data.puuid.slice(0, 16)}...`
      }
      showToast(`Đã xác minh tài khoản Riot ${data.game_name}#${data.tagline} chính chủ!`, 'success')
    } else {
      riotVerificationStatus.value = {
        success: false,
        message: data.detail || 'Không tìm thấy tài khoản hoặc Riot API Key đã hết hạn.'
      }
      showToast(data.detail || 'Kiểm tra thất bại', 'error')
    }
  } catch (err) {
    riotVerificationStatus.value = {
      success: false,
      message: 'Không thể kết nối API Riot Games'
    }
    showToast('Lỗi kết nối máy chủ', 'error')
  } finally {
    verifyingRiot.value = false
  }
}

// Available agents for the currently selected role in modal
const availableAgents = computed(() => {
  return AGENTS_BY_ROLE[formData.role] || []
})

const handleRoleChange = () => {
  const agents = availableAgents.value
  if (agents.length > 0 && !agents.includes(formData.main_agent)) {
    formData.main_agent = agents[0]
  }
}

// Open modal for Create
const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  riotVerificationStatus.value = null
  Object.assign(formData, defaultFormData, { tags: ['Thân Thiện', 'Chịu Nghe Call'] })
  showModal.value = true
}

// Open modal for Edit
const openEditModal = (mate) => {
  isEditing.value = true
  editingId.value = mate.id
  riotVerificationStatus.value = null
  Object.assign(formData, {
    game_name: mate.game_name,
    tagline: mate.tagline,
    role: mate.role,
    main_agent: mate.main_agent,
    rank_tier: mate.rank_tier,
    rating_type: mate.rating_type,
    tags: [...(mate.tags || [])],
    discord: mate.discord || '',
    notes: mate.notes || '',
    matches_played: mate.matches_played ?? 1,
    win_rate: mate.win_rate ?? 50,
    is_favorite: mate.is_favorite ?? false
  })
  showModal.value = true
}

// Toggle Tag in Modal
const toggleTag = (tag) => {
  const idx = formData.tags.indexOf(tag)
  if (idx > -1) {
    formData.tags.splice(idx, 1)
  } else {
    formData.tags.push(tag)
  }
}

const addCustomTag = () => {
  const trimmed = customTagInput.value.trim()
  if (trimmed && !formData.tags.includes(trimmed)) {
    formData.tags.push(trimmed)
    customTagInput.value = ''
  }
}

// Submit Form
const handleSubmit = async () => {
  if (!formData.game_name.trim() || !formData.tagline.trim()) {
    showToast('Vui lòng nhập Tên Game và Tagline Riot!', 'error')
    return
  }

  submitting.value = true
  try {
    const url = isEditing.value ? `/api/teammates/${editingId.value}` : '/api/teammates'
    const method = isEditing.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })

    if (res.ok) {
      showToast(isEditing.value ? 'Đã cập nhật đồng đội!' : 'Đã thêm đồng đội mới!', 'success')
      showModal.value = false
      await fetchTeammates()
      await fetchStats()
    } else {
      const err = await res.json()
      showToast(err.detail || 'Có lỗi xảy ra', 'error')
    }
  } catch (err) {
    showToast('Lỗi khi gửi dữ liệu', 'error')
  } finally {
    submitting.value = false
  }
}

// Toggle Favorite
const handleToggleFavorite = async (id, e) => {
  e.stopPropagation()
  try {
    const res = await fetch(`/api/teammates/${id}/toggle-favorite`, { method: 'POST' })
    if (res.ok) {
      const updated = await res.json()
      const target = teammates.value.find(m => m.id === id)
      if (target) target.is_favorite = updated.is_favorite
      await fetchStats()
      showToast(updated.is_favorite ? 'Đã thêm vào danh sách Cạ Cứng ⭐' : 'Đã bỏ cạ cứng', 'info')
    }
  } catch (err) {
    showToast('Không thể cập nhật cạ cứng', 'error')
  }
}

// Delete Teammate
const handleDelete = async (id, name, e) => {
  e.stopPropagation()
  if (!confirm(`Bạn có chắc muốn xóa đồng đội "${name}" khỏi danh sách?`)) return

  try {
    const res = await fetch(`/api/teammates/${id}`, { method: 'DELETE' })
    if (res.ok) {
      showToast(`Đã xóa đồng đội ${name}`, 'info')
      await fetchTeammates()
      await fetchStats()
    }
  } catch (err) {
    showToast('Lỗi khi xóa đồng đội', 'error')
  }
}

// Reseed Sample Data
const handleReseed = async () => {
  if (!confirm('Tải lại dữ liệu đồng đội mẫu mặc định?')) return
  try {
    const res = await fetch('/api/seed', { method: 'POST' })
    if (res.ok) {
      showToast('Đã nạp lại danh sách đồng đội mẫu!', 'success')
      await fetchTeammates()
      await fetchStats()
    }
  } catch (err) {
    showToast('Không thể nạp dữ liệu', 'error')
  }
}

// Helper formatting functions
const getRankColor = (rankName) => {
  const r = RANKS.find(x => x.id === rankName || x.name.includes(rankName))
  return r ? r.color : '#94a3b8'
}

const getRoleColor = (roleName) => {
  const r = ROLES.find(x => x.id === roleName)
  return r ? r.color : '#ff4655'
}

const getRoleIcon = (roleName) => {
  const r = ROLES.find(x => x.id === roleName)
  return r ? r.icon : '🎮'
}

const getRatingMeta = (ratingId) => {
  return RATING_TYPES[ratingId] || RATING_TYPES.duo_buddy
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedRole.value = 'All'
  selectedRank.value = 'All'
  selectedRating.value = 'All'
  onlyFavorites.value = false
  fetchTeammates()
}

onMounted(() => {
  fetchTeammates()
  fetchStats()
})
</script>

<template>
  <div class="app-layout">
    <!-- TOP NOTIFICATION TOAST -->
    <transition name="toast">
      <div v-if="toast.show" class="tactical-toast" :class="`toast-${toast.type}`">
        <span class="toast-indicator"></span>
        <span class="toast-text">{{ toast.message }}</span>
      </div>
    </transition>

    <!-- HEADER / NAVIGATION -->
    <header class="header">
      <div class="container header-container">
        <div class="brand">
          <div class="brand-logo">
            <span class="logo-slash">//</span>
            <span class="logo-primary">MEET</span>
            <span class="logo-accent">VALORANT</span>
          </div>
          <p class="brand-subtitle">TACTICAL TEAMMATE ROSTER & DUO TRACKER</p>
        </div>

        <div class="header-actions">
          <!-- BUTTON HENRIKDEV MATCH & PLAYER LOOKUP -->
          <button @click="openMatchModal" class="tactical-btn btn-purple-glow" title="Lấy lịch sử trận đấu & danh sách player vừa gặp qua HenrikDev API">
            <span class="btn-icon">🎮</span> Trận Đấu & Player Đã Gặp
          </button>
          <!-- BUTTON GET API THÔNG TIN RIOT -->
          <button @click="openRiotInfoModal" class="tactical-btn btn-cyan-glow" title="Lấy thông tin tài khoản qua HenrikDev API">
            <span class="btn-icon">⚡</span> GET API Thông Tin Riot
          </button>
          <button @click="handleReseed" class="tactical-btn btn-secondary" title="Nạp lại các đồng đội mẫu">
            <span class="btn-icon">🔄</span> Nạp Dữ Liệu Mẫu
          </button>
          <button @click="openCreateModal" class="tactical-btn btn-primary">
            <span class="btn-icon">➕</span> Thêm Đồng Đội Mới
          </button>
        </div>
      </div>
    </header>

    <main class="container main-content">
      <!-- STATS HERO BANNER -->
      <section class="stats-grid">
        <div class="stat-card tactical-cut">
          <div class="stat-accent" style="background: var(--val-red);"></div>
          <div class="stat-content">
            <span class="stat-label">Tổng Đồng Đội</span>
            <div class="stat-value font-display">{{ stats.total_teammates }}</div>
            <span class="stat-sub">Đã lưu trong sổ tay</span>
          </div>
          <div class="stat-icon-bg">👥</div>
        </div>

        <div class="stat-card tactical-cut">
          <div class="stat-accent" style="background: var(--val-gold);"></div>
          <div class="stat-content">
            <span class="stat-label">Cạ Cứng (Duo Buddy)</span>
            <div class="stat-value font-display text-gold">{{ stats.favorites_count }}</div>
            <span class="stat-sub">Ưu tiên rủ leo rank</span>
          </div>
          <div class="stat-icon-bg">⭐</div>
        </div>

        <div class="stat-card tactical-cut">
          <div class="stat-accent" style="background: var(--val-cyan);"></div>
          <div class="stat-content">
            <span class="stat-label">Vai Trò Nhiều Nhất</span>
            <div class="stat-value font-display text-cyan">{{ stats.most_common_role || 'N/A' }}</div>
            <span class="stat-sub">{{ stats.role_distribution[stats.most_common_role] || 0 }} người chơi</span>
          </div>
          <div class="stat-icon-bg">{{ getRoleIcon(stats.most_common_role) }}</div>
        </div>

        <div class="stat-card tactical-cut">
          <div class="stat-accent" style="background: #a855f7;"></div>
          <div class="stat-content">
            <span class="stat-label">Tỉ Lệ Gánh Team</span>
            <div class="stat-value font-display text-purple">
              {{ stats.rating_distribution['carry'] || 0 }}
            </div>
            <span class="stat-sub">Tay to bảo kê trận đấu</span>
          </div>
          <div class="stat-icon-bg">🎯</div>
        </div>
      </section>

      <!-- FILTER & SEARCH CONTROLS -->
      <section class="filter-section tactical-cut">
        <!-- Search Bar -->
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchQuery"
            @input="fetchTeammates"
            type="text"
            placeholder="Tìm theo Riot ID, Tag, Đặc vụ, hoặc ghi chú..."
            class="tactical-input search-input"
          />
          <button v-if="searchQuery" @click="searchQuery = ''; fetchTeammates()" class="clear-search">✕</button>
        </div>

        <!-- Role Filter Pills -->
        <div class="filter-roles">
          <button
            class="role-pill"
            :class="{ active: selectedRole === 'All' }"
            @click="selectedRole = 'All'; fetchTeammates()"
          >
            Tất Cả Roles
          </button>
          <button
            v-for="role in ROLES"
            :key="role.id"
            class="role-pill"
            :class="{ active: selectedRole === role.id }"
            @click="selectedRole = role.id; fetchTeammates()"
            :style="{ '--active-color': role.color }"
          >
            <span>{{ role.icon }}</span> {{ role.name }}
          </button>
        </div>

        <!-- Secondary Filters Row -->
        <div class="filter-dropdowns">
          <!-- Rank Filter -->
          <div class="select-group">
            <label>Rank:</label>
            <select v-model="selectedRank" @change="fetchTeammates" class="tactical-select">
              <option value="All">Tất Cả Rank</option>
              <option v-for="r in RANKS" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>

          <!-- Rating Filter -->
          <div class="select-group">
            <label>Đánh giá:</label>
            <select v-model="selectedRating" @change="fetchTeammates" class="tactical-select">
              <option value="All">Tất Cả Đánh Giá</option>
              <option v-for="(meta, key) in RATING_TYPES" :key="key" :value="key">
                {{ meta.icon }} {{ meta.label }}
              </option>
            </select>
          </div>

          <!-- Favorite Toggle Button -->
          <button
            class="tactical-btn"
            :class="onlyFavorites ? 'btn-gold-active' : 'btn-outline'"
            @click="onlyFavorites = !onlyFavorites; fetchTeammates()"
          >
            <span>⭐</span> Chỉ Cạ Cứng
          </button>

          <!-- Reset Filter -->
          <button
            v-if="selectedRole !== 'All' || selectedRank !== 'All' || selectedRating !== 'All' || onlyFavorites || searchQuery"
            @click="resetFilters"
            class="tactical-btn btn-outline reset-btn"
          >
            Đặt lại lọc
          </button>
        </div>
      </section>

      <!-- TEAMMATES LIST / CARDS -->
      <section class="roster-section">
        <div class="section-title-bar">
          <h2 class="section-title">
            <span class="title-accent">//</span> DANH SÁCH ĐỒNG ĐỘI
            <span class="count-badge">({{ teammates.length }})</span>
          </h2>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="state-container">
          <div class="tactical-spinner"></div>
          <p class="state-text">Đang tải danh sách đặc vụ...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="teammates.length === 0" class="empty-container tactical-cut">
          <div class="empty-icon">🎮</div>
          <h3>Không tìm thấy đồng đội phù hợp</h3>
          <p>Thử điều chỉnh bộ lọc hoặc bấm "Thêm Đồng Đội Mới" để lưu người bạn vừa chơi cùng!</p>
          <button @click="openCreateModal" class="tactical-btn btn-primary" style="margin-top: 16px;">
            + Thêm Đồng Đội Ngay
          </button>
        </div>

        <!-- Cards Grid -->
        <div v-else class="cards-grid">
          <div
            v-for="mate in teammates"
            :key="mate.id"
            class="mate-card tactical-cut"
            :class="{ 'is-favorite-card': mate.is_favorite }"
          >
            <!-- Card Header -->
            <div class="mate-header">
              <div class="role-badge" :style="{ color: getRoleColor(mate.role), borderColor: getRoleColor(mate.role) }">
                <span>{{ getRoleIcon(mate.role) }}</span>
                <span>{{ mate.role }}</span>
              </div>

              <div class="header-right">
                <button
                  @click="handleToggleFavorite(mate.id, $event)"
                  class="favorite-star-btn"
                  :class="{ active: mate.is_favorite }"
                  :title="mate.is_favorite ? 'Bỏ cạ cứng' : 'Đánh dấu cạ cứng'"
                >
                  {{ mate.is_favorite ? '★' : '☆' }}
                </button>
              </div>
            </div>

            <!-- Agent & Name Area -->
            <div class="mate-identity">
              <div class="agent-avatar" :style="{ borderColor: getRoleColor(mate.role) }">
                <span class="agent-initial">{{ mate.main_agent.slice(0, 2).toUpperCase() }}</span>
              </div>
              <div class="identity-text">
                <div class="riot-id font-display">
                  <span class="name">{{ mate.game_name }}</span>
                  <span class="tag">#{{ mate.tagline }}</span>
                </div>
                <div class="agent-name">
                  Đặc vụ tủ: <strong>{{ mate.main_agent }}</strong>
                </div>
              </div>
            </div>

            <!-- Rank & Rating Badges -->
            <div class="badge-row">
              <div class="rank-pill" :style="{ borderColor: getRankColor(mate.rank_tier), color: getRankColor(mate.rank_tier) }">
                <span class="rank-dot" :style="{ backgroundColor: getRankColor(mate.rank_tier) }"></span>
                <span>{{ mate.rank_tier }}</span>
              </div>

              <div
                class="rating-pill"
                :style="{
                  backgroundColor: getRatingMeta(mate.rating_type).bg,
                  color: getRatingMeta(mate.rating_type).color
                }"
              >
                <span>{{ getRatingMeta(mate.rating_type).icon }}</span>
                <span>{{ getRatingMeta(mate.rating_type).label }}</span>
              </div>
            </div>

            <!-- Stats Mini Bar -->
            <div class="mate-stats-row">
              <div class="stat-mini">
                <span class="label">Số trận duo:</span>
                <span class="val font-display">{{ mate.matches_played }}</span>
              </div>
              <div class="stat-mini">
                <span class="label">Tỉ lệ thắng:</span>
                <span class="val font-display" :class="mate.win_rate >= 60 ? 'text-win-high' : ''">{{ mate.win_rate }}%</span>
              </div>
              <div class="winrate-bar-track">
                <div class="winrate-bar-fill" :style="{ width: `${mate.win_rate}%` }"></div>
              </div>
            </div>

            <!-- Tags -->
            <div v-if="mate.tags && mate.tags.length > 0" class="tags-container">
              <span v-for="t in mate.tags" :key="t" class="tag-chip">
                {{ t }}
              </span>
            </div>

            <!-- Notes & Discord -->
            <div v-if="mate.notes || mate.discord" class="mate-details">
              <p v-if="mate.notes" class="mate-notes">"{{ mate.notes }}"</p>
              <div v-if="mate.discord" class="discord-contact">
                <span class="discord-icon">💬</span>
                <span class="discord-text">{{ mate.discord }}</span>
              </div>
            </div>

            <!-- Card Footer Actions -->
            <div class="card-footer">
              <span class="mate-time">ID #{{ mate.id }}</span>
              <div class="action-buttons">
                <button @click="openEditModal(mate)" class="card-action-btn edit-btn" title="Chỉnh sửa thông tin">
                  ✏️ Sửa
                </button>
                <button @click="handleDelete(mate.id, mate.game_name, $event)" class="card-action-btn delete-btn" title="Xóa khỏi danh sách">
                  🗑️ Xóa
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- HENRIKDEV MATCHES & PLAYERS MODAL -->
    <div v-if="showMatchModal" class="modal-overlay" @click.self="showMatchModal = false">
      <div class="modal-content tactical-cut animate-fade-in" style="max-width: 860px;">
        <div class="modal-header">
          <h3 class="modal-title font-display" style="color: #c084fc;">
            <span class="title-accent">//</span> TRẬN ĐẤU VỪA CHƠI & ĐỒNG ĐỘI ĐÃ GẶP (HENRIKDEV API)
          </h3>
          <button @click="showMatchModal = false" class="close-modal-btn">✕</button>
        </div>

        <!-- Search Bar Header inside Modal -->
        <div class="modal-body-section">
          <p class="section-desc">
            Nhập Riot ID để lấy lịch sử 5 trận gần nhất và trích xuất <strong>toàn bộ đồng đội vừa bắn cùng</strong>:
          </p>
          <div class="form-row two-cols" style="margin-bottom: 14px;">
            <input v-model="matchUserGameName" type="text" placeholder="Tên Game (ví dụ: ThanHuCongTu)" class="tactical-input" />
            <div class="tagline-input-row">
              <input v-model="matchUserTagline" type="text" placeholder="Tag (ví dụ: hohoh)" class="tactical-input" />
              <select v-model="matchRegion" class="tactical-select">
                <option value="ap">Server AP (ĐNÁ / VN)</option>
                <option value="na">Server NA (Bắc Mỹ)</option>
                <option value="eu">Server EU (Châu Âu)</option>
                <option value="kr">Server KR (Hàn Quốc)</option>
              </select>
            </div>
          </div>

          <div class="action-bar-row" style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button @click="fetchHenrikMatches" :disabled="matchLoading" class="tactical-btn btn-primary">
              <span v-if="matchLoading">⏳ Đang tải...</span>
              <span v-else>🔍 Tra Cứu Trận Đấu</span>
            </button>
            <button @click="importAllTeammates" :disabled="importingAll || matchLoading" class="tactical-btn btn-gold-active">
              <span v-if="importingAll">⏳ Đang tự động lưu...</span>
              <span v-else>⚡ Tự Động Lưu Tất Cả Đồng Đội Vào Sổ Tay</span>
            </button>
          </div>
        </div>

        <!-- Matches & Players Results -->
        <div v-if="matchLoading" class="state-container" style="padding: 30px;">
          <div class="tactical-spinner"></div>
          <p>Đang tải dữ liệu trận đấu và đặc vụ từ HenrikDev API...</p>
        </div>

        <div v-else-if="matchResults && matchResults.success" class="matches-list-container">
          <div class="matches-header-info">
            <span class="status-badge" style="background: #a855f7;">HDEV API 200 OK</span>
            <span>Tài khoản: <strong>{{ matchResults.game_name }}#{{ matchResults.tagline }}</strong> ({{ matchResults.total_matches }} trận vừa tìm thấy)</span>
          </div>

          <div v-for="match in matchResults.matches" :key="match.match_id" class="match-item-card tactical-cut">
            <div class="match-meta-bar">
              <span class="match-map-title font-display">🗺️ {{ match.map }}</span>
              <span class="match-mode-tag">{{ match.mode }}</span>
              <span class="match-time">{{ match.game_start }} ({{ match.rounds_played }} rounds)</span>
            </div>

            <div class="match-players-title">👥 DANH SÁCH PLAYERS TRONG TRẬN:</div>
            <div class="match-players-grid">
              <div
                v-for="p in match.players"
                :key="p.puuid || p.game_name"
                class="match-player-row"
                :class="{ 'is-user-row': p.is_me, 'is-teammate-row': p.is_teammate }"
              >
                <div class="player-left">
                  <span class="team-dot" :class="`team-${p.team ? p.team.toLowerCase() : 'neutral'}`"></span>
                  <span class="player-name font-display">{{ p.game_name }}<span class="tag">#{{ p.tagline }}</span></span>
                  <span class="agent-chip">{{ p.agent_name }}</span>
                  <span v-if="p.is_me" class="badge-me">BẠN</span>
                  <span v-else-if="p.is_teammate" class="badge-teammate">ĐỒNG ĐỘI</span>
                </div>

                <div class="player-right">
                  <span class="kda-text font-display">K/D/A: {{ p.kills }}/{{ p.deaths }}/{{ p.assists }}</span>
                  <button v-if="!p.is_me" @click="savePlayerFromMatch(p)" class="quick-add-mate-btn" title="Lưu player này vào sổ tay đồng đội">
                    ➕ Lưu Đồng Đội
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="matchResults && !matchResults.success" class="result-error-content" style="padding: 20px;">
          <div class="error-title font-display">⚠️ LỖI TRA CỨU TRẬN ĐẤU</div>
          <p class="error-msg">{{ matchResults.error }}</p>
        </div>

        <div class="modal-footer">
          <button type="button" @click="showMatchModal = false" class="tactical-btn btn-secondary">
            Đóng
          </button>
        </div>
      </div>
    </div>

    <!-- DEDICATED RIOT API INFO MODAL -->
    <div v-if="showRiotInfoModal" class="modal-overlay" @click.self="showRiotInfoModal = false">
      <div class="modal-content tactical-cut animate-fade-in">
        <div class="modal-header">
          <h3 class="modal-title font-display" style="color: var(--val-cyan);">
            <span class="title-accent">//</span> TRA CỨU THÔNG TIN RIOT / HENRIKDEV API
          </h3>
          <button @click="showRiotInfoModal = false" class="close-modal-btn">✕</button>
        </div>

        <!-- Mode Switcher Tabs -->
        <div class="riot-modal-tabs">
          <button
            class="tab-btn"
            :class="{ active: riotInfoMode === 'me' }"
            @click="riotInfoMode = 'me'; fetchRiotApiMe()"
          >
            👤 Tài Khoản Cá Nhân (/accounts/me)
          </button>
          <button
            class="tab-btn"
            :class="{ active: riotInfoMode === 'lookup' }"
            @click="riotInfoMode = 'lookup'; riotApiResponse = null"
          >
            🔍 Tra Cứu Theo Riot ID (/by-riot-id)
          </button>
        </div>

        <!-- Mode 1: /accounts/me info -->
        <div v-if="riotInfoMode === 'me'" class="modal-body-section">
          <p class="section-desc">
            Gọi API endpoint <code>/riot/account/v1/accounts/me</code> lấy thông tin tài khoản hiện tại từ API Token trong file <code>.env</code>.
          </p>
          <button @click="fetchRiotApiMe" :disabled="riotApiLoading" class="tactical-btn btn-primary" style="margin-bottom: 16px;">
            <span v-if="riotApiLoading">⏳ Đang gọi API...</span>
            <span v-else>⚡ Tải Lại Thông Tin /accounts/me</span>
          </button>
        </div>

        <!-- Mode 2: /by-riot-id lookup -->
        <div v-if="riotInfoMode === 'lookup'" class="modal-body-section">
          <p class="section-desc">
            Nhập Riot ID bất kỳ để gọi endpoint tra cứu thông tin tài khoản từ HenrikDev API.
          </p>
          <div class="form-row two-cols" style="margin-bottom: 14px;">
            <input v-model="lookupGameName" type="text" placeholder="Tên Game (ví dụ: ThanHuCongTu)" class="tactical-input" />
            <input v-model="lookupTagline" type="text" placeholder="Tagline (ví dụ: hohoh)" class="tactical-input" />
          </div>
          <button @click="fetchRiotApiLookup" :disabled="riotApiLoading" class="tactical-btn btn-primary" style="margin-bottom: 16px;">
            <span v-if="riotApiLoading">⏳ Đang tra cứu...</span>
            <span v-else>🔍 Tra Cứu Riot ID</span>
          </button>
        </div>

        <!-- Response Results Area -->
        <div v-if="riotApiLoading" class="state-container" style="padding: 30px;">
          <div class="tactical-spinner"></div>
          <p>Đang kết nối máy chủ API...</p>
        </div>

        <div v-else-if="riotApiResponse" class="riot-result-card" :class="riotApiResponse.success ? 'card-success' : 'card-error'">
          <div v-if="riotApiResponse.success" class="result-success-content">
            <div class="res-header">
              <span class="status-badge">HTTP 200 OK</span>
              <span class="time-stamp">Xác minh chính chủ HenrikDev API</span>
            </div>
            <div class="player-big-id font-display">
              {{ riotApiResponse.game_name }} <span class="tag">#{{ riotApiResponse.tagline }}</span>
            </div>
            <div v-if="riotApiResponse.rank_tier" class="rank-info-badge" style="margin-bottom: 8px; color: var(--val-gold); font-weight: 700;">
              🏅 Rank hiện tại: {{ riotApiResponse.rank_tier }} (Level {{ riotApiResponse.account_level || 'N/A' }})
            </div>
            <div class="puuid-box">
              <label>Riot PUUID:</label>
              <code>{{ riotApiResponse.puuid }}</code>
            </div>
            <button @click="addFetchedToRoster" class="tactical-btn btn-gold-active" style="margin-top: 14px; width: 100%; justify-content: center;">
              ➕ Thêm Người Này Vào Sổ Tay Đồng Đội
            </button>
          </div>

          <div v-else class="result-error-content">
            <div class="error-title font-display">⚠️ KẾT QUẢ API THẤT BẠI</div>
            <p class="error-msg">{{ riotApiResponse.error }}</p>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" @click="showRiotInfoModal = false" class="tactical-btn btn-secondary">
            Đóng
          </button>
        </div>
      </div>
    </div>

    <!-- ADD / EDIT MODAL -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content tactical-cut animate-fade-in">
        <div class="modal-header">
          <h3 class="modal-title font-display">
            <span class="title-accent">//</span> {{ isEditing ? 'CHỈNH SỬA ĐỒNG ĐỘI' : 'THÊM ĐỒNG ĐỘI MỚI' }}
          </h3>
          <button @click="showModal = false" class="close-modal-btn">✕</button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-form">
          <!-- Riot ID Row with Riot API Verification Button -->
          <div class="form-row two-cols">
            <div class="form-group">
              <label class="form-label">Tên trong game (Riot ID) *</label>
              <input
                v-model="formData.game_name"
                type="text"
                placeholder="Ví dụ: TenZ, Derke, Yay..."
                required
                class="tactical-input"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Tagline (#) *</label>
              <div class="tagline-input-row">
                <input
                  v-model="formData.tagline"
                  type="text"
                  placeholder="Ví dụ: NA1, VN1, 007..."
                  required
                  class="tactical-input"
                />
                <button
                  type="button"
                  @click="verifyRiotAccount"
                  :disabled="verifyingRiot"
                  class="tactical-btn btn-secondary riot-verify-btn"
                  title="Tra cứu trực tiếp qua HenrikDev API"
                >
                  <span v-if="verifyingRiot">⏳</span>
                  <span v-else>⚡ Kiểm Tra API</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Riot Verification Status Alert -->
          <div v-if="riotVerificationStatus" class="riot-status-box" :class="riotVerificationStatus.success ? 'status-success' : 'status-error'">
            <span class="status-icon">{{ riotVerificationStatus.success ? '✅' : '⚠️' }}</span>
            <span class="status-msg">{{ riotVerificationStatus.message }}</span>
          </div>

          <!-- Role & Agent Row -->
          <div class="form-row two-cols">
            <div class="form-group">
              <label class="form-label">Vai Trò (Role) *</label>
              <select v-model="formData.role" @change="handleRoleChange" class="tactical-select">
                <option v-for="r in ROLES" :key="r.id" :value="r.id">
                  {{ r.icon }} {{ r.name }} ({{ r.viName }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Đặc Vụ Tủ (Main Agent) *</label>
              <select v-model="formData.main_agent" class="tactical-select">
                <option v-for="agent in availableAgents" :key="agent" :value="agent">
                  {{ agent }}
                </option>
              </select>
            </div>
          </div>

          <!-- Rank & Rating Row -->
          <div class="form-row two-cols">
            <div class="form-group">
              <label class="form-label">Bậc Rank Hiện Tại</label>
              <select v-model="formData.rank_tier" class="tactical-select">
                <option v-for="rank in RANKS" :key="rank.id" :value="rank.id">
                  {{ rank.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Đánh Giá Phối Hợp</label>
              <select v-model="formData.rating_type" class="tactical-select">
                <option v-for="(meta, key) in RATING_TYPES" :key="key" :value="key">
                  {{ meta.icon }} {{ meta.label }}
                </option>
              </select>
            </div>
          </div>

          <!-- Matches & Winrate -->
          <div class="form-row two-cols">
            <div class="form-group">
              <label class="form-label">Số trận đã bắn chung</label>
              <input
                v-model.number="formData.matches_played"
                type="number"
                min="0"
                class="tactical-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Tỉ lệ thắng ước tính ({{ formData.win_rate }}%)</label>
              <input
                v-model.number="formData.win_rate"
                type="range"
                min="0"
                max="100"
                class="tactical-slider"
              />
            </div>
          </div>

          <!-- Discord -->
          <div class="form-group">
            <label class="form-label">Discord / Liên hệ (tùy chọn)</label>
            <input
              v-model="formData.discord"
              type="text"
              placeholder="ví dụ: tenz#1234 hoặc link voice"
              class="tactical-input"
            />
          </div>

          <!-- Playstyle Tags Selector -->
          <div class="form-group">
            <label class="form-label">Thẻ phong cách chơi (Chọn nhanh)</label>
            <div class="tags-picker">
              <button
                type="button"
                v-for="tag in COMMON_TAGS"
                :key="tag"
                class="tag-toggle-btn"
                :class="{ active: formData.tags.includes(tag) }"
                @click="toggleTag(tag)"
              >
                {{ tag }}
              </button>
            </div>
            <!-- Custom tag input -->
            <div class="custom-tag-row">
              <input
                v-model="customTagInput"
                @keydown.enter.prevent="addCustomTag"
                type="text"
                placeholder="Thêm thẻ tự chọn (nhấn Enter)..."
                class="tactical-input custom-tag-input"
              />
              <button type="button" @click="addCustomTag" class="tactical-btn btn-secondary">
                + Thêm
              </button>
            </div>
          </div>

          <!-- Favorite Checkbox -->
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="formData.is_favorite" type="checkbox" class="tactical-checkbox" />
              <span>⭐ Đánh dấu là <strong>Cạ Cứng (Duo Buddy)</strong> ưu tiên gọi leo rank</span>
            </label>
          </div>

          <!-- Notes -->
          <div class="form-group">
            <label class="form-label">Ghi Chú Trận Đấu & Nhận Xét</label>
            <textarea
              v-model="formData.notes"
              rows="3"
              placeholder="Ví dụ: Bắn Omen cực chuẩn bài, clutch 1v3 cứu team round 12, biết callout thông tin..."
              class="tactical-textarea"
            ></textarea>
          </div>

          <!-- Modal Footer Actions -->
          <div class="modal-footer">
            <button type="button" @click="showModal = false" class="tactical-btn btn-secondary">
              Hủy
            </button>
            <button type="submit" :disabled="submitting" class="tactical-btn btn-primary">
              <span v-if="submitting">Đang lưu...</span>
              <span v-else>{{ isEditing ? 'Cập Nhật' : 'Lưu Đồng Đội' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.btn-purple-glow {
  background: var(--val-surface);
  color: #c084fc;
  border: 1px solid #c084fc;
  box-shadow: 0 0 10px rgba(192, 132, 252, 0.2);
}

.btn-purple-glow:hover {
  background: #c084fc;
  color: #000;
  box-shadow: 0 0 16px rgba(192, 132, 252, 0.5);
}

.btn-cyan-glow {
  background: var(--val-surface);
  color: var(--val-cyan);
  border: 1px solid var(--val-cyan);
  box-shadow: 0 0 10px rgba(0, 245, 212, 0.2);
}

.btn-cyan-glow:hover {
  background: var(--val-cyan);
  color: #000;
  box-shadow: 0 0 16px rgba(0, 245, 212, 0.5);
}

.matches-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 4px;
}

.matches-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: var(--val-text-secondary);
}

.match-item-card {
  background: var(--val-dark);
  border: 1px solid var(--val-border);
  padding: 16px;
}

.match-meta-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 8px;
}

.match-map-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
}

.match-mode-tag {
  background: rgba(255, 255, 255, 0.1);
  color: var(--val-text-primary);
  font-size: 0.75rem;
  padding: 2px 8px;
}

.match-time {
  font-size: 0.75rem;
  color: var(--val-text-muted);
  margin-left: auto;
}

.match-players-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--val-text-secondary);
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.match-players-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.match-player-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 3px;
}

.match-player-row.is-user-row {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
}

.match-player-row.is-teammate-row {
  background: rgba(0, 245, 212, 0.05);
  border-color: rgba(0, 245, 212, 0.2);
}

.player-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.team-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.team-red { background: var(--val-red); }
.team-blue { background: var(--val-cyan); }
.team-neutral { background: var(--val-text-muted); }

.player-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
}

.player-name .tag {
  color: var(--val-text-muted);
  font-size: 0.8rem;
}

.agent-chip {
  background: rgba(255, 255, 255, 0.1);
  color: var(--val-text-primary);
  font-size: 0.75rem;
  padding: 1px 6px;
  border-radius: 2px;
}

.badge-me {
  background: var(--val-gold);
  color: #000;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 5px;
}

.badge-teammate {
  background: var(--val-cyan);
  color: #000;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 5px;
}

.player-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.kda-text {
  font-size: 0.85rem;
  color: var(--val-text-secondary);
}

.quick-add-mate-btn {
  background: var(--val-surface);
  border: 1px solid var(--val-border);
  color: var(--val-cyan);
  font-size: 0.75rem;
  font-family: var(--font-display);
  font-weight: 600;
  padding: 3px 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.quick-add-mate-btn:hover {
  background: var(--val-cyan);
  color: #000;
}

.riot-modal-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--val-border);
  padding-bottom: 12px;
}

.tab-btn {
  background: var(--val-surface);
  border: 1px solid var(--val-border);
  color: var(--val-text-secondary);
  padding: 8px 14px;
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
}

.tab-btn.active {
  background: var(--val-cyan);
  color: #000;
  border-color: transparent;
  font-weight: 700;
}

.section-desc {
  font-size: 0.85rem;
  color: var(--val-text-secondary);
  margin-bottom: 14px;
  line-height: 1.5;
}

.section-desc code {
  color: var(--val-cyan);
  background: rgba(0, 0, 0, 0.4);
  padding: 2px 6px;
  border-radius: 3px;
}

.riot-result-card {
  background: var(--val-dark);
  border: 1px solid var(--val-border);
  padding: 20px;
  margin-bottom: 16px;
}

.card-success {
  border-color: var(--val-cyan);
  box-shadow: 0 0 20px rgba(0, 245, 212, 0.15);
}

.card-error {
  border-color: #ef4444;
}

.res-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.status-badge {
  background: var(--val-cyan);
  color: #000;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.75rem;
  padding: 2px 8px;
}

.time-stamp {
  font-size: 0.75rem;
  color: var(--val-text-muted);
}

.player-big-id {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
}

.player-big-id .tag {
  color: var(--val-text-muted);
}

.puuid-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  padding: 10px;
  border-left: 2px solid var(--val-cyan);
}

.puuid-box label {
  font-size: 0.75rem;
  color: var(--val-text-muted);
}

.puuid-box code {
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--val-cyan);
  word-break: break-all;
}

.error-title {
  color: #ef4444;
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 6px;
}

.error-msg {
  font-size: 0.85rem;
  color: var(--val-text-secondary);
}

.tagline-input-row {
  display: flex;
  gap: 8px;
}

.riot-verify-btn {
  white-space: nowrap;
  font-size: 0.8rem;
  padding: 8px 12px;
}

.riot-status-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
}

.status-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
}

/* Toast */
.tactical-toast {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  background: var(--val-dark-card);
  border: 1px solid var(--val-border);
  color: #fff;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
  clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
}

.toast-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--val-cyan);
}

.toast-success .toast-indicator { background: var(--val-cyan); }
.toast-error .toast-indicator { background: var(--val-red); }
.toast-info .toast-indicator { background: var(--val-gold); }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(-20px); }

/* Header */
.header {
  border-bottom: 1px solid var(--val-border);
  background: rgba(15, 25, 35, 0.85);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 18px;
  padding-bottom: 18px;
}

.brand {
  display: flex;
  flex-direction: column;
}

.brand-logo {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 2px;
}

.logo-slash {
  color: var(--val-red);
}

.logo-primary {
  color: var(--val-text-primary);
}

.logo-accent {
  color: var(--val-red);
  background: linear-gradient(135deg, #ff4655, #ff727f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 0.75rem;
  letter-spacing: 2px;
  color: var(--val-text-muted);
  font-weight: 600;
  font-family: var(--font-display);
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Hero Banner */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 28px;
  margin-bottom: 28px;
}

.stat-card {
  background: var(--val-dark-card);
  border: 1px solid var(--val-border);
  padding: 20px;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.2);
}

.stat-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
}

.stat-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--val-text-secondary);
  font-weight: 600;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 700;
  line-height: 1.1;
  margin: 4px 0;
  color: var(--val-text-primary);
}

.stat-sub {
  font-size: 0.75rem;
  color: var(--val-text-muted);
}

.stat-icon-bg {
  font-size: 2.5rem;
  opacity: 0.2;
}

.text-gold { color: var(--val-gold); }
.text-cyan { color: var(--val-cyan); }
.text-purple { color: #c084fc; }

/* Filter Section */
.filter-section {
  background: var(--val-dark-card);
  border: 1px solid var(--val-border);
  padding: 20px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  background: var(--val-dark);
  border: 1px solid var(--val-border);
  padding: 0 16px;
  position: relative;
}

.search-icon {
  font-size: 1rem;
  color: var(--val-text-muted);
  margin-right: 10px;
}

.search-input {
  width: 100%;
  background: transparent;
  border: none;
  padding: 12px 0;
  color: var(--val-text-primary);
  font-size: 0.95rem;
  outline: none;
}

.clear-search {
  background: none;
  border: none;
  color: var(--val-text-muted);
  cursor: pointer;
  padding: 4px 8px;
}

.filter-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.role-pill {
  background: var(--val-surface);
  border: 1px solid var(--val-border);
  color: var(--val-text-secondary);
  padding: 8px 16px;
  font-family: var(--font-display);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
}

.role-pill:hover {
  background: var(--val-surface-light);
  color: var(--val-text-primary);
}

.role-pill.active {
  background: var(--active-color, var(--val-red));
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 0 12px rgba(255, 70, 85, 0.4);
}

.filter-dropdowns {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.select-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-group label {
  font-size: 0.85rem;
  color: var(--val-text-secondary);
}

.tactical-select {
  background: var(--val-dark);
  border: 1px solid var(--val-border);
  color: var(--val-text-primary);
  padding: 8px 12px;
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
}

.tactical-select:focus {
  border-color: var(--val-red);
}

.btn-gold-active {
  background: var(--val-gold);
  color: #000;
  font-weight: 700;
  box-shadow: 0 0 12px rgba(255, 200, 59, 0.4);
}

.reset-btn {
  font-size: 0.8rem;
  padding: 8px 14px;
}

/* Roster Section */
.roster-section {
  margin-bottom: 60px;
}

.section-title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--val-text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-accent {
  color: var(--val-red);
}

.count-badge {
  font-size: 1rem;
  color: var(--val-text-muted);
  font-weight: 500;
}

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.mate-card {
  background: var(--val-dark-card);
  border: 1px solid var(--val-border);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.mate-card:hover {
  background: var(--val-dark-card-hover);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
}

.is-favorite-card {
  border-left: 3px solid var(--val-gold);
}

.is-favorite-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 32px;
  height: 32px;
  background: radial-gradient(circle at top right, rgba(255, 200, 59, 0.2), transparent 70%);
}

.mate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-badge {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  border: 1px solid;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(0, 0, 0, 0.2);
}

.favorite-star-btn {
  background: none;
  border: none;
  font-size: 1.4rem;
  color: var(--val-text-muted);
  cursor: pointer;
  transition: transform 0.2s ease, color 0.2s ease;
  line-height: 1;
}

.favorite-star-btn:hover {
  transform: scale(1.2);
  color: var(--val-gold);
}

.favorite-star-btn.active {
  color: var(--val-gold);
  text-shadow: 0 0 10px rgba(255, 200, 59, 0.6);
}

.mate-identity {
  display: flex;
  align-items: center;
  gap: 14px;
}

.agent-avatar {
  width: 48px;
  height: 48px;
  background: var(--val-surface);
  border: 2px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.1rem;
  color: #fff;
  clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 8px));
}

.identity-text {
  display: flex;
  flex-direction: column;
}

.riot-id {
  font-size: 1.35rem;
  font-weight: 700;
  display: flex;
  align-items: baseline;
  gap: 4px;
  color: #fff;
}

.riot-id .tag {
  font-size: 0.9rem;
  color: var(--val-text-muted);
}

.agent-name {
  font-size: 0.85rem;
  color: var(--val-text-secondary);
}

.agent-name strong {
  color: var(--val-cyan);
}

/* Badges */
.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.rank-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border: 1px solid;
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  background: rgba(0, 0, 0, 0.3);
}

.rank-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.rating-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 2px;
}

/* Stats Mini Bar */
.mate-stats-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  background: rgba(0, 0, 0, 0.25);
  padding: 8px 12px;
  border-left: 2px solid var(--val-border);
}

.stat-mini {
  display: flex;
  gap: 6px;
  font-size: 0.8rem;
}

.stat-mini .label {
  color: var(--val-text-muted);
}

.stat-mini .val {
  font-weight: 700;
  color: var(--val-text-primary);
}

.text-win-high {
  color: var(--val-cyan);
}

.winrate-bar-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 2px;
}

.winrate-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--val-red), var(--val-cyan));
  border-radius: 2px;
}

/* Tags */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-chip {
  background: var(--val-surface);
  color: var(--val-text-secondary);
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 2px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Notes & Discord */
.mate-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(15, 25, 35, 0.5);
  padding: 10px;
  border-left: 2px solid var(--val-border);
}

.mate-notes {
  font-size: 0.85rem;
  color: var(--val-text-primary);
  font-style: italic;
  line-height: 1.4;
}

.discord-contact {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #818cf8;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.mate-time {
  font-size: 0.75rem;
  color: var(--val-text-muted);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.card-action-btn {
  background: var(--val-surface);
  border: 1px solid var(--val-border);
  color: var(--val-text-secondary);
  padding: 4px 10px;
  font-size: 0.75rem;
  font-family: var(--font-display);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.card-action-btn:hover {
  background: var(--val-surface-light);
  color: #fff;
}

.delete-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
}

/* States */
.state-container, .empty-container {
  text-align: center;
  padding: 60px 20px;
  background: var(--val-dark-card);
  border: 1px solid var(--val-border);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.tactical-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 70, 85, 0.2);
  border-top-color: var(--val-red);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--val-dark-card);
  border: 1px solid var(--val-border-focus);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(255, 70, 85, 0.2);
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--val-border);
  padding-bottom: 14px;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--val-text-muted);
  cursor: pointer;
  padding: 4px 8px;
}

.close-modal-btn:hover {
  color: #fff;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-row.two-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--val-text-secondary);
}

.tactical-input, .tactical-textarea {
  background: var(--val-dark);
  border: 1px solid var(--val-border);
  color: var(--val-text-primary);
  padding: 10px 14px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.tactical-input:focus, .tactical-textarea:focus {
  border-color: var(--val-red);
}

.tactical-slider {
  accent-color: var(--val-red);
  margin-top: 10px;
}

.tags-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.tag-toggle-btn {
  background: var(--val-surface);
  border: 1px solid var(--val-border);
  color: var(--val-text-secondary);
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s ease;
}

.tag-toggle-btn:hover {
  background: var(--val-surface-light);
  color: #fff;
}

.tag-toggle-btn.active {
  background: var(--val-red);
  border-color: var(--val-red);
  color: #fff;
}

.custom-tag-row {
  display: flex;
  gap: 8px;
}

.custom-tag-input {
  flex: 1;
}

.checkbox-group {
  padding: 8px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 0.9rem;
}

.tactical-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--val-gold);
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
  border-top: 1px solid var(--val-border);
  padding-top: 18px;
}

/* Responsive */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  .form-row.two-cols {
    grid-template-columns: 1fr;
  }
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
