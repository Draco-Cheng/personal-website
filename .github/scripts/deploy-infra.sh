#!/bin/bash
set -e

echo "=== Deploying infrastructure components ==="

HELM_ARGS="--set namespace.name=${K8S_NAMESPACE}"

# Set ingress host if provided
if [ -n "$INGRESS_HOST" ]; then
  HELM_ARGS="$HELM_ARGS --set ingress.host=${INGRESS_HOST}"
  echo "Ingress host: ${INGRESS_HOST}"
fi

# Deliberately NOT passing --namespace here. On a shared cluster where the
# live release's Helm bookkeeping is already tracked in "default", adding
# --namespace makes Helm treat this as a DIFFERENT release from the one
# already live (Helm keys a release by name + tracking namespace) — it then
# tries to re-install and collides with the live Namespace object's existing
# ownership annotations, breaking a working deploy (confirmed on
# yi-ying-orchids, see PR #184 there). Chart resources still land in the
# right namespace via .Values.namespace.name regardless of where the
# release itself is tracked. Do not re-add without first checking where
# THIS repo's live release is actually tracked (`helm list -A`).
helm upgrade --install infra-${K8S_NAMESPACE} helm \
  $HELM_ARGS \
  --create-namespace
echo "✓ Infrastructure deployed successfully"
