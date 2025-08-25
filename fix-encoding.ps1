# Save this as fix-encoding.ps1 and run it
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    try {
        # Read file content as UTF-8
        $content = Get-Content $_.FullName -Raw -Encoding UTF8
        # Write back as UTF-8 without BOM
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($_.FullName, $content, $utf8NoBom)
        Write-Host "Fixed encoding for: $($_.FullName)"
    } catch {
        Write-Host "Could not fix: $($_.FullName) - $($_.Exception.Message)"
    }
}