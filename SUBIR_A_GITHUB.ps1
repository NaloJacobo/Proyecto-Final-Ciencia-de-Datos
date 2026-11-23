# Sube el proyecto a GitHub desde Windows (PowerShell 5.1 o posterior).
# Requiere internet. Si falta Git o GitHub CLI, intenta instalarlos con winget.
# El inicio de sesion de GitHub debe autorizarlo el propietario de la cuenta.

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

# Puedes cambiar este nombre si ya tienes un repositorio con el mismo nombre.
$nombreRepo = 'Proyecto-Final-Ciencia-de-Datos'
$visibilidad = '--public'  # Cambia por '--private' si lo deseas.
$nombreAutor = 'Jose Antonio Ortega Jacobo'

function Aviso($mensaje) { Write-Host "`n$mensaje" -ForegroundColor Cyan }
function Comprobar($mensaje) {
    if ($LASTEXITCODE -ne 0) { throw $mensaje }
}
function RecargarRuta {
    # Permite encontrar los programas que winget acaba de instalar.
    $maquina = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $usuario = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$maquina;$usuario;$env:Path"
}
function BuscarPrograma($nombre) {
    $cmd = Get-Command "$nombre.exe" -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cmd = Get-Command $nombre -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    if ($nombre -eq 'git') {
        $rutas = @(
            "${env:ProgramFiles}\Git\cmd\git.exe",
            "${env:LOCALAPPDATA}\Programs\Git\cmd\git.exe",
            "${env:ProgramFiles(x86)}\Git\cmd\git.exe"
        )
    } else {
        $rutas = @(
            "${env:ProgramFiles}\GitHub CLI\gh.exe",
            "${env:LOCALAPPDATA}\Programs\GitHub CLI\gh.exe",
            "${env:ProgramFiles(x86)}\GitHub CLI\gh.exe",
            "${env:LOCALAPPDATA}\Microsoft\WinGet\Links\gh.exe"
        )
    }
    foreach ($ruta in $rutas) {
        if ($ruta -and (Test-Path -LiteralPath $ruta -PathType Leaf)) {
            return $ruta
        }
    }
    return $null
}
function AsegurarPrograma($nombre, $paquete, $direccion) {
    $ruta = BuscarPrograma $nombre
    if ($ruta) { Write-Host "$nombre encontrado: $ruta" -ForegroundColor Green; return $ruta }

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "No se encontro winget. Instala $nombre desde $direccion y vuelve a ejecutar el archivo."
    }

    Aviso "Instalando $nombre automaticamente con winget..."
    & winget install --id $paquete --exact --source winget --accept-source-agreements --accept-package-agreements
    Comprobar "No se pudo instalar $nombre. Instala manualmente desde $direccion."
    RecargarRuta
    $ruta = BuscarPrograma $nombre
    if (-not $ruta) {
        throw "Se instalo $nombre, pero Windows aun no lo encuentra. Cierra la ventana y vuelve a ejecutar SUBIR_TODO.cmd."
    }
    Write-Host "$nombre listo." -ForegroundColor Green
    return $ruta
}

try {
    Aviso 'PROYECTO DE CIENCIA DE DATOS - SUBIDA AUTOMATICA A GITHUB'
    if (-not (Test-Path -LiteralPath './proyecto.py')) {
        throw 'No encuentro proyecto.py. Extrae TODO el ZIP y ejecuta el archivo dentro de la carpeta del proyecto.'
    }
    if (-not (Test-Path -LiteralPath './README.md')) {
        throw 'No encuentro README.md. Extrae TODO el ZIP antes de continuar.'
    }

    # 1. Encontrar o instalar herramientas.
    RecargarRuta
    $git = AsegurarPrograma 'git' 'Git.Git' 'https://git-scm.com/downloads'
    $gh = AsegurarPrograma 'gh' 'GitHub.cli' 'https://cli.github.com/'
    # GitHub CLI tambien necesita encontrar Git dentro de esta sesion.
    $env:Path = "$(Split-Path -Path $git -Parent);$(Split-Path -Path $gh -Parent);$env:Path"
    & $git --version
    Comprobar 'Git no se pudo iniciar.'
    & $gh --version
    Comprobar 'GitHub CLI no se pudo iniciar.'

    # 2. Autorizacion de la cuenta (solo si no se hizo anteriormente).
    Aviso 'Comprobando tu cuenta de GitHub...'
    & $gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Se abrira el navegador para iniciar sesion en GitHub.' -ForegroundColor Yellow
        & $gh auth login --hostname github.com --git-protocol https --web
        Comprobar 'No se completo el inicio de sesion en GitHub.'
    }
    & $gh auth setup-git
    Comprobar 'No se pudo configurar el acceso de Git con GitHub.'

    $usuario = ((& $gh api user --jq '.login') | Out-String).Trim()
    Comprobar 'No se pudo consultar el usuario de GitHub.'
    $idUsuario = ((& $gh api user --jq '.id') | Out-String).Trim()
    Comprobar 'No se pudo consultar el ID de GitHub.'
    if (-not $usuario -or $idUsuario -notmatch '^\d+$') {
        throw 'No pude comprobar el usuario de GitHub.'
    }
    $destino = "$usuario/$nombreRepo"
    $url = "https://github.com/$destino"
    Aviso "Cuenta: $usuario | Destino: $url"
    Write-Host 'El repositorio sera PUBLICO: tu nombre en el articulo sera visible.' -ForegroundColor Yellow
    Write-Host 'Puedes cambiar a privado editando $visibilidad dentro del script.'

    # 3. Crear repositorio Git local si aun no existe.
    if (-not (Test-Path -LiteralPath './.git')) {
        & $git init -b main
        Comprobar 'No se pudo iniciar el repositorio Git local.'
    }
    $rama = ((& $git branch --show-current) | Out-String).Trim()
    Comprobar 'No se pudo comprobar la rama Git.'
    if ($rama -and $rama -ne 'main') {
        throw "Esta carpeta ya usa la rama '$rama'. No la voy a cambiar automaticamente."
    }

    # 4. Configurar los commits sin mostrar tu correo personal.
    & $git config --local user.name $nombreAutor
    Comprobar 'No se pudo configurar el nombre de Git.'
    & $git config --local user.email "$idUsuario+$usuario@users.noreply.github.com"
    Comprobar 'No se pudo configurar el correo privado de Git.'

    # 5. Verificar si ya hay un repositorio remoto asociado.
    $remoto = ((& $git remote get-url origin 2>$null) | Out-String).Trim()
    $remotoExiste = ($LASTEXITCODE -eq 0 -and $remoto)
    if ($remotoExiste) {
        $https = "https://github.com/$destino.git"
        $ssh = "git@github.com:$destino.git"
        if ($remoto -notin @($https, $ssh, "https://github.com/$destino")) {
            throw "Esta carpeta ya esta conectada a otro repositorio: $remoto. No lo modificare."
        }
    } else {
        & $gh repo view $destino --json name --jq '.name' *> $null
        if ($LASTEXITCODE -eq 0) {
            throw "Ya existe $url y esta carpeta no esta conectada a ese repositorio. Cambia `$nombreRepo al principio del script."
        }
    }

    # 6. Guardar los archivos localmente.
    Aviso 'Preparando todos los archivos...'
    & $git add -A
    Comprobar 'No se pudieron agregar los archivos.'
    & $git diff --cached --quiet
    $hayCambios = ($LASTEXITCODE -eq 1)
    if ($LASTEXITCODE -gt 1) { throw 'Error comprobando los cambios de Git.' }
    if ($hayCambios) {
        & $git commit -m 'Entrega final de Ciencia de Datos'
        Comprobar 'No se pudo crear el commit.'
    } else {
        Write-Host 'No hay archivos nuevos que agregar.'
    }

    # 7. Publicar en GitHub.
    if ($remotoExiste) {
        Aviso 'Actualizando tu repositorio existente...'
        & $git push -u origin main
        Comprobar 'No se pudo actualizar el repositorio.'
    } else {
        Aviso 'Creando el repositorio y subiendo el proyecto...'
        & $gh repo create $destino $visibilidad --source . --remote origin --push
        Comprobar 'No se completo la publicacion. Revisa el mensaje de GitHub e intenta de nuevo.'
    }

    Aviso 'LISTO: EL PROYECTO SE PUBLICO EN GITHUB'
    Write-Host $url -ForegroundColor Green
    Write-Host 'Abriendo la pagina de tu repositorio...'
    Start-Process $url
} catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Tus archivos originales no se borraron.' -ForegroundColor Yellow
    exit 1
}
