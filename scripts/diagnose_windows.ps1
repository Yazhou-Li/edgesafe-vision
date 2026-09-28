Write-Host "EdgeSafe Doctor - Windows"
Write-Host "========================"

function Show-Result($Status, $Text) {
    Write-Host ("{0,-5} {1}" -f $Status, $Text)
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    Show-Result "PASS" "python available"
} else {
    Show-Result "WARN" "python not found in PATH"
}

if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Show-Result "PASS" "ffmpeg available"
} else {
    Show-Result "WARN" "ffmpeg not found in PATH"
}

Get-PSDrive -PSProvider FileSystem |
Select-Object Name,
    @{Name="FreeGB";Expression={[math]::Round($_.Free / 1GB, 1)}},
    @{Name="UsedGB";Expression={[math]::Round($_.Used / 1GB, 1)}} |
Format-Table -AutoSize

Write-Host ""
Write-Host "This script is intentionally non-invasive."
Write-Host "Use edgesafe-doctor for endpoint checks."
