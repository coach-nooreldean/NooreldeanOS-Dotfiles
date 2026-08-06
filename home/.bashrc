#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '
fastfetch
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
export PATH="$HOME/.pub-cache/bin:$HOME/fvm/default/bin:$JAVA_HOME/bin:$PATH"
export CHROME_EXECUTABLE=/usr/bin/google-chrome-stable
alias autosubs='WEBKIT_DISABLE_DMABUF_RENDERER=1 autosubs'
export PATH="$HOME/.local/bin:$PATH"
export PATH=~/.npm-global/bin:$PATH

eval "$(starship init bash)"

export PATH="$PATH:$HOME/.spicetify"
