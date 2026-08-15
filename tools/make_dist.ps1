# 生成一键上传包：dist/（仅网站运行文件）与 wechat-ecard-dist.zip
$src = "D:\AI\wechat-ecard"
$stage = Join-Path $src "dist\_publish"

if (-not (Test-Path $stage)) {
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
}

Copy-Item (Join-Path $src "index.html") $stage -Force
Copy-Item (Join-Path $src "css") $stage -Recurse -Force
Copy-Item (Join-Path $src "js") $stage -Recurse -Force
$needAssets = @("cover.jpg", "inner.jpg", "music.mp3", "preview.png")
New-Item -ItemType Directory -Force -Path (Join-Path $stage "assets") | Out-Null
foreach ($a in $needAssets) {
    Copy-Item (Join-Path $src "assets\$a") (Join-Path $stage "assets\$a") -Force
}
Copy-Item (Join-Path $src ".nojekyll") $stage -Force -ErrorAction SilentlyContinue

$zip = Join-Path $src "wechat-ecard-dist.zip"
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force

Get-ChildItem $stage -Recurse -File | Select-Object FullName, Length
Get-Item $zip | Select-Object FullName, Length
