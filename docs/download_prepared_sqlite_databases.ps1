# Do not show the progress bar during download
$ProgressPreference = 'SilentlyContinue'

# Describe metadata for download operation
$sqlite_databases = "demo_continental_gateway", "demo_deham_cta", "demo_poc"
$web_root_directory = "https://media.tuhh.de/mls/software/conflowgen/docs/data/prepared_dbs/"
$local_prepared_db_root_directory = "./notebooks/data/prepared_dbs"

# Actually execute the download
foreach ($db in $sqlite_databases) {
    $source_url = "$($web_root_directory)$($db).sqlite"
    $target_path = "$($local_prepared_db_root_directory)/$($db).sqlite"
    Write-Output "Download $source_url and save it at $target_path"
    Invoke-WebRequest $source_url -OutFile $target_path
}
