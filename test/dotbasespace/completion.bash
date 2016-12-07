_bs()
{
  local cur prev words
  IFS=$'\n'
  COMPREPLY=()
  _get_comp_words_by_ref -n : cur prev words

  # Command data:
  cmds=$'app\nappsession\nauth\nauthenticate\ncomplete\ncp\ncreate\nhelp\nhistory\nimport\nkill\nlaunch\nlist\nmount\nproject\nregister\nsample\nunmount\nunregister\nupload\nversion\nwhoami'
  cmds_app=$'import launch'
  cmds_app_import=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-i\n--appid\n-n\n--appname\n-p\n--properties-file\n-e\n--defaults-file\n-a\n--appsession-id\n-r\n--appversion\n-m\n--appsession-path\n-j\n--input-templates\n-f\n--force'
  cmds_app_launch=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-i\n--appid\n-a\n--agentid\n-b\n--batch-size\n-n\n--appname\n-o\n--option\n-s\n--sample-attributes\n--disable-consistency-checking'
  cmds_appsession=$'kill'
  cmds_appsession_kill=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse'
  cmds_auth=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n--api-server\n--api-version\n--force\n--scopes\n--client-id\n--client-secret'
  cmds_authenticate=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n--api-server\n--api-version\n--force\n--scopes\n--client-id\n--client-secret'
  cmds_complete=$'-h\n--help\n--name\n--shell'
  cmds_cp=$'-h\n--help'
  cmds_create=$'project'
  cmds_create_project=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse'
  cmds_help=$'-h\n--help'
  cmds_history=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n--json\n--domain'
  cmds_import=$'app'
  cmds_import_app=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-i\n--appid\n-n\n--appname\n-p\n--properties-file\n-e\n--defaults-file\n-a\n--appsession-id\n-r\n--appversion\n-m\n--appsession-path\n-j\n--input-templates\n-f\n--force'
  cmds_kill=$'appsession'
  cmds_kill_appsession=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse'
  cmds_launch=$'app'
  cmds_launch_app=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-i\n--appid\n-a\n--agentid\n-b\n--batch-size\n-n\n--appname\n-o\n--option\n-s\n--sample-attributes\n--disable-consistency-checking'
  cmds_mount=$'-h\n--help'
  cmds_project=$'create'
  cmds_project_create=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse'
  cmds_register=$'-h\n--help\n-p\n--path\n-d\n--description\n-g\n--group\n--force'
  cmds_sample=$'upload'
  cmds_sample_upload=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-p\n--project\n-i\n--sample-id\n-e\n--experiment\n--show-validation-rules'
  cmds_unmount=$'-h\n--help'
  cmds_unregister=$'-h\n--help\n-g\n--group'
  cmds_upload=$'sample'
  cmds_upload_sample=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-p\n--project\n-i\n--sample-id\n-e\n--experiment\n--show-validation-rules'
  cmds_version=$'-h\n--help'
  cmds_list=$'samples\nprojects\nappsessions\nappresults\napps'
  cmds_list_samples=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-f\n--format\n-C\n--column\n--max-width\n--noindent\n--quote\n--project-name'
  cmds_list_projects=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-f\n--format\n-C\n--column\n--max-width\n--noindent\n--quote\n--project-name'
  cmds_list_appsessions=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-f\n--format\n-C\n--column\n--max-width\n--noindent\n--quote\n--project-name'
  cmds_list_appresults=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-f\n--format\n-C\n--column\n--max-width\n--noindent\n--quote\n--project-name'
  cmds_list_apps=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-f\n--format\n-C\n--column\n--max-width\n--noindent\n--quote\n--project-name'
  cmds_whoami=$'-v\n--verbose\n--log-file\n-q\n--quiet\n-h\n--help\n--debug\n-V\n--version\n--dry-run\n-c\n--config\n--terse\n-f\n--format\n-C\n--column\n--max-width\n--noindent\n--quote'

  cmd=""
  words[0]=""
  completed="${cmds}"
  for var in "${words[@]:1}"
  do
    if [[ ${var} == -* ]] ; then
      break
    fi
    if [ -z "${cmd}" ] ; then
      proposed="${var}"
    else
      proposed="${cmd}_${var}"
    fi
    local i="cmds_${proposed}"
    local comp="${!i}"
    if [ -z "${comp}" ] ; then
      break
    fi
    if [[ ${comp} == -* ]] ; then
      if [[ ${cur} != -* ]] ; then
        completed=""
        break
      fi
    fi
    cmd="${proposed}"
    completed="${comp}"
  done

  if [ -z "${completed}" ] ; then
    COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )
  else
    COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )
  fi
  return 0
}
complete -o filenames -F _bs bs
