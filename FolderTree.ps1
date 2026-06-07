$exclude = @("backup", "venv", "venv311", ".git")

# Set to $true if you want files displayed
$showFiles = $true

function Is-Excluded {
    param([System.IO.FileSystemInfo]$item)

    foreach ($ex in $exclude) {
        if ($item.Name -like $ex -or $item.FullName -like "*$ex*") {
            return $true
        }
    }
    return $false
}


function Show-FilteredTree {
    param (
        [string]$path,
        [int]$indent = 0,
        [switch]$ShowFiles
    )

    $items = Get-ChildItem -LiteralPath $path -Force -ErrorAction SilentlyContinue |
        Where-Object { -not (Is-Excluded $_) }

    foreach ($item in $items) {

        if ($item.PSIsContainer) {
            Write-Output (" " * $indent + "|-- " + $item.Name)
            Show-FilteredTree -path $item.FullName -indent ($indent + 4) -ShowFiles:$ShowFiles
        }
        elseif ($ShowFiles) {
            Write-Output (" " * $indent + "|-- " + $item.Name)
        }
    }
}

#Show-FilteredTree -path "E:\Projects\ai-summarizer" //folders only
#Show-FilteredTree -path "E:\Projects\ai-summarizer" -ShowFiles