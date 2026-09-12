# Termux aliases — source from ~/.bashrc after ducky mobile hydration
#   source ~/zenOS/ducky/hydrate/mobile/termux-aliases.sh

alias zchat='zen chat'
alias zdoc='python ~/zenOS/ducky/env_doctor.py'
alias zduck='bash ~/zenOS/ducky/run.sh'
alias zwake='termux-wake-lock'

if command -v termux-wake-lock >/dev/null 2>&1; then
  termux-wake-lock || true
fi
