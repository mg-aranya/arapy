_netloom_complete() {
  local cur
  cur="${COMP_WORDS[COMP_CWORD]}"
  local cli
  cli="${COMP_WORDS[0]}"
  local backend

  backend="$(type -P -- "${cli}")"
  if [[ -z "${backend}" ]]; then
    backend="$(type -P -- netloom)"
  fi
  if [[ -z "${backend}" ]]; then
    COMPREPLY=()
    return 0
  fi

  local candidates
  candidates="$("${backend}" --_complete \
    --_cword="${COMP_CWORD}" \
    --_cur="${cur}" \
    "${COMP_WORDS[@]:1}" 2>/dev/null)"

  COMPREPLY=( $(compgen -W "${candidates}" -- "${cur}") )
  return 0
}

complete -F _netloom_complete netloom
