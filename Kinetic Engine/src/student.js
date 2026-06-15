import { TILE_S, WORLD_W, WORLD_H, isWalkable, speedMult, T } from './engine.js'

// ── TASK 1 ───────────────────────────────────────────────────
export function createPlayer(startX, startY) {
  return {
    x: startX,
    y: startY,
    hp: 120,
    maxHp: 120,
    stamina: 100,
    maxStamina: 100,
    xp: 0,
    level: 1,
    gold: 0,
    potions: 3,
    kills: 0,
    state: 'idle',
    dir: 'down',
    facingDir: 'right',
    comboCount: 0,
    invincible: 0,
    attackCd: 0,
    dodgeCd: 0,
    score: 0,
  }
}

// ── TASK 2 ───────────────────────────────────────────────────
export function movePlayer(player, direction, tiles) {
  let newX = player.x
  let newY = player.y

  if (direction === 'up')    newY -= TILE_S
  if (direction === 'down')  newY += TILE_S
  if (direction === 'left')  newX -= TILE_S
  if (direction === 'right') newX += TILE_S

  const tx = Math.floor(newX / TILE_S)
  const ty = Math.floor(newY / TILE_S)

  if (tx < 0 || tx >= WORLD_W || ty < 0 || ty >= WORLD_H) return player
  if (!isWalkable(tiles[ty][tx])) return player

  const facingDir = direction === 'left' ? 'left' : 'right'
  return { ...player, x: newX, y: newY, dir: direction, facingDir, state: 'walking' }
}

// ── TASK 3 ───────────────────────────────────────────────────
export function getSpeedMultiplier(player, tiles) {
  const tx = Math.floor(player.x / TILE_S)
  const ty = Math.floor(player.y / TILE_S)
  if (tx < 0 || tx >= WORLD_W || ty < 0 || ty >= WORLD_H) return 1.0
  return speedMult(tiles[ty][tx])
}

// ── TASK 4 ───────────────────────────────────────────────────
export function collectItem(player, item) {
  if (item.type === 'coin') {
    return { player: { ...player, gold: player.gold + 10 }, message: '💰 +10 gold' }
  }
  if (item.type === 'potion') {
    return { player: { ...player, potions: player.potions + 1 }, message: '🧪 +1 potion' }
  }
  return { player, message: '' }
}

// ── TASK 5 ───────────────────────────────────────────────────
export function checkLevelUp(player) {
  const threshold = player.level * 150
  if (player.xp >= threshold) {
    return {
      player: {
        ...player,
        level: player.level + 1,
        xp: player.xp - threshold,
        maxHp: player.maxHp + 12,
        hp: player.maxHp + 12,
        maxStamina: player.maxStamina + 5,
        stamina: player.maxStamina + 5,
      },
      leveledUp: true,
    }
  }
  return { player, leveledUp: false }
}