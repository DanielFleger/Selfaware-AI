# Resolve external helpers independently of the scripts' new folder depth.
$SelfawareWorkspace = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SelfawareVillageStudio = if ($env:SELFAWARE_VILLAGE_STUDIO_PATH) {
    $env:SELFAWARE_VILLAGE_STUDIO_PATH
} else {
    Join-Path $SelfawareWorkspace "..\VillageStudio"
}
