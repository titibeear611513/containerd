#!/bin/bash
# 修復 Next.js 建置快取問題

echo "🧹 清理 Next.js 建置快取..."

# 刪除 .next 目錄
if [ -d ".next" ]; then
  rm -rf .next
  echo "✅ 已刪除 .next 目錄"
else
  echo "ℹ️  .next 目錄不存在"
fi

# 可選：重新安裝依賴（如果需要）
# echo "📦 重新安裝依賴..."
# rm -rf node_modules
# npm install

echo "✨ 完成！請重新啟動開發服務器："
echo "   npm run dev"
