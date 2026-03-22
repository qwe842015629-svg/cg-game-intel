param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"

$utf8 = [System.Text.UTF8Encoding]::new($false)
$gbk = [System.Text.Encoding]::GetEncoding("GBK")
$cjkRegex = [regex]"[\u4e00-\u9fff]"
$cjkQuestionRegex = [regex]"[\u4e00-\u9fff]\?"

$target = Resolve-Path -Path $Root

$files = Get-ChildItem -Path $target -Recurse -File | Where-Object {
  $path = $_.FullName
  if ($path -match "\\node_modules\\") { return $false }
  if ($path -match "\\dist\\") { return $false }
  if ($path -match "\\.git\\") { return $false }
  if ($path -match "\\public\\characters\\") { return $false }
  if ($path -match "\\public\\data\\") { return $false }
  return $_.Extension -in @(".vue", ".ts", ".tsx", ".js", ".cjs", ".mjs", ".json", ".md")
}

$issues = @()

foreach ($file in $files) {
  $relative = $file.FullName.Substring($target.Path.Length).TrimStart('\', '/')
  $lines = [System.IO.File]::ReadAllLines($file.FullName, $utf8)

  for ($i = 0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]
    $lineNo = $i + 1

    # Heuristic 1:
    # If "GBK bytes -> UTF-8 text" creates readable CJK and differs from source,
    # source line is likely mojibake.
    $converted = [System.Text.Encoding]::UTF8.GetString($gbk.GetBytes($line))
    if ($converted -ne $line -and -not $converted.Contains([char]0xFFFD) -and $cjkRegex.IsMatch($converted)) {
      $issues += [PSCustomObject]@{
        Type = "reversible_mojibake"
        File = $relative
        Line = $lineNo
        Source = $line.Trim()
        Suggestion = $converted.Trim()
      }
      continue
    }

    # Heuristic 2:
    # Chinese text followed by ASCII '?' often indicates lost characters during encoding.
    if ($cjkQuestionRegex.IsMatch($line)) {
      $issues += [PSCustomObject]@{
        Type = "cjk_with_ascii_question"
        File = $relative
        Line = $lineNo
        Source = $line.Trim()
        Suggestion = ""
      }
    }
  }
}

if ($issues.Count -eq 0) {
  Write-Output "[check:mojibake] OK - no mojibake detected."
  exit 0
}

Write-Output "[check:mojibake] Found $($issues.Count) potential issues:"
foreach ($issue in $issues) {
  Write-Output "- [$($issue.Type)] $($issue.File):$($issue.Line)"
  Write-Output "  source: $($issue.Source)"
  if ($issue.Suggestion) {
    Write-Output "  suggest: $($issue.Suggestion)"
  }
}

exit 1
