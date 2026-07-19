#!/bin/bash
# phase4_vm.sh — headless scummvm-cht 截圖輔助（docker 內使用）
# 用法：source 此檔後用 start_vm / shot / press / vclick / stop_vm
# 截圖：ScummVM 內建 Alt+S → <outdir>/scummvm-samnmax-XXXXX.png

start_vm() {  # $1=outdir（截圖目錄）, 其餘=scummvm 額外參數
  local out="$1"; shift
  export DISPLAY=:99 SDL_AUDIODRIVER=dummy
  if ! xdpyinfo >/dev/null 2>&1; then
    Xvfb :99 -screen 0 1280x960x24 & XPID=$!
    sleep 1.5
  fi
  mkdir -p "$out"
  /work/bin/scummvm-cht -p /work/game-cht --auto-detect --language=cn \
      -e adlib --subtitles --screenshotpath="$out" "$@" \
      > "/work/logs/phase4-$(basename "$out").log" 2>&1 & VMPID=$!
  sleep 6
  WID=$(xdotool search --name 'Sam' 2>/dev/null | tail -1)
  [ -z "$WID" ] && WID=$(xdotool getactivewindow)
  xdotool windowactivate --sync "$WID" 2>/dev/null
  eval "$(xdotool getwindowgeometry --shell "$WID")"  # 得 X Y WIDTH HEIGHT
  echo "WID=$WID at $X,$Y ${WIDTH}x${HEIGHT}"
}

shot() {  # $1=等待秒數（先等再截）
  sleep "${1:-0}"
  xdotool key alt+s
  sleep 0.8
}

press() {  # $1=鍵名, $2=後續等待
  xdotool key "$1"
  sleep "${2:-0.5}"
}

vclick() {  # $1,$2 = 遊戲畫面 640x480 相對座標, $3=後續等待, $4=按鍵(預設左鍵)
  local sx=$(( X + WIDTH * $1 / 640 ))
  local sy=$(( Y + HEIGHT * $2 / 480 ))
  xdotool mousemove "$sx" "$sy" click "${4:-1}"
  sleep "${3:-1}"
}

vhover() {  # 只移動不點
  local sx=$(( X + WIDTH * $1 / 640 ))
  local sy=$(( Y + HEIGHT * $2 / 480 ))
  xdotool mousemove "$sx" "$sy"
  sleep "${3:-0.5}"
}

stop_vm() {
  kill "$VMPID" 2>/dev/null
  sleep 0.5
  [ -n "$XPID" ] && kill "$XPID" 2>/dev/null
  wait 2>/dev/null
}
