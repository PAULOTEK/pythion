#!/bin/bash

PODNAME=${1}

PODS=$(kubectl get pods -o json | jq -r '.items[].metadata.name' | grep $PODNAME)


for pod in $PODS
do
    echo "Gerando log /tmp/$pod.log"
    #kubectl logs --since=30m $pod > /tmp/${pod}.log
    kubectl logs --tail=500 $pod > /tmp/${pod}.log
done