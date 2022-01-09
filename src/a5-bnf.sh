set -o pipefail
set -o errexit
set -o nounset

bnf -s BDE -v -k 8 -e data/a4-output -c /dev/stderr 3>&2 2>&1 1>&3
