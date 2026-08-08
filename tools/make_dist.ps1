# 生成一键上传包：dist/（仅网站运行文件）与 wechat-ecard-dist.zip
$src = "D:\AI\wechat-ecard"
$dist = Join-Path $src "dist"

if (-not (Test-Path $dist)) {
    New-Item -ItemType Directory -Force -Path $dist | Out-Null
}

Copy-Item (Join-Path $src "index.html") $dist -Force
Copy-Item (Join-Path $src "css") $dist -Recurse -Force
Copy-Item (Join-Path $src "js") $dist -Recurse -Force
Copy-Item (Join-Path $src "assets") $dist -Recurse -Force
Copy-Item (Join-Path $src ".nojekyll") $dist -Force -ErrorAction SilentlyContinue

$zip = Join-Path $src "wechat-ecard-dist.zip"
Compress-Archive -Path (Join-Path $dist "*") -DestinationPath $zip -Force

Get-ChildItem $dist -Recurse -File | Select-Object FullName, Length
Get-Item $zip | Select-Object FullName, Length
