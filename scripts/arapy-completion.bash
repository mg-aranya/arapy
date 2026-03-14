_netloom_complete() {
  local cur
  cur="${COMP_WORDS[COMP_CWORD]}"
  local cli
  cli="${COMP_WORDS[0]}"

  # Pass words after the invoked CLI name, plus cursor index and current token
  local candidates
  candidates="$("${cli}" --_complete \
    --_cword="${COMP_CWORD}" \
    --_cur="${cur}" \
    "${COMP_WORDS[@]:1}" 2>/dev/null)"

  COMPREPLY=( $(compgen -W "${candidates}" -- "${cur}") )
  return 0
}

complete -F _netloom_complete arapy
complete -F _netloom_complete netloom
