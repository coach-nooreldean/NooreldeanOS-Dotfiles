#
# ~/.bashrc - NooreldeanOS
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Show system info once per top-level interactive terminal session
if [[ -z "$BASHRC_LOADED" ]]; then
    export BASHRC_LOADED=1
    if command -v fastfetch &>/dev/null; then
        fastfetch
    fi
fi

# ==============================================================================
# Environment Variables & PATH
# ==============================================================================
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
export CHROME_EXECUTABLE=/usr/bin/google-chrome-stable
export EDITOR="nano"

# Add directories to PATH cleanly without duplicates
declare -a custom_paths=(
    "$HOME/.local/bin"
    "$HOME/.pub-cache/bin"
    "$HOME/fvm/default/bin"
    "$JAVA_HOME/bin"
    "$HOME/.npm-global/bin"
    "$HOME/.opencode/bin"
    "$HOME/.spicetify"
)

for p in "${custom_paths[@]}"; do
    if [[ -d "$p" ]] && [[ ":$PATH:" != *":$p:"* ]]; then
        PATH="$p:$PATH"
    fi
done
export PATH

# ==============================================================================
# Aliases & Shortcuts
# ==============================================================================
# Navigation & System
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias cls='clear'
alias reload='source ~/.bashrc && echo "⚡ ~/.bashrc reloaded!"'
alias ports='ss -tulpn'
alias df='df -h'
alias free='free -m'
alias clean="sys-clean"

# Core tools
alias ls='ls --color=auto'
alias ll='ls -lh --color=auto'
alias la='ls -lah --color=auto'
alias grep='grep --color=auto'
alias autosubs='WEBKIT_DISABLE_DMABUF_RENDERER=1 autosubs'

# Git Productivity
alias gs='git status -sb'
alias ga='git add'
alias gaa='git add -A'
alias gc='git commit -m'
alias gca='git commit --amend'
alias gp='git push'
alias gpl='git pull --rebase'
alias gco='git checkout'
alias gb='git branch'
alias gd='git diff'
alias gl='git log --graph --oneline --decorate -n 15'

# Flutter / Dart Productivity
alias fpg='flutter pub get'
alias fbr='flutter pub run build_runner build --delete-conflicting-outputs'
alias fbrw='flutter pub run build_runner watch --delete-conflicting-outputs'
alias fclean='flutter clean && flutter pub get'

# ==============================================================================
# CLI Integrations
# ==============================================================================
# Starship Prompt
if command -v starship &>/dev/null; then
    eval "$(starship init bash)"
else
    PS1='[\u@\h \W]\$ '
fi

# Zoxide: smart directory navigation ('z <dir>')
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init bash)"
fi

# FZF: fuzzy finder completion and keybindings (Ctrl+R history, Ctrl+T file)
if command -v fzf &>/dev/null; then
    eval "$(fzf --bash)"
fi
