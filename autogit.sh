#!/bin/bash

# ===== AYAR =====
read -p "📁 Folder: " folder
read -p "🌐 GitHub Repo: " repo
read -p "💬 Commit: " msg

cd $folder || { echo "❌ Error Folder Not"; exit; }

echo "📦 Git Start..."
git init

echo "📁 File Add..."
git add .

echo "💾 Commit..."
git commit -m "$msg"

echo "🔗 Remote Add..."
git remote remove origin 2>/dev/null
git remote add origin $repo

echo "🚀 Push..."
git branch -M main
git push -u origin main

echo "✅ Final! GitHub Upload"
