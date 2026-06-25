# git-neko

CLI for syncing repositories from a specified GitHub user.

## Installation

### Via PyPI (Recommended)

#### With pip (Basic)

```sh
pip install git-neko
```

#### With pipx (Isolated)

```sh
pipx install git-neko
```

#### With uv (Best)

The most efficient way to install or run `git-neko`.

```sh
# Permanent isolated installation
uv tool install git-neko

# Run once without installing
uvx git-neko -u <github-username>

# Run in scripts or ad-hoc environments
uv run --with git-neko git-neko -u <github-username> -t <github-personal-access-token>
```

### From Source (Development)

```sh
# Clone the repository and navigate to it
git clone git@github.com:NecRaul/git-neko.git
cd git-neko

# Install environment and all development dependencies (mandatory and optional)
uv sync --dev

# Install pre-commit hook
uv run pre-commit install

# Optional: Run all linters and type checkers manually
uv run pre-commit run --all-files

# Run the local version
uv run git-neko -u <github-username> --git
```

## Usage

`git-neko` acts as a sync tool. If a repo folder doesn't exist, it clones it, if it does, it updates it.

```sh
# Sync public repositories with `requests`
git-neko -u <github-username>

# Sync public and private repositories with `requests` (using a personal access token)
git-neko -u <github-username> -t <github-personal-access-token>

# Use 'git clone/pull' instead of 'requests' (preserves history, branches and submodules)
git-neko -u <github-username> -g

# Use 'git' with a personal access token for private repository syncing
git-neko -u <github-username> -t <github-personal-access-token> --git

# Sync repositories to a specific directory
git-neko -u <github-username> -d /path/to/repos

# Include only repositories you own
git-neko -u <github-username> --access owner

# Include repositories you own and ones you have read access to
git-neko -u <github-username> --access owner accessible

# Include only public repositories
git-neko -u <github-username> --visibility public

# Exclude forked repositories
git-neko -u <github-username> --fork no

# Include only archived repositories
git-neko -u <github-username> --archived yes

# Exclude template repositories
git-neko -u <github-username> --template no

# Combine filters: own non-fork public repositories to a specific directory
git-neko -u <github-username> -d /path/to/repos --access owner --visibility public --fork no
```

### Options

```sh
-h, --help                             Display usage information and exit
-v, --version                          Show program version and exit

    --config          FILE             Load configuration from file
    --no-config                        Ignore configuration file
    --init-config     [FILE]           Create a default configuration file
    --show-config                      Show effective configuration and exit

-u, --username       USERNAME          GitHub username to fetch repositories from
-t, --token          TOKEN             GitHub personal access token for private repositories

-e, --environment                      Read username and token from environment variables
    --no-environment                   Do not read username and token from environment variables

-g, --git                              Download repositories using git instead of archive downloads
    --no-git                           Download repositories using archive downloads instead of git

    --access          ACCESS [...]     Access types to include:
                                       owner, collaborator, accessible,
                                       org-member, all

    --visibility      VIS [...]        Visibility levels to include:
                                       public, private, internal, all

    --fork            {yes,no,both}    Filter fork repositories
    --archived        {yes,no,both}    Filter archived repositories
    --template        {yes,no,both}    Filter template repositories
```

### Configuration

`git-neko` supports a JSON configuration file to set defaults for all options. You can create a default config, inspect the effective configuration, and override or ignore the config file at runtime.

- Default path
  - Linux/BSD: `$XDG_CONFIG_HOME/necraul/git-neko.json` or `~/.config/necraul/git-neko.json`
  - MacOS: `~/Library/Application Support/necraul/git-neko.json`
  - Windows: `%APPDATA%/necraul/git-neko.json`
- Basic structure
  - `github`: credentials and whether to read from environment variables.
  - `download`: target directory and git engine settings including extra args for `clone` and `pull`.
  - `filters`: control which repositories are included by access type, visibility, fork status, archive status, and template status.

```json
{
  "github": {
    "username": null,
    "token": null,
    "environment": false
  },
  "download": {
    "directory": ".",
    "git": {
      "enabled": true,
      "clone_args": ["--recursive"],
      "pull_args": ["--recurse-submodules"]
    }
  },
  "filters": {
    "access": ["owner"],
    "visibility": ["public", "private"],
    "fork": "both",
    "archived": "both",
    "template": "both"
  }
}
```

```sh
# Create a default configuration file at the default path
git-neko --init-config

# Create a default configuration file at a custom path
git-neko --init-config config.json

# Show the effective configuration (defaults merged with the config file)
git-neko --show-config

# Create a default configuration file at the default path and print it
git-neko --init-config --show-config

# Create a default configuration file at a custom path and print it
git-neko --init-config /path/to/config.json --show-config

# Show the effective configuration using a custom config file
git-neko --config config.json --show-config

# Use a custom configuration file
git-neko --config /path/to/config.json

# Ignore the configuration file and use only CLI flags
git-neko --no-config -u <github-username>

# Override config's directory at runtime
git-neko -d /path/to/repos
```

### Environment Variables

You can save your credentials to environment variables to avoid passing them manually in every command.

For persistence, add these exports to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`).

```sh
# Set your credentials as environment variables
export GITHUB_USERNAME="NecRaul"
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_necraul"
export GITHUB_REPOS_DIRECTORY="/path/to/repos"

# Run using the stored environment variables
git-neko --environment

# Run without using environment variables
git-neko --no-environment

# Run using the git engine
git-neko --git

# Run without using the git engine
git-neko --no-git

# Run using environment variables with the git engine
git-neko -e --git

# Run using environment variables without the git engine
git-neko -e --no-git

# Run without environment variables with the git engine
git-neko --no-environment --git

# Run without environment variables without the git engine
git-neko --no-environment --no-git

# Pass the GitHub username and personal access token environment variables directly within the command
GITHUB_USERNAME="NecRaul" GITHUB_PERSONAL_ACCESS_TOKEN="ghp_necraul" git-neko --environment

# Pass the directory environment variable directly within the command
GITHUB_REPOS_DIRECTORY="/path/to/repos" git-neko --environment
```

> [!TIP]
> `--environment` and `--git` enable a feature, while `--no-environment` and `--no-git` disable it.

## Dependencies

- [requests](https://github.com/psf/requests): fetch data from the GitHub API and handle downloads.

## How it works

The tool determines the appropriate GitHub API endpoint based on your input: it queries `https://api.github.com/users/{username}/repos` for public profiles or `https://api.github.com/user/repos` when a token is provided to include private data.

Once the repo list is retrieved, `git-neko` automates the synchronization process using one of two engines:

- Requests Engine (via `--no-git`): Fetches the repo as a compressed snapshot. This is fast but does not include **history**, **branches** or **submodules**.
- Git Engine (via `-g` or `--git` flag): Uses your local **git** installation to perform a full **clone** or **pull**. This preserves the complete **history**, **branches** and **submodules**.

### The Manual Way

Without this tool, you would need to manually parse JSON responses, manage authentication headers, and write logic to differentiate between new clones and existing updates:

```sh
# A simplified version of the logic git-neko automates
# It fetches the name and ssh_url, then loops through them
curl -s -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" https://api.github.com/user/repos |
    jq -r '.[] | "\(.name) \(.ssh_url)"' | while read -r name ssh_url; do
    if [ ! -d "$name" ]; then
        git clone --recursive "$ssh_url" "$name"
    else
        echo "Pulling '$name'..."
        git -C "$name" pull --recurse-submodules
    fi
done
```

### The git-neko way

- Dynamic API Routing: Automatically identifies the correct GitHub endpoint. It uses `/users/{username}/repos` for public browsing or the authenticated `/user/repos` for private access, ensuring you get the full list of repos you have permission to view.
- State-Aware Syncing: Instead of a simple download, it checks your local file system. If a repo already exists, it intelligently switches to an "update" mode (using `git pull` or overwriting via `requests`) to keep your local mirror current.
- Hybrid Engine Support:
  - Lightweight Mode: Uses `requests` to pull repo snapshots quickly without needing `git` installed or **SSH keys** configured.
  - Developer Mode (`--git`): Interfaces directly with your local `git` binary to handle **full history**, **branch tracking**, and **submodule recursion**.
- Repository Filtering: Supports fine-grained control over which repositories are synced, filtering by access level, visibility, fork status, archive status, and template status.
- Subprocess Management: Uses Python's `subprocess` module to provide a robust bridge between the GitHub API and your local shell, handling directory navigation and command execution automatically.
