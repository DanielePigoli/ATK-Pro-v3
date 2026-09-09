#!/usr/bin/env bash
set -euo pipefail

tag="${1:?release tag is required}"
shift
if [ "$#" -eq 0 ]; then
  echo "At least one release asset is required." >&2
  exit 2
fi

repo="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
token="${GITHUB_TOKEN:?GITHUB_TOKEN is required}"

find_release() {
  gh api "repos/$repo/releases?per_page=100" \
    --jq ".[] | select(.tag_name == \"$tag\") | [.id, .draft] | @tsv" \
    | head -n 1
}

release_record="$(find_release)"
if [ -z "$release_record" ]; then
  if [[ "$tag" == *"rc"* ]]; then
    gh release create "$tag" --title "ATK-Pro $tag" --notes "" \
      --draft=false --prerelease 2>/dev/null || true
  else
    gh release create "$tag" --title "ATK-Pro $tag" --notes "" \
      --draft=false 2>/dev/null || true
  fi
  release_record="$(find_release)"
fi

if [ -z "$release_record" ]; then
  echo "Unable to resolve release for tag $tag." >&2
  exit 1
fi

IFS=$'\t' read -r release_id release_is_draft <<< "$release_record"
echo "Uploading assets to release $tag (id=$release_id, draft=$release_is_draft)."

content_type_for() {
  case "$1" in
    *.zip) printf '%s' 'application/zip' ;;
    *.tar.gz) printf '%s' 'application/gzip' ;;
    *.deb) printf '%s' 'application/vnd.debian.binary-package' ;;
    *.dmg) printf '%s' 'application/x-apple-diskimage' ;;
    *.exe) printf '%s' 'application/vnd.microsoft.portable-executable' ;;
    *.sha256) printf '%s' 'text/plain' ;;
    *) printf '%s' 'application/octet-stream' ;;
  esac
}

for asset_path in "$@"; do
  if [ ! -f "$asset_path" ]; then
    echo "Release asset not found: $asset_path" >&2
    exit 1
  fi

  asset_name="$(basename "$asset_path")"
  existing_id="$(
    gh api "repos/$repo/releases/$release_id/assets?per_page=100" \
      --jq ".[] | select(.name == \"$asset_name\") | .id" \
      | head -n 1
  )"
  if [ -n "$existing_id" ]; then
    gh api --method DELETE "repos/$repo/releases/assets/$existing_id" --silent
  fi

  curl --location --fail-with-body --retry 3 --retry-all-errors \
    --request POST \
    --header "Accept: application/vnd.github+json" \
    --header "Authorization: Bearer $token" \
    --header "X-GitHub-Api-Version: 2022-11-28" \
    --header "Content-Type: $(content_type_for "$asset_name")" \
    --upload-file "$asset_path" \
    "https://uploads.github.com/repos/$repo/releases/$release_id/assets?name=$asset_name"
done
