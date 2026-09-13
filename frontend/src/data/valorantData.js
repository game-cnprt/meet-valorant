export const ROLES = [
  { id: 'Duelist', name: 'Duelist', viName: 'Đối Đầu', icon: '⚔️', color: '#ff4655', desc: 'Mở giao tranh và tìm kiếm mạng hạ gục đầu tiên' },
  { id: 'Initiator', name: 'Initiator', viName: 'Khởi Tranh', icon: '🎯', color: '#00f5d4', desc: 'Cung cấp thông tin và tạo lợi thế cho đồng đội chiếm khu vực' },
  { id: 'Controller', name: 'Controller', viName: 'Kiểm Soát', icon: '💨', color: '#818cf8', desc: 'Chắn tầm nhìn và làm chủ nhịp độ round đấu với làn khói' },
  { id: 'Sentinel', name: 'Sentinel', viName: 'Hộ Vệ', icon: '🛡️', color: '#f59e0b', desc: 'Khóa chặt khu vực đặt bom và bọc lót bảo vệ hậu phương' }
];

export const AGENTS_BY_ROLE = {
  Duelist: ['Jett', 'Reyna', 'Raze', 'Phoenix', 'Yoru', 'Neon', 'Iso'],
  Initiator: ['Sova', 'Breach', 'Skye', 'KAY/O', 'Fade', 'Gekko', 'Tejo'],
  Controller: ['Omen', 'Viper', 'Brimstone', 'Astra', 'Harbor', 'Clove'],
  Sentinel: ['Killjoy', 'Cypher', 'Sage', 'Chamber', 'Deadlock', 'Vyse']
};

export const ALL_AGENTS = Object.entries(AGENTS_BY_ROLE).flatMap(([role, agents]) =>
  agents.map(name => ({ name, role }))
);

export const RANKS = [
  { id: 'Radiant', name: 'Radiant', color: '#ffff76', bg: 'linear-gradient(135deg, #ffff76, #ff9f1c)' },
  { id: 'Immortal', name: 'Bất Tử (Immortal)', color: '#ff2a6d', bg: '#ff2a6d' },
  { id: 'Ascendant', name: 'Cao Thủ (Ascendant)', color: '#10b981', bg: '#10b981' },
  { id: 'Diamond', name: 'Kim Cương (Diamond)', color: '#c084fc', bg: '#c084fc' },
  { id: 'Platinum', name: 'Bạch Kim (Platinum)', color: '#38bdf8', bg: '#38bdf8' },
  { id: 'Gold', name: 'Vàng (Gold)', color: '#fbbf24', bg: '#fbbf24' },
  { id: 'Silver', name: 'Bạc (Silver)', color: '#cbd5e1', bg: '#cbd5e1' },
  { id: 'Bronze', name: 'Đồng (Bronze)', color: '#b45309', bg: '#b45309' },
  { id: 'Iron', name: 'Sắt (Iron)', color: '#64748b', bg: '#64748b' },
  { id: 'Unranked', name: 'Chưa Rank', color: '#475569', bg: '#475569' }
];

export const RATING_TYPES = {
  carry: { id: 'carry', label: 'Gánh Team', icon: '⭐', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' },
  duo_buddy: { id: 'duo_buddy', label: 'Hợp Cạ Duo', icon: '🔥', color: '#ff4655', bg: 'rgba(255, 70, 85, 0.15)' },
  good_comms: { id: 'good_comms', label: 'Callout Chuẩn', icon: '🗣️', color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.15)' },
  chill: { id: 'chill', label: 'Vui Vẻ / Chill', icon: '✨', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.15)' },
  avoid: { id: 'avoid', label: 'Né Gấp', icon: '⚠️', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)' }
};

export const COMMON_TAGS = [
  'Entry', 'Lurker', 'IGL', 'Lineup', 'OP God', 'Clutch God',
  'Aim To', 'Thân Thiện', 'Chịu Nghe Call', 'Aggressive Smoke',
  'Giữ Flank Tốt', 'No Mic', 'Dễ Tilt'
];
