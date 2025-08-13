param($arg)

if ($arg -eq "a") {
    & ".\.venv\Scripts\Activate.ps1"
}
elseif ($arg -eq "d") {
    deactivate
}
else {
    Write-Host "Invalid option. Use 'a' to activate or 'd' to deactivate."
}
